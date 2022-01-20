import json
import logging
import logging.config
import threading
import signal
from types import FunctionType
from typing import Dict, Deque
from collections import deque
from contextlib import contextmanager

import singleton_decorator


class ColoredFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    def __init__(self, fmt_str: str, *args, **kwargs):
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


class LoggingContextHandler:
    def __init__(self):
        self.attributes: Deque[Dict[str, str]] = deque([{}])

    def add(self, **new_context_vars) -> Dict[str, str]:
        old_context = self.attributes[0]
        new_context = {**old_context, **new_context_vars}
        self.attributes.appendleft(new_context)
        return new_context

    def get_ctx(self) -> Dict[str, str]:
        return {} if len(self.attributes) == 0 else self.attributes[0]

    def remove(self):
        self.attributes.popleft()


@singleton_decorator.singleton
class LogMng:

    def __init__(self):
        self.is_init: bool = False
        threading.get_ident()
        self._logging_ctx: Dict[int, LoggingContextHandler] = dict()
        self.enable_hot_config_reload()

    def enable_hot_config_reload(self):
        def hot_reload_method(signum, stack_frame):
            self.init_from_file()
        signal.signal(signal.SIGHUP, hot_reload_method)

    def get_context_handler(self) -> LoggingContextHandler:
        thread_id = threading.get_ident()
        ctx_handler = self._logging_ctx.get(thread_id)
        if ctx_handler is None:
            self._logging_ctx.update({thread_id: LoggingContextHandler()})
            ctx_handler = self._logging_ctx.get(thread_id)
        return ctx_handler

    def init_from_file(self, log_cfg: str = "log_cfg.json"):
        try:
            self._init_from_file_impl(log_cfg)
        except FileNotFoundError:
            logging.getLogger().error(f"Failed to configure logged_groups package, file not found: {log_cfg}")
        except json.JSONDecodeError as e:
            logging.getLogger().error(f"Failed decode logged_groups package from {log_cfg}, error: {e}")
        finally:
            self.is_init = True

    @staticmethod
    def _init_from_file_impl(log_cfg: str):
        with open(log_cfg) as log_cfg_file:
            log_cfg_data = json.load(log_cfg_file)
            logging.config.dictConfig(log_cfg_data)


@contextmanager
def logging_context(**kwargs):
    log_mng = LogMng()
    logging_ctx_handler = log_mng.get_context_handler()
    logging_ctx = logging_ctx_handler.add(**kwargs)
    try:
        yield logging_ctx
    finally:
        logging_ctx_handler.remove()


class ContextFilter(logging.Filter):
    def __init__(self):
        super(ContextFilter, self).__init__()

    def filter(self, record):
        log_mng: LogMng = LogMng()
        log_ctx_handler = log_mng.get_context_handler()
        log_ctx = log_ctx_handler.get_ctx()
        record.context = str(log_ctx)
        return True


def logged_group(logged_group: str):
    """Designed to provide methods: debug, info, warning, error and critical inside decorated class in logger_group"""
    log_mng = LogMng()
    if not log_mng.is_init:
        log_mng.init_from_file()

    logger = logging.getLogger(logged_group)

    def class_wrapper(original_class):
        orig_init = original_class.__init__

        def __init__(self, *args, **kws):
            self._class_id = kws.get("class_id", "")
            _logger = logging.LoggerAdapter(logger, {"class": original_class.__name__, "class_id": self._class_id})
            self.debug = _logger.debug
            self.info = _logger.info
            self.error = _logger.error
            self.critical = _logger.critical
            self.warning = _logger.warning

            orig_init(self, *args, **kws)

        original_class.__init__ = __init__
        return original_class

    def function_wrapper(original_function):
        _logger = logging.LoggerAdapter(logging.getLogger(logged_group),
                                        {"class": original_function.__name__, "class_id": ""})

        def inner_wrapper(*args, **kwargs):
            kwargs.update({"logger": _logger})
            return original_function(*args, **kwargs)

        return inner_wrapper

    def wrapper(entity):
        return function_wrapper(entity) if isinstance(entity, FunctionType) else class_wrapper(entity)

    return wrapper
