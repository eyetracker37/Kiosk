import pygame
from Utils import config
from Input import input_handler
from Elements import window_elements
from Utils.logger import  log

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


class Cursor(window_elements.ChildElement):
    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.x = 0
        self.y = 0

    def update(self):
        super().update()
        pos = input_handler.get_cursor()
        if pos.is_valid:
            self.x = pos.x_pos
            self.y = pos.y_pos

    def draw(self):
        super().draw()
        pygame.draw.circle(self.screen, BLUE, [self.x, self.y], 40)


class Background(window_elements.ChildElement):
    priority = 0

    def draw(self):
        super().draw()
        self.screen.fill(WHITE)


class Rectangle(window_elements.ChildElement):
    def __init__(self, parent_window):
        self.priority = 0
        super().__init__(parent_window)
        self.x = config.screen_x / 2
        self.y = config.screen_y / 2

    def draw(self):
        super().draw()
        pygame.draw.rect(self.screen, BLACK, [150, 10, 50, 20])


def example():

    master = window_elements.MasterWindow()

    window = window_elements.Subwindow(master)
    master.set_window(window)
    Cursor(window)
    Rectangle(window)
    Background(window)

    window_elements.run_master(master)
