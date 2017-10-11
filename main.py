from Input import input_handler
import example_screen
from Utils import config

config.initialize()
input_handler.initialize()

#for i in range(0, 100):
#    cursor = input_handler.get_cursor()
#    if cursor.is_valid:
#        print(cursor.x_pos)
#    sleep(0.1)
example_screen.example()

input_handler.close()
