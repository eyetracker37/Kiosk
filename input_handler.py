import quick_link
from logger import log
import threading
import config


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
        frame = quick_link.get_frame()
        if frame.x_pos < 0:
            frame.x_pos = 0
        if frame.x_pos > 100:
            frame.x_pos = 100
        if frame.y_pos < 0:
            frame.y_pos = 0
        if frame.y_pos > 100:
            frame.y_pos = 100

        with lock:
            self.cursor.x_pos = config.screen_x * frame.x_pos / 100
            self.cursor.y_pos = config.screen_y * frame.y_pos / 100
            self.cursor.is_valid = frame.is_valid

    def get_cursor(self):
        with lock:
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
    quick_link.initialize()
    update_thread.start()
    log("Update thread started", 2)


def get_cursor():
    return cursor.get_cursor()


def close():
    log("Closing update thread", 3)
    global is_running
    is_running = False
    update_thread.join()
    log("Update thread closed", 2)
    quick_link.stop_all()
