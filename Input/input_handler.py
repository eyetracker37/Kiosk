try:
    from Input import quick_link
except OSError:
    from Input import fake_quick_link as quick_link
from Utils.logger import log
import threading
from Utils import config
import pygame
from pygame import mouse
from Utils import thread_manager
from Elements import window_elements
import time
from Pages import welcome


# Position of the gaze/mouse on the screen
class Cursor:
    def __init__(self):
        self.x_pos = 0
        self.y_pos = 0
        self.is_valid = False


class CursorHandler:
    TIMEOUT = 7

    def __init__(self, master):
        assert isinstance(master, window_elements.WindowManager)
        self.master = master

        self.cursor = Cursor()

        self.is_running = False
        self.update_thread = UpdateThread(master, self, thread_manager.get_thread_id())
        self.update_thread.start()
        self.last_valid = time.time()
        log("Input update thread started", 2)

    def update(self):
        # If getting data from the eye tracker
        if self.is_running:
            if config.use_tracker:
                frame = quick_link.get_frame()

                with thread_manager.input_lock:  # Make sure it isn't read while updating
                    try:
                        self.cursor.x_pos = int(config.screen_x * frame.x_pos / 100)
                        self.cursor.y_pos = int(config.screen_y * frame.y_pos / 100)
                        self.cursor.is_valid = frame.is_valid
                    except AttributeError:
                        log("Attempted to get cursor data from NoneType Frame", 1)
                        self.cursor.is_valid = False
            else:  # Otherwise use keyboard
                with thread_manager.input_lock:
                    try:
                        self.cursor.x_pos, self.cursor.y_pos = mouse.get_pos()
                    except pygame.error:
                        pass
                self.cursor.is_valid = True

            current_time = time.time()
            if self.cursor.is_valid:
                self.last_valid = current_time
            else:
                if current_time - self.last_valid > self.TIMEOUT and self.is_running:
                    log("Eye tracker resetting due to lack of activity", 1)
                    self.reset()

            # Handle bounds of screen
            if self.cursor.x_pos < 0:
                self.cursor.x_pos = 0
            if self.cursor.x_pos > config.screen_x:
                self.cursor.x_pos = config.screen_x
            if self.cursor.y_pos < 0:
                self.cursor.y_pos = 0
            if self .cursor.y_pos > config.screen_y:
                self.cursor.y_pos = config.screen_y

    def get_cursor(self):
        with thread_manager.input_lock:  # Make sure it doesn't update while reading
            return self.cursor

    def reset(self):
        log("Resetting eye tracker", 1)
        self.is_running = False
        if config.use_tracker:
            quick_link.stop_all()
        welcome.run(self.master)

    def start(self):
        log("Starting eye tracker", 1)
        if config.use_tracker:
            quick_link.initialize()
        log("Got tracking", 2)
        self.last_valid = time.time()
        self.is_running = True

    # Stop getting cursor position
    def close(self):
        log("Closing update thread", 3)
        self.update_thread.join()  # Join thread to wait until it closes
        log("Update thread closed", 2)
        if config.use_tracker:
            quick_link.stop_all()


# Thread that gets the cursor position
class UpdateThread(threading.Thread):
    def __init__(self, window, cursor, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.cursor = cursor

        assert isinstance(window, window_elements.WindowManager)
        self.window = window

    def run(self):
        log("Starting update thread", 3)
        while thread_manager.running:
            self.cursor.update()
            thread_manager.clock.tick(60)
