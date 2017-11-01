import pygame
import pygame.gfxdraw
from Utils import config
from Input import input_handler
from Elements import window_elements
from Utils.logger import log

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


class Background(window_elements.ChildElement):
    priority = 0

    def __init__(self, window):
        super().__init__(window)
        self.image = pygame.image.load("Resources/asu_poly_map.bmp")
        self.imagerect = self.image.get_rect()
        self.width = self.imagerect.width
        self.height = self.imagerect.height
        self.x = self.width/2
        self.y = self.height/2

        self.x_max = self.width/2
        self.x_min = config.screen_x - self.width/2

        self.y_max = self.height/2
        self.y_min = config.screen_y - self.height/2

        self.off_x = 0
        self.off_y = 0

        self.cursor = input_handler.get_cursor()

    def update(self):
        self.cursor = input_handler.get_cursor()
        if self.cursor.is_valid:
            deadband = 100
            min_speed = 5
            feathering = 30

            x_off = self.cursor.x_pos - config.screen_x / 2
            y_off = self.cursor.y_pos - config.screen_y / 2

            if y_off > deadband:
                speed = min_speed + (y_off - deadband) / feathering
                self.y -= speed
            elif y_off < -deadband:
                speed = -min_speed + (y_off + deadband) / feathering
                self.y -= speed

            if x_off > deadband:
                speed = min_speed + (x_off - deadband) / feathering
                self.x -= speed
            elif x_off < -deadband:
                speed = - min_speed + (x_off + deadband) / feathering
                self.x -= speed

            if self.x > self.x_max:
                self.x = self.x_max
            elif self.x < self.x_min:
                self.x = self.x_min

            if self.y > self.y_max:
                self.y = self.y_max
            elif self.y < self.y_min:
                self.y = self.y_min

            self.off_x = self.x - self.width/2
            self.off_y = self.y - self.height/2

        self.imagerect.center = (self.x, self.y)

    def draw(self):
        super().draw()
        self.screen.blit(self.image, self.imagerect)

    def get_offset(self):
        return self.off_x, self.off_y


class InteractionBox(window_elements.ChildElement):
    priority = 255

    def __init__(self, background, x, y, width, height):
        self.color = BLACK
        self.background = background
        parent = background.parent
        super().__init__(parent)
        self.base_x = x
        self.base_y = y
        self.box = pygame.Rect(x, y, width, height)
        self.is_selected = 0

    def draw(self):
        super().draw()
        if self.is_selected:
            pygame.gfxdraw.rectangle(self.screen, self.box, (255, 0, 0, self.is_selected))

    def update(self):
        self.box.x = self.base_x + self.background.off_x
        self.box.y = self.base_y + self.background.off_y

        cursor_x = self.background.cursor.x_pos
        cursor_y = self.background.cursor.y_pos

        if self.background.cursor.is_valid \
                and self.box.collidepoint(cursor_x, cursor_y):
            self.is_selected += 10
            if self.is_selected > 255:
                log("Button pressed", 2)
                self.is_selected = 0
        else:
            if self.is_selected > 0:
                self.is_selected -= 25
                if self.is_selected < 0:
                    self.is_selected = 0


def run():
    log("Map window loading", 2)
    master = window_elements.MasterWindow()

    window = window_elements.Subwindow(master)
    master.set_window(window)
    background = Background(window)
    InteractionBox(background, 837, 837, 135, 119)  # TECH
    log("Loaded map window", 3)

    window_elements.run_master(master)
