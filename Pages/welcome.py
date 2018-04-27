from Elements import window_elements
from Utils.logger import log
from Pages import Calibration_Screen
import pygame
from Utils import config
from Utils.scale import scale

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


class IntroScreen(window_elements.HierarchyObject):
    priority = 0  # Draw on bottom

    def __init__(self, window):
        super().__init__(window)
        font = "opensans"
        size = scale(80)
        text = "Look at the screen to start"
        self.font = pygame.font.SysFont(font, size)
        self.display_text = self.font.render(text, True, (0, 0, 0))

        width, height = self.font.size(text)

        self.x_off = (config.screen_x - width) / 2
        self.y_off = (config.screen_y - height) / 2

        self.draw()

    def draw(self):
        self.screen.fill(WHITE)
        try:
            self.screen.blit(self.display_text, (self.x_off, self.y_off))
        except AttributeError:
            pass
        super().draw()


def run(master):
    log("Intro screen loading", 2)

    window = window_elements.HierarchyObject(master)
    log("Window set to intro screen", 3)

    IntroScreen(window)

    log("Loaded intro screen", 3)

    master.cursor.start()  # Wait for eyes to be detected

    Calibration_Screen.run(master)  #
