from __future__ import annotations
import logging
import inspect
from typing import Optional, Any, List


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
                 ):
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
            all_names = self.reveal_object_names(self)
            if len(all_names):
                logger_name += "." + ".".join(all_names)
        return logging.getLogger(logger_name)

    def reveal_object_names(self, an_object: Any) -> List[str]:
        """ Find the name(s) of variable(s) that are aliases for self.

        The function uses a naive but fast approach,
        it does not always find all the names
        """
        all_names = []

        for f in reversed(inspect.stack()):
            local_vars = f.frame.f_locals
            names = [name for name in local_vars if
                     local_vars[name] is an_object]
            if "self" in names:
                names.remove("self")
            all_names += names

        all_names.remove("an_object")
        all_names = list(dict.fromkeys(all_names))  # dedup but keep the order

        return all_names

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
                             ,
                             new_logging_handler: logging.Handler = logging.StreamHandler()
                             ,
                             new_logging_formatter: logging.Formatter = logging.Formatter(
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
        self.log(level=logging.DEBUG, msg=msg, *args, **kwargs)

    def info(self, msg: Optional[Any] = None, *args, **kwargs):
        self.log(level=logging.INFO, msg=msg, *args, **kwargs)

    def warning(self, msg: Optional[Any] = None, *args, **kwargs):
        self.log(level=logging.WARNING, msg=msg, *args, **kwargs)

    def error(self, msg: Optional[Any] = None, *args, **kwargs):
        self.log(level=logging.ERROR, msg=msg, *args, **kwargs)

    def critical(self, msg: Optional[Any] = None, *args, **kwargs):
        self.log(level=logging.CRITICAL, msg=msg, *args, **kwargs)

    def fatal(self, msg: Optional[Any] = None, *args, **kwargs):
        self.log(level=logging.FATAL, msg=msg, *args, **kwargs)

    def log(self
            , level: Optional[int] = None
            , msg: Optional[Any] = None
            , *args
            , **kwargs):

        if level is None:
            level = self.logging_level

        if msg is None:
            msg_to_log = self.selflog_prefix + str(self)
        elif isinstance(msg, str):
            msg_to_log = msg
        else:
            msg_to_log = "Object <"
            names = self.reveal_object_names(msg)
            if "msg" in names:
                names.remove("msg")
            if len(names):
                msg_to_log += " / ".join(names)
            msg_to_log += "> has type <"
            msg_to_log += type(msg).__qualname__
            msg_to_log += "> and value <"
            msg_to_log += repr(msg)
            msg_to_log += ">"

            msg_to_log = msg_to_log.replace("  ", " ")
            msg_to_log = msg_to_log.replace("<<", "<")
            msg_to_log = msg_to_log.replace(">>", ">")

        self.logger.log(level, msg_to_log, *args, **kwargs)
