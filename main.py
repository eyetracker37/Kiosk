from Input import input_handler
import example_screen
from Utils import config

config.initialize()
input_handler.initialize()

example_screen.example()

input_handler.close()
