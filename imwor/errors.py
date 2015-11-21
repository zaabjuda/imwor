# coding=utf-8
__author__ = "Dmitry Zhiltsov"
__copyright__ = "Copyright 2015, Dmitry Zhiltsov"

import tornado.web


class ImworError(tornado.web.HTTPError):
    @staticmethod
    def get_code():
        raise NotImplementedError()


class BadRequestError(ImworError):
    def __init__(self, msg=None, *args, **kwargs):
        super(BadRequestError, self).__init__(400, msg, *args, **kwargs)


class BackgroundError(BadRequestError):
    @staticmethod
    def get_code():
        return 1


class DimensionsError(BadRequestError):
    @staticmethod
    def get_code():
        return 2


class FilterError(BadRequestError):
    @staticmethod
    def get_code():
        return 3


class FormatError(BadRequestError):
    @staticmethod
    def get_code():
        return 4


class ModeError(BadRequestError):
    @staticmethod
    def get_code():
        return 5


class PositionError(BadRequestError):
    @staticmethod
    def get_code():
        return 6


class QualityError(BadRequestError):
    @staticmethod
    def get_code():
        return 7


class UrlError(BadRequestError):
    @staticmethod
    def get_code():
        return 8


class DegreeError(BadRequestError):
    @staticmethod
    def get_code():
        return 9


class OperationError(BadRequestError):
    @staticmethod
    def get_code():
        return 10


class RectangleError(BadRequestError):
    @staticmethod
    def get_code():
        return 11


class OptimizeError(BadRequestError):
    @staticmethod
    def get_code():
        return 12


class PreserveExifError(BadRequestError):
    @staticmethod
    def get_code():
        return 15


class ProgressiveError(BadRequestError):
    @staticmethod
    def get_code():
        return 13


class RetainError(BadRequestError):
    @staticmethod
    def get_code():
        return 14


class FetchError(ImworError):
    def __init__(self, msg=None, *args, **kwargs):
        super(FetchError, self).__init__(404, msg, *args, **kwargs)

    @staticmethod
    def get_code():
        return 301


class ForbiddenError(ImworError):
    def __init__(self, msg=None, *args, **kwargs):
        super(ForbiddenError, self).__init__(403, msg, *args, **kwargs)


class SignatureError(ForbiddenError):
    @staticmethod
    def get_code():
        return 101


class ClientError(ForbiddenError):
    @staticmethod
    def get_code():
        return 102


class HostError(ForbiddenError):
    @staticmethod
    def get_code():
        return 103


class UnsupportedError(ImworError):
    def __init__(self, msg=None, *args, **kwargs):
        super(UnsupportedError, self).__init__(415, msg, *args, **kwargs)


class ImageFormatError(UnsupportedError):
    @staticmethod
    def get_code():
        return 201


class ImageSaveError(UnsupportedError):
    @staticmethod
    def get_code():
        return 202
