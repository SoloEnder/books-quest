
from app.utils import paths
from app.src import my_logging_stuff
import logging

logger = logging.getLogger("app")
logger = logging.getLogger(__name__)
log_msg_formatter = logging.Formatter(fmt="[{asctime}] - [{name}/{levelname}] : {message}", style="{")
logs_streamhandler = logging.StreamHandler()
logs_streamhandler.setFormatter(log_msg_formatter)
logs_streamhandler.setLevel(logging.DEBUG)
logs_filehandler = my_logging_stuff.MyRotatingFileHandler(paths.get_abspath("app/logs/app.log"), maxBytes=1000000, backupCount=5)
logs_filehandler.setFormatter(log_msg_formatter)
logs_filehandler.setLevel(logging.INFO)
logger.addHandler(logs_streamhandler)
logger.addHandler(logs_filehandler)
logger.setLevel(logging.DEBUG)
logs_filehandler.addFilter(my_logging_stuff.ErrorsFilter())
logs_filehandler.addFilter(my_logging_stuff.SensitiveInfoFilter())
logs_streamhandler.addFilter(my_logging_stuff.SensitiveInfoFilter())