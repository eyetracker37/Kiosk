from Input import input_handler
<<<<<<< .merge_file_a12432
from Pages import map, info
=======
from Pages import Calibration_Screen
>>>>>>> .merge_file_a19796
from Utils import config
from Utils.logger import log_sys_info
from Elements import window_elements

config.initialize()  # Loads config settings
log_sys_info()  # Logs information about system for debug purposes
input_handler.initialize()  # Starts up input handler

<<<<<<< .merge_file_a12432
master = window_elements.MasterWindow()
#info.run(master, "AravaipaAuditorium")  # Use this to enter directly to info screen
map.run(master)  # Runs entry point for GUI

window_elements.run_master(master)
input_handler.close()  # If map.run() stops, close input handler
=======
Calibration_Screen.run()  # Runs entry point for GUI

input_handler.close()  # If Calibration_Screen.run() stops, close input handler
>>>>>>> .merge_file_a19796
