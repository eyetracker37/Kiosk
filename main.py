from Input import input_handler
from Pages import Calibration_Screen
from Utils import config
from Utils.logger import log_sys_info

config.initialize()  # Loads config settings
log_sys_info()  # Logs information about system for debug purposes
input_handler.initialize()  # Starts up input handler

Calibration_Screen.run()  # Runs entry point for GUI

input_handler.close()  # If Calibration_Screen.run() stops, close input handler
