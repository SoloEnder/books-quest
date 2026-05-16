import logging
import os

from app.src import my_logging_stuff
from app.utils import paths

logger = logging.getLogger("app")
logger = logging.getLogger(__name__)
log_msg_formatter = logging.Formatter(
    fmt="[{asctime}] - [{name}/{levelname}] : {message}", style="{"
)
logs_filehandler = my_logging_stuff.MyRotatingFileHandler(
    os.path.join(paths.BASE_PATH, "logs", "app.log"), maxBytes=1000000, backupCount=5
)
logs_filehandler.setFormatter(log_msg_formatter)
logs_filehandler.setLevel(logging.INFO)
logs_streamhandler = logging.StreamHandler()
logs_streamhandler.setFormatter(log_msg_formatter)
logs_streamhandler.setLevel(logging.DEBUG)
logger.addHandler(logs_streamhandler)
logger.addHandler(logs_filehandler)
logger.setLevel(logging.DEBUG)
#logs_filehandler.addFilter(my_logging_stuff.ErrorsFilter())
logs_filehandler.addFilter(my_logging_stuff.SensitiveInfoFilter())
logs_streamhandler.addFilter(my_logging_stuff.SensitiveInfoFilter())
