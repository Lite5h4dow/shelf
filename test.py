import threading
import time

class StoppableThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

def funct():
    while not threading.current_thread().stopped():
        print("hello")

testthread = StoppableThread(target=funct)
testthread.start()
time.sleep(5)
testthread.stop()
