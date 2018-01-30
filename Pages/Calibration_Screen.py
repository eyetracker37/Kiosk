import pygame
import pygame.gfxdraw
from Utils import config
from math import sqrt
from Elements import window_elements
from Utils.logger import log
from enum import Enum
from random import randint

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


class States(Enum):
    GOING_TO_TARGET = 1
    CALIBRATING = 2
    GETTING_TARGET = 3
    DONE = 4
    GROWING = 5
    SHRINKING = 6


def is_calibrated():
    number = randint(0, 100)
    return number == 50


def get_target():
    x_target = randint(0, config.screen_x)
    y_target = randint(0, config.screen_y)
    return [x_target, y_target]


# Map background
class Background(window_elements.ChildElement):
    priority = 0  # Draw on bottom

    def draw(self):
        super().draw()
        self.screen.fill(BLUE)


class CalibrationPoint(window_elements.ChildElement):
    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.x = 0.0
        self.y = 0.0
        self.target_x = 200.0
        self.target_y = 100.0
        self.state = States.GETTING_TARGET
        self.speed = 15.0
        self.calibrations_remaining = 5
        self.grown_size = 100
        self.grow_speed = 2
        self.shrunk_size = 20
        self.shrink_speed = 1
        self.size = self.grown_size
        self.color = WHITE

    def update(self):
        super().update()
        if self.state == States.GOING_TO_TARGET:
            x_distance = self.target_x-self.x
            offset_x = x_distance
            y_distance = self.target_y-self.y
            offset_y = y_distance
            magnitude = sqrt(x_distance**2+y_distance**2)
            x_distance /= magnitude
            y_distance /= magnitude
            x_distance *= self.speed
            y_distance *= self.speed
            if abs(offset_x) < abs(x_distance) and abs(offset_y) < abs(y_distance):
                self.x = self.target_x
                self.y = self.target_y
                self.state = States.SHRINKING
            else:
                self.x += x_distance
                self.y += y_distance
        elif self.state == States.CALIBRATING:
            if is_calibrated():
                self.state = States.GROWING
                log("Calibrated point", 2)
                self.color = WHITE
        elif self.state == States.GETTING_TARGET:
            if self.calibrations_remaining:  # anything no zero true anything larger it will keep going
                self.calibrations_remaining -= 1
                self.target_x, self.target_y = get_target()
                self.state = States.GOING_TO_TARGET
                log("Going to point " + str(self.target_x) + "," + str(self.target_y), 2)
            else:
                self.state = States.DONE
                log("Calibration done", 1)
        elif self.state == States.DONE:
            pass
        elif self.state == States.GROWING:
            if self.size < self.grown_size:
                self.size += self.grow_speed
            else:
                self.state = States.GETTING_TARGET
        elif self.state == States.SHRINKING:
            if self.size > self.shrunk_size:
                self.size -= self.shrink_speed
            else:
                self.state = States.CALIBRATING
                self.color = RED

    def draw(self):
        super().draw()
        pygame.draw.circle(self.screen, self.color, [int(self.x), int(self.y)], self.size)


def run():
    log("Map window loading", 2)
    master = window_elements.MasterWindow()
    window = window_elements.Subwindow(master)
    master.set_window(window)
    CalibrationPoint(window)
    Background(window)
    log("Loaded map window", 3)

    window_elements.run_master(master)
