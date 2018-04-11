import pygame
import pygame.gfxdraw
from Utils import config
from math import sqrt
from Elements import window_elements
from Utils.logger import log
from enum import Enum
from Input import quick_link
from Pages import map

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


# Map background
class Background(window_elements.HierarchyObject):
    priority = 0  # Draw on bottom

    def draw(self):
        self.screen.fill(BLUE)
        super().draw()


class CalibrationPoint(window_elements.HierarchyObject):
    def __init__(self, parent, calibration):
        super().__init__(parent)
        self.current_target = None
        self.calibration = calibration
        self.targets = quick_link.calibration_get_targets(calibration)
        self.x = config.screen_x / 2
        self.y = config.screen_y / 2
        self.target_x = 200.0
        self.target_y = 100.0
        self.state = States.GETTING_TARGET
        self.speed = 15.0
        self.num_targets = len(self.targets)
        self.calibrations_remaining = self.num_targets
        self.grown_size = 100
        self.grow_speed = 2
        self.shrunk_size = 20
        self.shrink_speed = 1
        self.size = self.grown_size
        self.color = WHITE

    def is_calibrating(self):
        status = quick_link.calibration_get_status(self.calibration, self.current_target)
        if status == 4 or status == 3 or status == 2:
            log("Calibration failed", 0)
            self.start_calibrating()
        return status

    def get_target(self):
        target_id = self.targets[self.calibrations_remaining][0]
        x_target = int(self.targets[self.calibrations_remaining][1] * config.screen_x / 100)
        y_target = int(self.targets[self.calibrations_remaining][2] * config.screen_y / 100)
        return [target_id, x_target, y_target]

    def start_calibrating(self):
        quick_link.calibration_calibrate(self.calibration, self.current_target, 2000, False)

    def get_scoring(self):
        score_sum = 0
        for i in range(self.num_targets):
            score_l = round(quick_link.calibration_get_scoring(self.calibration, i, quick_link.QL_EYE_TYPE_LEFT), 2)
            score_r = round(quick_link.calibration_get_scoring(self.calibration, i, quick_link.QL_EYE_TYPE_RIGHT), 2)
            score_sum += score_l + score_r
            log("Score for target " + str(i) + ": " + str(score_l) + ", " + str(score_r), 3)
        average_score = round(score_sum / (self.num_targets * 2), 2)
        log("Average score: " + str(average_score), 2)

    def apply(self):
        quick_link.calibration_finalize(self.calibration)
        quick_link.apply_calibration(self.calibration)
        log("Calibration complete", 2)
        map.run(self.master)

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
            if abs(offset_x) < abs(x_distance) + 0.1 and abs(offset_y) < abs(y_distance) + 0.1:
                self.x = self.target_x
                self.y = self.target_y
                self.state = States.SHRINKING
            else:
                self.x += x_distance
                self.y += y_distance
        elif self.state == States.CALIBRATING:
            if not self.is_calibrating():
                self.state = States.GROWING
                log("Calibrated point", 2)
                self.color = WHITE
        elif self.state == States.GETTING_TARGET:
            if self.calibrations_remaining:
                self.calibrations_remaining -= 1
                self.current_target, self.target_x, self.target_y = self.get_target()
                self.state = States.GOING_TO_TARGET
                log("Going to point " + str(self.target_x) + "," + str(self.target_y), 2)
            else:
                self.state = States.DONE
                log("Calibration done", 1)
                self.get_scoring()
                self.apply()
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
                self.start_calibrating
                self.state = States.CALIBRATING
                self.color = RED

    def draw(self):
        super().draw()
        pygame.draw.circle(self.screen, self.color, [int(self.x), int(self.y)], self.size)


def run(master):
    log("Calibration starting", 2)

    log("Creating calibration file", 3)
    calibration = quick_link.calibration_create()
    identifier = quick_link.connected_device

    log("Initializing calibration", 3)
    quick_link.calibration_initialize(identifier, calibration)

    window = window_elements.HierarchyObject(master)

    CalibrationPoint(window, calibration)
    Background(window)
    log("Loaded calibration window", 3)
