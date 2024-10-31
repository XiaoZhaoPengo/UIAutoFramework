import logging
import sys
from colorama import init, Fore, Style
import threading

# 初始化 colorama
init(autoreset=True)

# 添加线程本地存储
local = threading.local()

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, Fore.WHITE)
        message = super().format(record)
        return f"{log_color}{message}{Style.RESET_ALL}"

class ThreadLocalHandler(logging.Handler):
    def emit(self, record):
        if not hasattr(local, 'log_buffer'):
            local.log_buffer = []
        local.log_buffer.append(self.format(record))

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    thread_local_handler = ThreadLocalHandler()
    thread_local_handler.setFormatter(console_formatter)
    logger.addHandler(thread_local_handler)

    logger.propagate = False

    return logger

# 创建一个全局的 logger 实例
logger = get_logger(__name__)

def flush_logs():
    if hasattr(local, 'log_buffer'):
        for log in local.log_buffer:
            print(log)
        local.log_buffer.clear()