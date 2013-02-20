# coding: utf8


class Event(object):

    def __init__(self, **kw):
        self.params = kw
        self.init(**kw)

    @classmethod
    def type(cls):
        return cls.__name__

    def init(self, **kw):
        ''' override '''

    def do(self, reactor, time):
        ''' override '''

    def __repr__(self):
        return '<%s:%s>' % (self.type(), self.params)