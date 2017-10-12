import pygame
from pygame.locals import *
from Utils import config
from Input import input_handler

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


def example():
    pygame.init()
    size = [0, 0]
    screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    done = False

    while not done:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == K_q:
                    done = True

        screen.fill(WHITE)
        pos = input_handler.get_cursor()
        if pos.is_valid:
            pygame.draw.circle(screen, BLUE, [pos.x_pos, pos.y_pos], 40)

        pygame.display.flip()

    pygame.quit()
