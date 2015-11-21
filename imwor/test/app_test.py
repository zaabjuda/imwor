# coding=utf-8
__author__ = "Dmitry Zhiltsov"
__copyright__ = "Copyright 2015, Dmitry Zhiltsov"

import logging
import os.path
import time

import tornado.escape
import tornado.gen
import tornado.ioloop
import tornado.web
from tornado.test.util import unittest
from tornado.testing import AsyncHTTPTestCase

from imwor import errors
from imwor.app import ImworApplication
from imwor.test import image_test

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib.parse import urlencode

try:
    import cv
except ImportError:
    cv = None

try:
    import pycurl
except ImportError:
    pycurl = None


logger = logging.getLogger("tornado.application")


class _AppAsyncMixin(object):
    def fetch_error(self, code, *args, **kwargs):
        response = self.fetch(*args, **kwargs)
        self.assertEqual(response.code, code)
        self.assertEqual(response.headers.get("Content-Type", None), "application/json")
        return tornado.escape.json_decode(response.body)

    def fetch_success(self, *args, **kwargs):
        response = self.fetch(*args, **kwargs)
        self.assertEqual(response.code, 200)
        return response

    def get_image_resize_cases(self):
        cases = image_test.get_image_resize_cases()
        m = dict(background="bg", filter="filter", format="fmt", optimize="opt", position="pos", progressive="prog",
                 quality="q", retain="retain")
        for i, case in enumerate(cases):
            path = "/test/data/{}".format(os.path.basename(case["source_path"]))
            cases[i]["source_query_params"] = dict(url=self.get_url(path), w=case["width"] or "",
                                                   h=case["height"] or "", mode=case["mode"])
            for k in list(m.keys()):
                if k in case:
                    cases[i]["source_query_params"][m.get(k)] = case[k]
            cases[i]["content_type"] = self._format_to_content_type(
                case.get("format"))
        return cases

    def get_image_rotate_cases(self):
        cases = image_test.get_image_rotate_cases()
        m = dict(expand="expand", format="fmt", optimize="opt", quality="q")
        for i, case in enumerate(cases):
            path = "/test/data/{}".format(os.path.basename(case["source_path"]))
            cases[i]["source_query_params"] = dict(op="rotate", url=self.get_url(path), deg=case["degree"])
            for k in list(m.keys()):
                if k in case:
                    cases[i]["source_query_params"][m.get(k)] = case[k]
            cases[i]["content_type"] = self._format_to_content_type(
                case.get("format"))
        return cases

    def get_image_region_cases(self):
        cases = image_test.get_image_region_cases()
        m = dict(expand="expand", format="fmt", optimize="opt", quality="q")
        for i, case in enumerate(cases):
            path = "/test/data/{}".format(os.path.basename(case["source_path"]))
            cases[i]["source_query_params"] = dict(op="region", url=self.get_url(path), rect=case["rect"])
            for k in list(m.keys()):
                if k in case:
                    cases[i]["source_query_params"][m.get(k)] = case[k]
            cases[i]["content_type"] = self._format_to_content_type(
                case.get("format"))
        return cases

    def get_image_chained_cases(self):
        cases = image_test.get_image_chained_cases()
        for i, case in enumerate(cases):
            path = "/test/data/{}".format(os.path.basename(case["source_path"]))
            cases[i]["source_query_params"] = dict(op=",".join(case["operation"]), url=self.get_url(path),
                                                   w=case["width"] or "", h=case["height"] or "",
                                                   deg=case.get("degree") or "", rect=case.get("rect") or "")
            cases[i]["content_type"] = self._format_to_content_type(
                case.get("format"))
        return cases

    def get_image_exif_cases(self):
        cases = image_test.get_image_exif_cases()
        m = dict(preserve_exif="exif")
        for i, case in enumerate(cases):
            path = "/test/data/{}".format(os.path.basename(case["source_path"]))
            cases[i]["source_query_params"] = dict(url=self.get_url(path), w=case["width"] or "",
                                                   h=case["height"] or "")
            for k in list(m.keys()):
                if k in case:
                    cases[i]["source_query_params"][m.get(k)] = case[k]
            cases[i]["content_type"] = self._format_to_content_type(
                case.get("format"))
        return cases

    def _format_to_content_type(self, fmt):
        if fmt in ["jpeg", "jpg"]:
            return "image/jpeg"
        elif fmt == "png":
            return "image/png"
        elif fmt == "webp":
            return "image/webp"
        elif fmt == "gif":
            return "image/gif"
        return None


class _ImworTestApplication(ImworApplication):
    def get_handlers(self):
        path = os.path.join(os.path.dirname(__file__), "data")
        handlers = [(r"/test/data/test-delayed.jpg", _DelayedHandler),
                    (r"/test/data/(.*)",
                     tornado.web.StaticFileHandler,
                     {"path": path})]
        handlers.extend(super(_ImworTestApplication, self).get_handlers())
        return handlers


class _DelayedHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        delay = time.time() + float(self.get_argument("delay", 0.0))
        yield tornado.gen.Task(
            tornado.ioloop.IOLoop.instance().add_timeout, delay)
        self.finish()


class AppTest(AsyncHTTPTestCase, _AppAsyncMixin):
    def get_app(self):
        return _ImworTestApplication(timeout=10.0)

    def test_missing_url(self):
        qs = urlencode(dict(w=1, h=1))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.UrlError.get_code())

    def test_invalid_operation(self):
        qs = urlencode(dict(url="http://foo.co/x.jpg", op="a"))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.OperationError.get_code())

    def test_missing_dimensions(self):
        qs = urlencode(dict(url="http://foo.co/x.jpg"))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.DimensionsError.get_code())

    def test_invalid_width(self):
        qs = urlencode(dict(url="http://foo.co/x.jpg", w="a", h=1))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.DimensionsError.get_code())

    def test_invalid_height(self):
        qs = urlencode(dict(url="http://foo.co/x.jpg", w=1, h="a"))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.DimensionsError.get_code())

    def test_invalid_degree(self):
        qs = urlencode(dict(url="http://foo.co/x.jpg", op="rotate", deg="a"))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.DegreeError.get_code())

    def test_invalid_rectangle(self):
        qs = urlencode(dict(url="http://foo.co/x.jpg", op="region", rect="a"))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.RectangleError.get_code())

    def test_invalid_mode(self):
        qs = urlencode(dict(url="http://foo.co/x.jpg", w=1, h=1, mode="foo"))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.ModeError.get_code())

    def test_invalid_hexadecimal_background(self):
        qs = urlencode(dict(url="http://foo.co/x.jpg", w=1, h=1, mode="fill", bg="r"))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.BackgroundError.get_code())

    def test_invalid_long_background(self):
        qs = urlencode(dict(url="http://foo.co/x.jpg", w=1, h=1, mode="fill", bg="0f0f0f0f0"))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.BackgroundError.get_code())

    def test_invalid_position(self):
        qs = urlencode(dict(url="http://foo.co/x.jpg", w=1, h=1, pos="foo"))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.PositionError.get_code())

    def test_invalid_position_ratio(self):
        qs = urlencode(dict(url="http://foo.co/x.jpg", w=1, h=1, pos="1.2,5.6"))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.PositionError.get_code())

    def test_invalid_filter(self):
        qs = urlencode(dict(url="http://foo.co/x.jpg", w=1, h=1, filter="bar"))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.FilterError.get_code())

    def test_invalid_format(self):
        qs = urlencode(dict(url="http://foo.co/x.jpg", w=1, h=1, fmt="foo"))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.FormatError.get_code())

    def test_invalid_optimize(self):
        qs = urlencode(dict(url="http://foo.co/x.jpg", w=1, h=1, opt="a"))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.OptimizeError.get_code())

    def test_invalid_integer_quality(self):
        qs = urlencode(dict(url="http://foo.co/x.jpg", w=1, h=1, q="a"))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.QualityError.get_code())

    def test_outofbounds_quality(self):
        qs = urlencode(dict(url="http://foo.co/x.jpg", w=1, h=1, q=200))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.QualityError.get_code())

    def test_nonimage_file(self):
        path = "/test/data/test-nonimage.txt"
        qs = urlencode(dict(url=self.get_url(path), w=1, h=1))
        resp = self.fetch_error(415, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.ImageFormatError.get_code())

    def test_unsupported_image_format(self):
        path = "/test/data/test-bad-format.ico"
        qs = urlencode(dict(url=self.get_url(path), w=1, h=1))
        resp = self.fetch_error(415, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.ImageFormatError.get_code())

    def test_retain_incorrect_format(self):
        url = self.get_url("/test/data/test-incorrect-format.png")
        qs = urlencode(dict(url=url, w=1, h=1))
        resp = self.fetch_success("/?{}".format(qs))
        self.assertEqual(resp.headers.get("Content-Type", None), "image/png")

    def test_not_found(self):
        path = "/test/data/test-not-found.jpg"
        qs = urlencode(dict(url=self.get_url(path), w=1, h=1))
        resp = self.fetch_error(404, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.FetchError.get_code())

    def test_invalid_protocol(self):
        path = os.path.join(os.path.dirname(__file__), "data", "test1.jpg")
        qs = urlencode(dict(url="file://{}".format(path), w=1, h=1))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.UrlError.get_code())

    def test_valid_noop(self):
        url = self.get_url("/test/data/test1.jpg")
        qs = urlencode(dict(url=url, op="noop"))
        resp = self.fetch_success("/?{}".format(qs))
        expected_path = os.path.join(os.path.dirname(__file__), "data", "test1.jpg")
        msg = "/?{} does not match {}".format(qs, expected_path)
        with open(expected_path, "rb") as expected:
            self.assertEqual(resp.buffer.read(), expected.read(), msg)

    def test_valid_resize(self):
        cases = self.get_image_resize_cases()
        for case in cases:
            if case.get("mode") == "crop" and case.get("position") == "face":
                continue
            self._assert_expected_case(case)

    def test_valid_rotate(self):
        cases = self.get_image_rotate_cases()
        for case in cases:
            self._assert_expected_case(case)

    def test_valid_region(self):
        cases = self.get_image_region_cases()
        for case in cases:
            self._assert_expected_case(case)

    def test_valid_chained(self):
        cases = self.get_image_chained_cases()
        for case in cases:
            self._assert_expected_case(case)

    def test_valid_exif(self):
        cases = self.get_image_exif_cases()
        for case in cases:
            self._assert_expected_case(case)

    @unittest.skipIf(cv is None, "OpenCV is not installed")
    def test_valid_face(self):
        cases = self.get_image_resize_cases()
        for case in cases:
            if case.get("mode") == "crop" and case.get("position") == "face":
                self._assert_expected_case(case)

    def _assert_expected_case(self, case):
        qs = urlencode(case["source_query_params"])
        resp = self.fetch_success("/?{}".format(qs))
        msg = "/?{} does not match {}".format(qs, case["expected_path"])
        if case["content_type"]:
            self.assertEqual(resp.headers.get("Content-Type", None), case["content_type"])
        with open(case["expected_path"], "rb") as expected:
            self.assertEqual(resp.buffer.read(), expected.read(), msg)


class AppImplicitBaseUrlTest(AsyncHTTPTestCase, _AppAsyncMixin):
    def get_app(self):
        return _ImworTestApplication(
            implicit_base_url=self.get_url("/"))

    def test_missing_url(self):
        qs = urlencode(dict(w=1, h=1))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.UrlError.get_code())

    def test_url(self):
        url = self.get_url("/test/data/test1.jpg")
        qs = urlencode(dict(url=url, op="noop"))
        resp = self.fetch_success("/?{}".format(qs))
        expected_path = os.path.join(os.path.dirname(__file__), "data", "test1.jpg")
        msg = "/?{} does not match {}".format(qs, expected_path)
        with open(expected_path, "rb") as expected:
            self.assertEqual(resp.buffer.read(), expected.read(), msg)

    def test_path(self):
        url_path = "/test/data/test1.jpg"
        qs = urlencode(dict(url=url_path, op="noop"))
        resp = self.fetch_success("/?{}".format(qs))
        expected_path = os.path.join(os.path.dirname(__file__), "data", "test1.jpg")
        msg = "/?{} does not match {}".format(qs, expected_path)
        with open(expected_path, "rb") as expected:
            self.assertEqual(resp.buffer.read(), expected.read(), msg)

    def test_invalid_protocol(self):
        path = os.path.join(os.path.dirname(__file__), "data", "test1.jpg")
        qs = urlencode(dict(url="file://{}".format(path), w=1, h=1))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.UrlError.get_code())


class AppAllowedOperationsTest(AsyncHTTPTestCase, _AppAsyncMixin):
    def get_app(self):
        return _ImworTestApplication(allowed_operations=['noop'])

    def test_invalid_operation(self):
        qs = urlencode(dict(url="http://foo.co/x.jpg", op="resize"))
        resp = self.fetch_error(400, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.OperationError.get_code())

    def test_valid_noop(self):
        url = self.get_url("/test/data/test1.jpg")
        qs = urlencode(dict(url=url, op="noop"))
        resp = self.fetch_success("/?{}".format(qs))
        expected_path = os.path.join(os.path.dirname(__file__), "data", "test1.jpg")
        msg = "/?{} does not match {}".format(qs, expected_path)
        with open(expected_path, "rb") as expected:
            self.assertEqual(resp.buffer.read(), expected.read(), msg)


class AppDefaultOperationTest(AsyncHTTPTestCase, _AppAsyncMixin):
    def get_app(self):
        return _ImworTestApplication(operation='noop')

    def test_valid_default_operation(self):
        url = self.get_url("/test/data/test1.jpg")
        qs = urlencode(dict(url=url))
        resp = self.fetch_success("/?{}".format(qs))
        expected_path = os.path.join(os.path.dirname(__file__), "data", "test1.jpg")
        msg = "/?{} does not match {}".format(qs, expected_path)
        with open(expected_path, "rb") as expected:
            self.assertEqual(resp.buffer.read(), expected.read(), msg)


class AppOverrideContentTypeTest(AsyncHTTPTestCase, _AppAsyncMixin):
    def get_app(self):
        return _ImworTestApplication(content_type_from_image=True)

    def test_override_unknown_format(self):
        url = self.get_url("/test/data/test-unknown-format")
        qs = urlencode(dict(url=url, w=1, h=1))
        resp = self.fetch_success("/?{}".format(qs))
        self.assertEqual(resp.headers.get("Content-Type", None), "image/jpeg")

    def test_override_incorrect_format(self):
        url = self.get_url("/test/data/test-incorrect-format.png")
        qs = urlencode(dict(url=url, w=1, h=1))
        resp = self.fetch_success("/?{}".format(qs))
        self.assertEqual(resp.headers.get("Content-Type", None), "image/jpeg")


class AppSlowTest(AsyncHTTPTestCase, _AppAsyncMixin):
    def get_app(self):
        return _ImworTestApplication(timeout=0.5)

    def test_timeout(self):
        url = self.get_url("/test/data/test-delayed.jpg?delay=1.0")
        qs = urlencode(dict(url=url, w=1, h=1))
        resp = self.fetch_error(404, "/?{}".format(qs))
        self.assertEqual(resp.get("error_code"), errors.FetchError.get_code())
