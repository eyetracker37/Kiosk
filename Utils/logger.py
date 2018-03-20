# Level 0 - Failures
# Level 1 - Critical Logging
# Level 2 - Basic Logging
# Level 3 - Everything

from datetime import datetime
from Utils.thread_manager import log_lock
import platform
import pygame
import threading


logfile = "log.log"

severity_threshold = 3
write_log = False


def update_threshold(verbosity):
    global severity_threshold
    severity_threshold = verbosity


def set_write_log(setter):
    global write_log
    write_log = setter


# Log a message, higher severity = less important
def log(message, severity):
    if severity <= severity_threshold:
        err_message = str(datetime.now()) + " - " + message
        thread_id = threading.get_ident()
        err_message = str(datetime.now()) + " - " + str(thread_id) + " - " + message
        with log_lock:
            print(err_message)

            global write_log
            if write_log:
                log_file = open(logfile, 'a')
                log_file.write(err_message + '\n')
                log_file.close()


# Log system information for debug purposes
def log_sys_info():
    log("Platform " + platform.platform(), 1)
    log("Processor " + platform.machine(), 1)
    log("Python version " + platform.python_version(), 1)
    log("PyGame version " + pygame.version.ver, 1)
