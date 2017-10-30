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

    def __init__(self, window):
        super().__init__(window)
        self.image = pygame.image.load("Resources/asu_poly_map.png")
        self.imagerect = self.image.get_rect()
        self.width = self.imagerect.width
        self.height = self.imagerect.height
        self.x = self.width/2
        self.y = self.height/2

        self.x_max = self.width/2
        self.x_min = config.res_width - self.width / 2

        self.y_max = self.height / 2
        self.y_min = config.res_height - self.height / 2

    def update(self):
        pos = input_handler.get_cursor()
        if pos.is_valid:
            deadband = 100

            x_off = pos.x_pos - config.screen_x / 2
            y_off = pos.y_pos - config.screen_y / 2

            if y_off > deadband:
                self.y -= 5
            elif y_off < -deadband:
                self.y += 5

            if x_off > deadband:
                self.x -= 5
            elif x_off < -deadband:
                self.x += 5

            if self.x > self.x_max:
                self.x = self.x_max
            elif self.x < self.x_min:
                self.x = self.x_min

            if self.y > self.y_max:
                self.y = self.y_max
            elif self.y < self.y_min:
                self.y = self.y_min
        self.imagerect.center = (self.x, self.y)

    def draw(self):
        super().draw()
        self.screen.blit(self.image, self.imagerect)


def run():

    master = window_elements.MasterWindow()

    window = window_elements.Subwindow(master)
    master.set_window(window)
    Cursor(window)
    Background(window)

    window_elements.run_master(master)