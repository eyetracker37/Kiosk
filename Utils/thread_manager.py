from threading import Lock
import pygame

thread_id = 0

# Lock for input data (e.g tracker)
input_lock = Lock()

# Lock for control of screen elements (e.g draw or update)
screen_lock = Lock()

# Lock for logging
log_lock = Lock()

clock = pygame.time.Clock()

running = True


# Get a unique ID for thread
def get_thread_id():
    global thread_id
    thread_id += 1
    return thread_id
