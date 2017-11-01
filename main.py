from Input import input_handler
from Pages import map
from Utils import config
from Utils.logger import log
import pygame
import platform

log("Platform " + platform.platform(), 1)
log("Processor " + platform.machine(), 1)
log("Python version " + platform.python_version(), 1)
log("PyGame version " + pygame.version.ver, 1)

config.initialize()
input_handler.initialize()

map.run()

input_handler.close()
