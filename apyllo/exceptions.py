# coding=utf-8


class BadRequestError(Exception):
    """
    Exception found before request
    """
    def __init__(self, error_msg):
        self.message = "Bad request: {}.".format(error_msg)

    def __str__(self):
        return self.message


class RequestError(Exception):
    """
    Exception found on request
    """
    def __init__(self, server):
        self.message = "Request failed to {}.".format(server)

    def __str__(self):
        return self.message


class InvalidResponseError(Exception):
    """
    Exception found on response
    """
    def __init__(self, server, error_msg):
        self.message = \
            "Got unexpect response from {server}, msg: {error_msg}".format(
                server, error_msg
            )

    def __str__(self):
        return self.message


class Request4xx5xxError(Exception):
    """
    Exception found on response
    """
    def __init__(self, server, error_msg):
        self.message = "Error call host: {server}, msg: {error_msg}".format(
            server=server, error_msg=error_msg
        )

    def __str__(self):
        return self.message


class AuthError(Exception):
    """
    Exception found on auth
    """
    def __init__(self, server, error_msg):
        self.message = "Auth err with host: {server}, msg: {error_msg}".format(
            server=server, error_msg=error_msg
        )

    def __str__(self):
        return self.message


class NotImplementError(Exception):
    """
    Exception found while the features are not implemented yet
    """
    def __init__(self, component):
        self.message = "{component} is NOT implement yet".format(
            component=component
        )

    def __str__(self):
        return self.message
