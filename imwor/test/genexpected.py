# coding=utf-8
__author__ = "Dmitry Zhiltsov"
__copyright__ = "Copyright 2015, Dmitry Zhiltsov"

import logging
from imwor.test import image_test
from imwor.image import Image

logging.basicConfig()


def main():
    """Generates expected results"""
    cases = image_test.get_image_resize_cases()
    for case in cases:
        with open(case["source_path"], "rb") as f:
            print("Generating {}".format(case["expected_path"]))
            try:
                img = Image(f).resize(case["width"], case["height"], mode=case["mode"],
                                      background=case.get("background"), filter=case.get("filter"),
                                      position=case.get("position"), retain=case.get("retain"))
            except NotImplementedError as exc:
                continue
            rv = img.save(format=case.get("format"), optimize=case.get("optimize"), progressive=case.get("progressive"),
                          quality=case.get("quality"))
            with open(case["expected_path"], "wb") as expected:
                expected.write(rv.read())
    cases = image_test.get_image_rotate_cases()
    for case in cases:
        with open(case["source_path"], "rb") as f:
            print("Generating {}".format(case["expected_path"]))
            img = Image(f).rotate(case["degree"], expand=case.get("expand"), filter=case.get("filter"))
            rv = img.save(format=case.get("format"), optimize=case.get("optimize"), progressive=case.get("progressive"),
                          quality=case.get("quality"))
            with open(case["expected_path"], "wb") as expected:
                expected.write(rv.read())
    cases = image_test.get_image_region_cases()
    for case in cases:
        with open(case["source_path"], "rb") as f:
            print("Generating {}".format(case["expected_path"]))
            img = Image(f).region(case["rect"].split(","))
            rv = img.save(format=case.get("format"), optimize=case.get("optimize"), progressive=case.get("progressive"),
                          quality=case.get("quality"))
            with open(case["expected_path"], "wb") as expected:
                expected.write(rv.read())
    cases = image_test.get_image_chained_cases()
    for case in cases:
        with open(case["source_path"], "rb") as f:
            print("Generating {}".format(case["expected_path"]))
            img = Image(f)
            for operation in case["operation"]:
                if operation == "resize":
                    img.resize(case["width"], case["height"])
                elif operation == "rotate":
                    img.rotate(case["degree"])
                elif operation == "region":
                    img.region(case["rect"].split(","))
            rv = img.save()
            with open(case["expected_path"], "wb") as expected:
                expected.write(rv.read())
    cases = image_test.get_image_exif_cases()
    for case in cases:
        with open(case["source_path"], "rb") as f:
            print("Generating {}".format(case["expected_path"]))
            img = Image(f).resize(case["width"], case["height"])
            rv = img.save(preserve_exif=case['preserve_exif'])
            with open(case["expected_path"], "wb") as expected:
                expected.write(rv.read())


if __name__ == "__main__":
    main()
