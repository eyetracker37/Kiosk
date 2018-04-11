from Pages import map, info, welcome
from Pages import Calibration_Screen
from Utils import config
from Utils.logger import log_sys_info
from Elements import window_elements

config.initialize()  # Loads config settings
log_sys_info()  # Logs information about system for debug purposes

master = window_elements.WindowManager()

if config.use_tracker:
    welcome.run()  # Load welcome screen
else:
    #info.run(master, "CitrusDiningPavilion")  # Use this to enter directly to info screen
    map.run(master)  # Runs entry point for GUI

window_elements.run_master(master)
