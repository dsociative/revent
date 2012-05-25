# coding: utf8

import pyev
import threading
from signal import SIGINT


class TickerThread(threading.Thread):
    ''' Нить с тикалкой '''

    def __init__(self, func):
        super(TickerThread, self).__init__()
        self.func = func
        self.loop = pyev.default_loop()

    def run(self):
        def stopper_cb(watcher, events):
            watcher.loop.stop()

        def timer_cb(watcher, events):
            self.func()

        timer = pyev.Timer(0, 1, self.loop, timer_cb, 0)
        timer.start()
        sig = pyev.Signal(SIGINT, self.loop, stopper_cb)
        sig.start()

        self.loop.start()

    def stop(self):
        self.loop.stop(pyev.EVBREAK_ALL)

