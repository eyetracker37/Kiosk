import quick_link
from logger import log
import threading
import config
from pygame import mouse


is_running = False
lock = threading.Lock()


class Cursor:
    def __init__(self):
        self.x_pos = 0
        self.y_pos = 0
        self.is_valid = False


class CursorHandler:
    def __init__(self):
        self.cursor = Cursor()

    def update(self):
        if config.use_tracker:
            frame = quick_link.get_frame()

            with lock:  # Make sure it isn't read while updating
                self.cursor.x_pos = int(config.screen_x * frame.x_pos / 100)
                self.cursor.y_pos = int(config.screen_y * frame.y_pos / 100)
                self.cursor.is_valid = frame.is_valid
        else:
            with lock:
                try:
                    self.cursor.x_pos, self.cursor.y_pos = mouse.get_pos()
                except:
                    pass
            self.cursor.is_valid = True

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
        with lock:  # Make sure it doesn't update while reading
            return self.cursor


cursor = CursorHandler()


class UpdateThread(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID

    def run(self):
        global is_running
        global cursor
        log("Starting update thread", 3)
        is_running = True
        while is_running:
            cursor.update()


update_thread = UpdateThread(1)


def initialize():
    if config.use_tracker:
        quick_link.initialize()
    update_thread.start()
    log("Update thread started", 2)


def get_cursor():
    return cursor.get_cursor()


def close():
    log("Closing update thread", 3)
    global is_running
    is_running = False
    update_thread.join()  # Join thread to wait until it closes
    log("Update thread closed", 2)
    if config.use_tracker:
        quick_link.stop_all()
