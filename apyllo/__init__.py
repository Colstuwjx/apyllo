# coding=utf-8

import logging
from logging.handlers import RotatingFileHandler
from .constance import DEFAULT_ROTATE_FILE_PATH, DEFAULT_ROTATE_SIZE, DEFAULT_ROTATE_COUNT
from .apyllo import Apyllo


__author__ = 'colstuwjx@gmail.com'
__version__ = '0.1.0'


def set_logger(
    name='apyllo',
    level=logging.DEBUG,
    format_string=None,
    output_to_console=False,
    output_to_file=True,
    rotate_file_path=DEFAULT_ROTATE_FILE_PATH,
    max_bytes=DEFAULT_ROTATE_SIZE,
    backup_count=DEFAULT_ROTATE_COUNT,
):
    if format_string is None:
        format_string = "[%(asctime)s.%(msecs)03d+08] %(levelname)s: %(message)s"

    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(format_string, "%Y-%m-%dT%H:%M:%S")

    # Define a Handler and set a format which output to console
    if output_to_console is True:
        console = logging.StreamHandler()
        console.setLevel(level)
        console.setFormatter(formatter)

        logger.addHandler(console)

    # Define a Handler and set a format which output to rotated file
    if output_to_file is True:
        rotate_file = RotatingFileHandler(
            rotate_file_path,
            maxBytes=DEFAULT_ROTATE_SIZE,
            backupCount=DEFAULT_ROTATE_COUNT
        )
        rotate_file.setLevel(level)
        rotate_file.setFormatter(formatter)

        logger.addHandler(rotate_file)


# Set up logging to ``/dev/null`` like a library is supposed to.
# http://docs.python.org/3.3/howto/logging.html#configuring-logging-for-a-library
class NullHandler(logging.Handler):
    def emit(self, record):
        pass


logging.getLogger('apyllo').addHandler(NullHandler())


DEFAULT_CLIENT = None


def client(*args, **kwargs):
    global DEFAULT_CLIENT
    DEFAULT_CLIENT = Apyllo(*args, **kwargs)
    return DEFAULT_CLIENT


def get_client():
    return DEFAULT_CLIENT
