import input_handler
from time import sleep

input_handler.initialize()

for i in range(0, 100):
    cursor = input_handler.get_cursor()
    if cursor.is_valid:
        print(cursor.x_pos)
    sleep(0.1)

input_handler.close()