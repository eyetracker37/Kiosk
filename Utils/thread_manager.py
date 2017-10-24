from threading import Lock
import pygame

thread_id = 0

input_lock = Lock()
screen_lock = Lock()

clock = pygame.time.Clock()


def get_thread_id():
    global thread_id
    thread_id += 1
    return thread_id
