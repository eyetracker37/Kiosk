from Utils import config
import pygame
from Utils.logger import log


def scale(value, scalar=1):
    return int(value * config.scale_factor * scalar)


def get_image(url, resize=1):
    try:
        raw = pygame.image.load(url)
    except pygame.error:
        log(url + " does not exist", 0)
        return None
    width = scale(raw.get_rect().size[0], resize)
    height = scale(raw.get_rect().size[1], resize)
    scaled_image = pygame.transform.scale(raw, (width, height))
    return scaled_image
