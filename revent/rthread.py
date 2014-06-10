# coding: utf8

import threading
import time


class RThread(threading.Thread):

    def __init__(self, reactor):
        super(RThread, self).__init__()
        self.reactor = reactor
        self.status = True

    def run(self):
        while self.status:
            time.sleep(1)
            self.reactor.calc()

    def stop(self):
        self.status = False

