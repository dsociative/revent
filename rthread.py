# coding: utf8

from reactor import Reactor
from signal import SIGINT
import pyev
import threading


class RThread(threading.Thread):

    def __init__(self, events, periodics):
        super(RThread, self).__init__()
        self.loop = pyev.default_loop()
        self.reactor = Reactor(events, periodics)

    def run(self):
        def stopper_cb(watcher, events):
            watcher.loop.stop()

        def timer_cb(watcher, events):
            self.reactor.calc()

        timer = pyev.Timer(0, 1, self.loop, timer_cb, 0)
        timer.start()
        sig = pyev.Signal(SIGINT, self.loop, stopper_cb)
        sig.start()

        self.loop.start()

    def stop(self):
        self.loop.stop(pyev.EVBREAK_ALL)

