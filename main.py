from Input import input_handler
from Pages import map
from Utils import config

config.initialize()
input_handler.initialize()

map.run()

input_handler.close()
