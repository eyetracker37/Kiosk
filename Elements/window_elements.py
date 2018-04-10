from Utils.logger import log
import pygame
import sys
from pygame.locals import *
from Utils import thread_manager
import threading
from Utils import config
from Input import input_handler


class UpdateThread(threading.Thread):
    def __init__(self, creator):
        self.is_running = False
        threading.Thread.__init__(self)
        self.threadID = thread_manager.get_thread_id()
        self.creator = creator

    def kill(self):
        thread_manager.running = False

    def run(self):
        log("Starting screen update thread", 2)
        while thread_manager.running:
                try:
                    self.creator.update()
                except AttributeError:
                    pass


class HierarchyObject:
    priority = 127

    def __init__(self, parent):
        self.parent = parent
        self.parent.register(self)
        self.master = parent.get_master()
        assert isinstance(self.master, WindowManager)
        self.window = parent.get_window()
        self.screen = self.master.screen
        self.child_list = []  # All of the elements on the screen

    def get_master(self):
        return self.master

    def get_window(self):
        return self.window

    def get_cursor(self):
        return self.master.get_cursor()

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

    def close(self):
        for child in self.child_list:
            child.close()
        self.parent.unregister(self)

    def update(self):
        for child in self.child_list:
            child.update()

    def draw(self):
        for child in self.child_list:
            child.draw()


# Master window handler, responsible for managing the screen
class WindowManager:
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
        if size[0] > got_resolution_x or size[1] > got_resolution_y:
            log("Screen resolution [" + str(got_resolution_x) + ", " + str(got_resolution_y) +
                "] too small to fit requested resolution " + str(size) + ", exiting", 0)
            self.kill_threads()
            sys.exit()

        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        log("Master screen started", 2)

        self.cursor = input_handler.CursorHandler(self)

        # Creates and starts the update thread
        self.update_thread = UpdateThread(self)
        self.update_thread.start()
        self.last_tick = pygame.time.get_ticks()

    # Set which window is being displayed
    def register(self, window):
        if self.current_window is not None:
            self.current_window.close()
        log("Changed active window to " + str(window), 3)
        self.current_window = window

    def unregister(self, window):
        pass

    def get_cursor(self):
        return self.cursor.get_cursor()

    # Kill update thread
    def kill_threads(self):
        log("Killing threads", 2)
        try:
            self.update_thread.kill()
        except AttributeError:
            pass
        pygame.quit()
        thread_manager.running = False

    # Draws the elements on the screen
    def draw(self):

        # Handling for keyboard presses has to be in draw task, since it can't be in a thread
        # and must instead be in the master task
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                log("Received quit signal", 2)
                self.kill_threads()
            elif event.type == pygame.KEYDOWN:
                if event.key == K_q:
                    log("Q pressed", 2)
                    self.kill_threads()
            else:
                pass
        self.current_window.draw()
        pygame.display.flip()

    # Updates the elements on the screen, but does not actually draw them
    def update(self):
        update_time = 1000 / 60  # 1000 ms / 60 FPS
        time_current = pygame.time.get_ticks()
        if time_current - self.last_tick > update_time:
            self.last_tick += update_time
            with thread_manager.screen_lock:
                self.current_window.update()

    def get_master(self):
        return self

    def get_window(self):
        return self.current_window


# Function will run until program is told to exit, drawing the screen
def run_master(master):
    while thread_manager.running:
        with thread_manager.screen_lock:
            try:
                master.draw()
            except pygame.error:
                pass
        thread_manager.clock.tick(60)

    log("Master screen closed", 1)
