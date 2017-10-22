from threading import Lock

thread_id = 0

input_lock = Lock()


def get_thread_id():
    global thread_id
    thread_id += 1
    return thread_id
