import logging
import os
from datetime import datetime
from config_loader import ConfigLoader

# static class
class LoggingManager:

    _log_level = ConfigLoader.get("logging", "log_level")
    _log_path = ConfigLoader.get("logging", "log_path")
    _log_format = ConfigLoader.get("logging", "log_format")
    _log_time = datetime.now().strftime('-%Y%m%d-%H%M') if ConfigLoader.get("logging", "log_file_with_time") else ''

    # check if log path exists, if not create it
    if not os.path.exists(_log_path):
        os.makedirs(_log_path)
    
    # name-logger pairs
    _loggers = {}

    @staticmethod
    def debug(message, name):
        LoggingManager.log(message, name, "DEBUG")

    @staticmethod
    def info(message, name):
        LoggingManager.log(message, name, "INFO")

    @staticmethod
    def warning(message, name):
        LoggingManager.log(message, name, "WARNING")

    @staticmethod
    def error(message, name):
        LoggingManager.log(message, name, "ERROR")

    @staticmethod
    def critical(message, name):
        LoggingManager.log(message, name, "CRITICAL")

    @staticmethod
    def log(message, name, level):
        # check if logger exists
        if name not in LoggingManager._loggers:
            # create logger
            logger = logging.getLogger(name)
            logger.setLevel(LoggingManager._log_level)
            # create file handler
            fh = logging.FileHandler(LoggingManager._log_path + 'chatgpt-telegram-bot%s.log' % LoggingManager._log_time)
            fh.setLevel(LoggingManager._log_level)
            # create formatter
            formatter = logging.Formatter(LoggingManager._log_format)
            # add formatter to fh
            fh.setFormatter(formatter)
            # add fh to logger
            logger.addHandler(fh)
            # add logger to _loggers
            LoggingManager._loggers[name] = logger
        # log message
        level_map = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}
        if level not in level_map:
            raise Exception('Invalid log level string')
        LoggingManager._loggers[name].log(level_map[level], message)

if __name__ == "__main__":
    LoggingManager.log('This is an INFO message from Module A', 'Module_A', "INFO")
    LoggingManager.log('This is an ERROR message from Module A', 'Module_A', "ERROR")
    LoggingManager.log('This is a DEBUG message from Module B', 'Module_B', "AAA")
    LoggingManager.info('This is an INFO message from Module C', 'Module_C')
    LoggingManager.critical('This is an CRITICAL message from Module A', 'Module_A')