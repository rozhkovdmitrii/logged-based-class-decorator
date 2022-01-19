import json
import logging
import logging.config
from types import FunctionType

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


@singleton_decorator.singleton
class LogMng:

    def __init__(self):
        self.is_init: bool = False

    def init_from_file(self, log_cfg: str = "log_cfg.json"):
        try:
            self._init_from_file_impl(log_cfg)
        except FileNotFoundError:
            logging.getLogger().error(f"Failed to configure logged_groups package, file not found: {log_cfg}")
        except json.JSONDecodeError as e:
            logging.getLogger().error(f"Failed decode logged_groups package from {log_cfg}, error: {e}")

    def _init_from_file_impl(self, log_cfg: str):
        with open(log_cfg) as log_cfg_file:
            log_cfg_data = json.load(log_cfg_file)
            logging.config.dictConfig(log_cfg_data)
        self.is_init = True


def logged_group(logged_group: str):
    """Designed to provide methods: debug, info, warning, error and critical inside decorated class in logger_group"""
    log_mng = LogMng()
    if not log_mng.is_init:
        log_mng.init_from_file()

    logger = logging.getLogger(logged_group)
    if len(logger.handlers) == 0:
        logger.setLevel(logging.CRITICAL)

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
