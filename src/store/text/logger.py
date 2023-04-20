import logging
import multiprocessing
import os
import threading


# TODO 加入memory的功能
class Logger:
    """
    日志记录器，实现了单例模式（线程安全和进程安全）
    日志包括debug、info、warning、error、critical五个级别,
    可以通过log_console和log_file参数控制是否将日志输出到控制台和文件
    额外实现了一个log方法，等价于warning
    """
    _instance_lock = threading.Lock()
    _process_lock = multiprocessing.Lock()
    _instance = None

    def __new__(cls, log_file=None, history_file=None):
        """
        单例模式，保证只有一个日志记录器
        :param log_file: 日志文件路径，如果不指定则默认为当前目录下的log.txt
        """
        if not cls._instance:
            with cls._process_lock:
                with cls._instance_lock:
                    if not cls._instance:
                        cls._instance = super().__new__(cls)
                        cls._instance.logger = logging.getLogger(__name__)
                        cls._instance.logger.setLevel(logging.DEBUG)

                        # 创建文件处理器，将日志写入指定文件
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

                        # 创建控制台处理器，将日志打印到控制台
                        cls._instance.console_handler = logging.StreamHandler()
                        cls._instance.console_handler.setLevel(logging.DEBUG)

                        # 创建格式器，设置日志格式
                        formatter_history = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                        cls._instance.log_handler.setFormatter(formatter_history)
                        cls._instance.console_handler.setFormatter(formatter_history)
                        formatter_history = logging.Formatter('%(asctime)s -  %(message)s')
                        cls._instance.history_handler.setFormatter(formatter_history)

                        # 将处理器添加到日志记录器中
                        cls._instance.logger.addHandler(cls._instance.log_handler)
                        cls._instance.logger.addHandler(cls._instance.console_handler)
        return cls._instance

    def debug(self, message, log_console=True, log_file=True):
        """
        记录debug级别的日志，下同
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
        等价于warning
        :param message:
        :param log_console:
        :param log_file:
        :return:
        """
        self.warning(message, log_console, log_file)

    def history(self, message):
        self.logger.info(message)  # 额外在log中保存一份
        self.logger.removeHandler(self.console_handler)
        self.logger.removeHandler(self.log_handler)
        self.logger.addHandler(self.history_handler)
        self.logger.info(message)
        self.logger.removeHandler(self.history_handler)
        self.logger.addHandler(self.log_handler)
        self.logger.addHandler(self.console_handler)
