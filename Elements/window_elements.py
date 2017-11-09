from Utils.logger import log
import pygame
from pygame.locals import *
from Utils import thread_manager
import threading
from time import sleep
from Utils import config


class UpdateThread(threading.Thread):
    def __init__(self, creator):
        self.is_running = False
        threading.Thread.__init__(self)
        self.threadID = thread_manager.get_thread_id()
        self.creator = creator

    def kill(self):
        self.is_running = False

    def run(self):
        log("Starting screen update thread", 2)
        self.is_running = True
        while self.is_running:

                try:
                    self.creator.update()
                except AttributeError:
                    pass


# Master window handler, responsible for managing the screen
class MasterWindow:
    current_window = None
    previous_window = None

    def __init__(self):

        # Creates the screen
        pygame.init()
        size = [config.screen_x, config.screen_y]
        got_resolution_x = pygame.display.Info().current_w
        got_resolution_y = pygame.display.Info().current_h
        log("Attempting to start screen of size " + str(size) +
            " on monitor of size [" + str(got_resolution_x) + ", " + str(got_resolution_y) + "]", 2)
        if size[0] > got_resolution_x:
            log("Horizontal screen resolution " + str(got_resolution_x) + " too small for desired width " + str(size[0])
                + ", decreasing to " + str(got_resolution_x), 0)
            size[0] = got_resolution_x

        if size[1] > got_resolution_y:
            log("Vertical screen resolution " + str(got_resolution_y) + " too small for desired width " + str(size[1])
                + ", decreasing to " + str(got_resolution_y), 0)

            size[1] = got_resolution_y

        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        self.done = False
        log("Master screen started", 2)

        # Creates and starts the update thread
        self.update_thread = UpdateThread(self)
        self.update_thread.start()
        self.last_tick = pygame.time.get_ticks()

    # Set which window is being displayed
    def set_window(self, window):
        self.current_window = window

    # Kill update thread
    def kill_threads(self):
        log("Killing threads", 2)
        self.update_thread.kill()
        pygame.quit()
        self.done = True

    # Draws the elements on the screen
    def draw(self):

        # Handling for keyboard presses has to be in draw task, since it can't be in a thread
        # and must instead be in the master task
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.kill_threads()
            elif event.type == pygame.KEYDOWN:
                if event.key == K_q:
                    self.kill_threads()
            else:
                pass

        self.current_window.draw()

    # Updates the elements on the screen, but does not actually draw them
    def update(self):
        update_time = 1000 / 60  # 1000 ms / 60 FPS
        time_current = pygame.time.get_ticks()
        if time_current - self.last_tick > update_time:
            self.last_tick += update_time
            with thread_manager.screen_lock:
                self.current_window.update()


# Function will run until program is told to exit, drawing the screen
def run_master(master):
    while not master.done:
        with thread_manager.screen_lock:
            try:
                master.draw()
            except pygame.error:
                pass
        thread_manager.clock.tick(60)

    log("Master screen closed", 1)


# Template for window being displayed by the master window
class Subwindow:
    child_list = []  # All of the elements on the screen

    def __init__(self, master):
        self.screen = master.screen
        pass

    def update(self):
        for child in self.child_list:
            child.update()

    def draw(self):
        for child in self.child_list:
            child.draw()
        pygame.display.flip()

    # Register as a child of the Subwindow to be added to the update/draw list
    def register(self, child):
        priority = child.priority
        for idx, entry in enumerate(self.child_list):
            if entry.priority >= priority:
                self.child_list.insert(idx, child)
                return
        self.child_list.append(child)

    # Remove child element from the update/draw list
    def unregister(self, child):
        if child in self.child_list:
            self.child_list.remove(child)


# Template for elements on the screen
class ChildElement:
    priority = 127  # This can be overridden to change draw order, higher = on top

    def __init__(self, parent_window):
        self.parent = parent_window
        self.screen = parent_window.screen
        parent_window.register(self)

    def close(self):
        self.parent.unregister(self)

    def update(self):
        pass

    def draw(self):
        pass
