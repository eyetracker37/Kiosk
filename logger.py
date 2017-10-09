# Level 0 - Failures
# Level 1 - Critical Logging
# Level 2 - Basic Logging
# Level 3 - Everything

from datetime import datetime

severity_threshold = 3


def log(message, severity):
    if severity >= severity_threshold:
        print(str(datetime.now()) + " - " + message)
