# from __future__ import annotations
# Above is temporarily commented to ensure compatibility with Python <= 3.6
# Versions 3.6 and below do not support postponed evaluation

import logging
from typing import Optional, Any
from Pythagoras import NeatStr

# Workaround to ensure compatibility with Python <= 3.6
# Versions 3.6 and below do not support postponed evaluation
class LoggableObject:
    pass

class LoggableObject:
    """ Base class for types that are able to log events/messages.

    A wrapper for standard Python logging functionality,
    extended with an ability to automatically
    append logger's name with information
    about an object that generated a message.
    """

    parent_logger_name: str
    reveal_identity: bool
    selflog_prefix: str = "__selflog__: "
    logging_level: Optional[int] = None

    def __init__(self
             , parent_logger_name: str = "Pythagoras"
             , reveal_loggers_identity: bool = True
             , new_logging_handler: logging.Handler = None
             , new_logging_level: Optional[int] = None
             , new_logging_formatter: logging.Formatter = None
             ) -> None:
        assert len(parent_logger_name), "parent_logger_name can not be empty"
        self.parent_logger_name = parent_logger_name
        self.reveal_identity = reveal_loggers_identity
        self.update_parent_logger(
            new_logging_level, new_logging_handler, new_logging_formatter)

    @property
    def logger(self):
        logger_name = self.parent_logger_name
        if self.reveal_identity:
            logger_name += "." + type(self).__qualname__
            self_names = NeatStr.object_names(self)
            if len(self_names):
                logger_name += "." + self_names
        return logging.getLogger(logger_name)

    def __str__(self) -> str:
        description = f"Parent logger name is '{self.parent_logger_name}'; "
        if self.reveal_identity:
            description += "object REVEALS self-identity while logging. "
        else:
            description += (
                "object DOES NOT reveal self-identity while logging. ")
        return description

    def update_parent_logger(self
            , new_logging_level: int = logging.DEBUG
            , new_logging_handler: logging.Handler = logging.StreamHandler()
            , new_logging_formatter: logging.Formatter = logging.Formatter(
                '%(asctime)s %(name)s %(levelname)s: %(message)s',
                datefmt="%I:%M:%S")
            ) -> LoggableObject:
        parent_logger = logging.getLogger(self.parent_logger_name)
        if new_logging_level is not None:
            parent_logger.setLevel(new_logging_level)

        if new_logging_handler is not None:
            if new_logging_level is not None:
                new_logging_handler.setLevel(new_logging_level)
            if new_logging_formatter is not None:
                new_logging_handler.setFormatter(new_logging_formatter)

            for h in parent_logger.handlers:
                if str(h) == str(new_logging_handler):
                    parent_logger.removeHandler(h)
                    parent_logger.addHandler(new_logging_handler)
                    break
            else:
                parent_logger.addHandler(new_logging_handler)

        return self

    def debug(self, msg: Optional[Any] = None, *args, **kwargs):
        """Log a DEBUG message msg via self.logger"""
        self._log_impl(level=logging.DEBUG, msg=msg, *args, **kwargs)

    def info(self, msg: Optional[Any] = None, *args, **kwargs):
        """Log an INFO message msg via self.logger"""
        self._log_impl(level=logging.INFO, msg=msg, *args, **kwargs)

    def warning(self, msg: Optional[Any] = None, *args, **kwargs):
        """Log a WARNING message msg via self.logger"""
        self._log_impl(level=logging.WARNING, msg=msg, *args, **kwargs)

    def error(self, msg: Optional[Any] = None, *args, **kwargs):
        """Log an ERROR message msg via self.logger"""
        self._log_impl(level=logging.ERROR, msg=msg, *args, **kwargs)

    def critical(self, msg: Optional[Any] = None, *args, **kwargs):
        """Log a CRITICAL message msg via self.logger"""
        self._log_impl(level=logging.CRITICAL, msg=msg, *args, **kwargs)

    def fatal(self, msg: Optional[Any] = None, *args, **kwargs):
        """Log a FATAL message msg via self.logger"""
        self._log_impl(level=logging.FATAL, msg=msg, *args, **kwargs)

    def log(self
            , level: Optional[int] = None
            , msg: Optional[Any] = None
            , *args
            , **kwargs):
        """Log a message msg with specific level via self.logger"""
        self._log_impl(level=level, msg=msg, *args, **kwargs)

    def _log_impl(self
            , level: Optional[int] = None
            , msg: Optional[Any] = None
            , *args
            , **kwargs):
        """Log a message msg via self.logger

        If msg is a string, it will be logged.
        If msg is None, str() representation of self will be logged.
        If msg has some other type, a string with object info for msg
        will be composed (including names of other variables
        holding the same object, object's type and str() representation),
        and this string will be used as a message to log.
        """
        if level is None:
            level = self.logging_level

        if msg is None:
            msg_to_log = self.selflog_prefix + str(self)
        elif isinstance(msg, str):
            msg_to_log = msg
        else:
            msg_to_log = NeatStr.object_info(
                msg, div_ch=" / ", stacks_to_skip = 2)

        self.logger.log(level, msg_to_log, *args, **kwargs)