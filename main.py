from Input import input_handler
from Pages import map
from Utils import config
from Utils.logger import log_sys_info

log_sys_info()

config.initialize()
input_handler.initialize()

map.run()

input_handler.close()
