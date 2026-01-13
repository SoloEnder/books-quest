
from app.utils import paths
from app.src import my_rotating_logsfile_handler
import logging

logger = logging.getLogger("app")
logger = logging.getLogger(__name__)
log_msg_formatter = logging.Formatter(fmt="[{asctime}] - [{name}/{levelname}] : {message}", style="{")
logs_streamhandler = logging.StreamHandler()
logs_streamhandler.setFormatter(log_msg_formatter)
logs_streamhandler.setLevel(logging.DEBUG)
logs_filehandler = my_rotating_logsfile_handler.MyRotatingFileHandler(paths.get_absfilepath("logs", "app.log"))
logs_filehandler.setFormatter(log_msg_formatter)
logs_filehandler.setLevel(logging.INFO)
logger.addHandler(logs_streamhandler)
logger.addHandler(logs_filehandler)
logger.setLevel(logging.DEBUG)