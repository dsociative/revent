# coding: utf8


class Event(object):

    def __init__(self, **kw):
        self.params = kw
        self.init(**kw)


    def init(self, **kw):
        ''' override '''

    def do(self, reactor, time):
        ''' override '''
