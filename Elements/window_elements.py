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


class MasterWindow:
    current_window = None
    previous_window = None

    def __init__(self):
        pygame.init()
        size = [config.res_width, config.res_height]
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

        self.done = False

        log("Master screen started", 2)
        self.update_thread = UpdateThread(self)
        self.update_thread.start()

    def set_window(self, window):
        self.current_window = window

    def kill_threads(self):
        log("Killing threads", 2)
        self.update_thread.kill()
        pygame.quit()
        self.done = True

    def draw(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.kill_threads()
            elif event.type == pygame.KEYDOWN:
                if event.key == K_q:
                    self.kill_threads()
            else:
                pass
        self.current_window.draw()

    def update(self):
        self.current_window.update()


def run_master(master):
    while not master.done:
        with thread_manager.screen_lock:
            try:
                master.draw()
            except pygame.error:
                pass
            thread_manager.clock.tick(60)

    log("Master screen closed", 1)


class Subwindow:
    child_list = []

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

    def register(self, child):
        priority = child.priority
        for idx, entry in enumerate(self.child_list):
            if entry.priority >= priority:
                self.child_list.insert(idx, child)
                return
        self.child_list.append(child)

    def unregister(self, child):
        if child in self.child_list:
            self.child_list.remove(child)


class ChildElement:
    priority = 127

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
