import logging
import os
import sys
import traceback

from app import system
from app.src import my_logging_stuff
from app.utils import paths

fmter = logging.Formatter(
    fmt="[{asctime}] - [{name}/{levelname}] : {message}", style="{"
)
logger = logging.getLogger(__name__)
mrfh = my_logging_stuff.MyRotatingFileHandler(os.path.join(paths.LOGS_PATH, "main.log"))
mrfh.setFormatter(fmter)
sh = logging.StreamHandler()
sh.setFormatter(fmter)
sh.addFilter(my_logging_stuff.ErrorsFilter())
logger.addHandler(mrfh)
logger.addHandler(sh)
logger.addFilter(my_logging_stuff.SensitiveInfoFilter())

if __name__ == "__main__":
    try:
        app_system = system.AppSystem()
        app_system.running()

    except Exception:
        logger.critical(traceback.format_exc())
        sys.exit()
