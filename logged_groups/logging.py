import json
from dataclasses import dataclass, field
import logging
import sys
from typing import NoReturn, Dict, Any
from types import FunctionType

import singleton_decorator


@dataclass
class LogConfig:
    groups: Dict[str, int] = field(default_factory=dict)
    format: str = "%(asctime)23s %(levelname)8s %(process)6d:%(threadName)-10s %(class)15s:%(class_id)-8s %(message)s"
    colored: bool = False
    propagate: bool = False


class _ColoredFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    def __init__(self, fmt_str: str):
        super().__init__()
        green = "\x1b[32m"
        grey = "\x1b[38m"
        yellow = "\x1b[33m"
        red = "\x1b[31m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"
        logged_fmt = fmt_str
        self.FORMATS = {
            logging.DEBUG: grey + logged_fmt + reset,
            logging.INFO: green + logged_fmt + reset,
            logging.WARNING: yellow + logged_fmt + reset,
            logging.ERROR: red + logged_fmt + reset,
            logging.CRITICAL: bold_red + logged_fmt + reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


@singleton_decorator.singleton
class LogMng:

    def __init__(self):
        self.log_cfg = LogConfig()
        self.is_init: bool = False

    def init_from_file(self, log_cfg: str = "log_cfg.json"):
        self._init_from_file_impl(log_cfg)
        self.init_logged_groups()

    def _init_from_file_impl(self, log_cfg: str):
        with open(log_cfg) as cfg_opened:
            cfg: Dict[str, Any] = json.load(cfg_opened)

            fmt_str: str = cfg.get("format")
            if fmt_str is not None:
                self.log_cfg.format = fmt_str

            groups: Dict[str, Any] = cfg.get("logged_groups")
            levels = {"DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR,
                      "CRITICAL": logging.CRITICAL, }
            for group, level in groups.items():
                self.log_cfg.groups[group] = levels[level]

            self.log_cfg.propagate = cfg.get("propagate", False)
            self.log_cfg.colored = cfg.get("colored", False)

        self.is_init = True

    def init_logged_groups(self) -> NoReturn:
        for logged_group, log_level in self.log_cfg.groups.items():
            self._init_logger(logged_group, log_level)

    def _init_logger(self, logged_group, log_level):
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        fmt_str = self.log_cfg.format
        formatter = _ColoredFormatter(fmt_str) if self.log_cfg.colored else logging.Formatter(fmt=fmt_str)
        handler.setFormatter(formatter)
        logger = logging.getLogger(logged_group)
        logger.setLevel(log_level)
        logger.addHandler(handler)
        logger.propagate = self.log_cfg.propagate


def logged_group(logged_group: str):
    """Designed to provide methods: debug, info, warning, error and critical inside decorated class in logger_group"""
    log_mng = LogMng()
    if not log_mng.is_init:
        log_mng.init_from_file()

    if logged_group not in log_mng.log_cfg.groups:
        logger = logging.getLogger(logged_group)
        logger.setLevel(logging.CRITICAL)

    def class_wrapper(original_class):
        orig_init = original_class.__init__

        def __init__(self, *args, **kws):
            self._class_id = kws.get("class_id", "")
            logger = logging.LoggerAdapter(logging.getLogger(logged_group),
                                           {"class": original_class.__name__, "class_id": self._class_id})
            self.debug = logger.debug
            self.info = logger.info
            self.error = logger.error
            self.critical = logger.critical
            self.warning = logger.warning

            orig_init(self, *args, **kws)

        original_class.__init__ = __init__
        return original_class

    def function_wrapper(original_function):
        logger = logging.LoggerAdapter(logging.getLogger(logged_group),
                                       {"class": original_function.__name__, "class_id": ""})

        def inner_wrapper(*args, **kwargs):
            kwargs.update({"logger": logger})
            return original_function(*args, **kwargs)

        return inner_wrapper

    def wrapper(entity):
        return function_wrapper(entity) if isinstance(entity, FunctionType) else class_wrapper(entity)

    return wrapper
