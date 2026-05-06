import logging
import os
import sys

from PySide6 import QtWidgets, QtCore
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
    qt_app = QtWidgets.QApplication()
    instance_locker = QtCore.QLockFile(os.path.join(paths.BASE_PATH, "session.lock"))
    instance_locker.setStaleLockTime(0)
    lock_result = instance_locker.tryLock(0)
    
    if not lock_result:
        error = instance_locker.error()
        msg = ""
        
        if error == instance_locker.LockError.LockFailedError:
            msg = "Another instance of book quest is running, please fully close all instance first !"
            
        elif error == instance_locker.LockError.PermissionError:
            msg = "Unable to acquire the lock : permission denied !"
            
        else:
            msg = "Unable to acquire the lock : Unknow error"
            
        logger.error(msg)
        logger.info("Exiting...")
        sys.exit()
        
    try:
        app_system = system.AppSystem(qt_app)
        app_system.set_instance_locker(instance_locker)
        app_system.start()
        sys.exit(qt_app.exec())

    except Exception:
        logger.exception("Oh no, Book Quest has crashed ! Check logs for more info.")
