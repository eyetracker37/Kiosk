from Input import input_handler
from Pages import map
from Utils import config
from Utils.logger import log_sys_info

config.initialize()  # Loads config settings
log_sys_info()  # Logs information about system for debug purposes
input_handler.initialize()  # Starts up input handler

map.run()  # Runs entry point for GUI

input_handler.close()  # If map.run() stops, close input handler
