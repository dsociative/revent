# coding: utf8

import threading


class RThread(threading.Thread):

    def __init__(self, reactor):
        super(RThread, self).__init__()
        self.reactor = reactor
        self.status = True

    def run(self):
        while self.status:
            self.reactor.calc()

    def stop(self):
        self.status = False

