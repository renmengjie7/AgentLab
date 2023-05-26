import logging
import multiprocessing
import os
import threading
from typing import Union
import inspect


# TODO 加入memory的功能
class Logger:
    """
    The logger implements the singleton mode (thread safety and process safety).
    The log includes five levels of debug, info, warning, error, and critical.
    You can control whether to output the log to the console and file through the log_console and log_file parameters.
    Additional implementation method `log`, which is equivalent to warning
    """
    _instance_lock = threading.Lock()
    _process_lock = multiprocessing.Lock()
    _instance = None

    def __new__(cls, log_file=None, history_file=None):
        if not cls._instance:
            with cls._process_lock:
                with cls._instance_lock:
                    if not cls._instance:
                        cls._instance = super().__new__(cls)
                        cls._instance.logger = logging.getLogger(__name__)
                        cls._instance.logger.setLevel(logging.DEBUG)

                        if log_file:
                            log_file_path = os.path.abspath(log_file)
                        else:
                            log_file_path = os.path.abspath('log.txt')
                        cls._instance.log_handler = logging.FileHandler(log_file_path)
                        cls._instance.log_handler.setLevel(logging.DEBUG)

                        if history_file:
                            history_file_path = os.path.abspath(history_file)
                        else:
                            history_file_path = os.path.abspath('history.txt')
                        cls._instance.history_handler = logging.FileHandler(history_file_path)
                        cls._instance.history_handler.setLevel(logging.DEBUG)

                        cls._instance.console_handler = logging.StreamHandler()
                        cls._instance.console_handler.setLevel(logging.ERROR)

                        formatter_history = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                        cls._instance.log_handler.setFormatter(formatter_history)
                        cls._instance.console_handler.setFormatter(formatter_history)
                        formatter_history = logging.Formatter('%(asctime)s -  %(message)s')
                        cls._instance.history_handler.setFormatter(formatter_history)

                        cls._instance.logger.addHandler(cls._instance.log_handler)
                        cls._instance.logger.addHandler(cls._instance.console_handler)
        return cls._instance

    def debug(self, message, log_console=True, log_file=True):
        """
        :param message:
        :param log_console:
        :param log_file:
        :return:
        """
        if log_console and log_file:
            self.logger.debug(message)
        elif log_console:
            self.logger.removeHandler(self.log_handler)
            self.logger.debug(message)
            self.logger.addHandler(self.log_handler)
        elif log_file:
            self.logger.removeHandler(self.console_handler)
            self.logger.debug(message)
            self.logger.addHandler(self.console_handler)
        else:
            pass

    def info(self, message, log_console=True, log_file=True):
        if log_console and log_file:
            self.logger.info(message)
        elif log_console:
            self.logger.removeHandler(self.log_handler)
            self.logger.info(message)
            self.logger.addHandler(self.log_handler)
        elif log_file:
            self.logger.removeHandler(self.console_handler)
            self.logger.info(message)
            self.logger.addHandler(self.console_handler)
        else:
            pass

    def warning(self, message, log_console=True, log_file=True):
        caller_frame = inspect.currentframe().f_back
        caller_info = inspect.getouterframes(caller_frame, 2)[1]
        caller_name = caller_info.function
        caller_class = caller_info.frame.f_locals.get('self').__class__.__name__
        message = f'{caller_class}.{caller_name} - {message}'
        if log_console and log_file:
            self.logger.warning(message)
        elif log_console:
            self.logger.removeHandler(self.log_handler)
            self.logger.warning(message)
            self.logger.addHandler(self.log_handler)
        elif log_file:
            self.logger.removeHandler(self.console_handler)
            self.logger.warning(message)
            self.logger.addHandler(self.console_handler)
        else:
            pass

    def error(self, message, log_console=True, log_file=True):
        caller_frame = inspect.currentframe().f_back
        caller_info = inspect.getouterframes(caller_frame, 2)[1]
        caller_name = caller_info.function
        caller_class = caller_info.frame.f_locals.get('self').__class__.__name__
        message = f'{caller_class}.{caller_name} - {message}'
        if log_console and log_file:
            self.logger.error(message)
        elif log_console:
            self.logger.removeHandler(self.log_handler)
            self.logger.error(message)
            self.logger.addHandler(self.log_handler)
        elif log_file:
            self.logger.removeHandler(self.console_handler)
            self.logger.error(message)
            self.logger.addHandler(self.console_handler)
        else:
            pass

    def critical(self, message, log_console=True, log_file=True):
        caller_frame = inspect.currentframe().f_back
        caller_info = inspect.getouterframes(caller_frame, 2)[1]
        caller_name = caller_info.function
        caller_class = caller_info.frame.f_locals.get('self').__class__.__name__
        message = f'{caller_class}.{caller_name} - {message}'
        if log_console and log_file:
            self.logger.critical(message)
        elif log_console:
            self.logger.removeHandler(self.log_handler)
            self.logger.critical(message)
            self.logger.addHandler(self.log_handler)
        elif log_file:
            self.logger.removeHandler(self.console_handler)
            self.logger.critical(message)
            self.logger.addHandler(self.console_handler)
        else:
            pass

    def log(self, message, log_console=True, log_file=True):
        """
        :param message:
        :param log_console:
        :param log_file:
        :return:
        """
        self.warning(message, log_console, log_file)

    def history(self, message):
        """
        will also call `self.logger.info(message)`
        :param message:
        :return:
        """
        self.logger.info(message)
        self.logger.removeHandler(self.console_handler)
        self.logger.removeHandler(self.log_handler)
        self.logger.addHandler(self.history_handler)
        self.logger.info(message)
        self.logger.removeHandler(self.history_handler)
        self.logger.addHandler(self.log_handler)
        self.logger.addHandler(self.console_handler)

    def set_level(self, level: Union[int, str]):
        """
        :param level:
        :return:
        """
        self.logger.setLevel(level)
