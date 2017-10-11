# Level 0 - Failures
# Level 1 - Critical Logging
# Level 2 - Basic Logging
# Level 3 - Everything

from datetime import datetime


logfile = "log.log"

severity_threshold = 3


def update_threshold(verbosity):
    global severity_threshold
    severity_threshold = verbosity


def log(message, severity):
    if severity <= severity_threshold:
        err_message = str(datetime.now()) + " - " + message
        print(err_message)
        log_file = open(logfile, 'a')
        log_file.write(err_message + '\n')
        log_file.close()
