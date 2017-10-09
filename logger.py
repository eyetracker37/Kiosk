# Level 0 - Failures
# Level 1 - Critical Logging
# Level 2 - Basic Logging
# Level 3 - Everything

severity_threshold = 2


def log(messsage, severity):
    if severity >= severity_threshold:
        print(messsage)