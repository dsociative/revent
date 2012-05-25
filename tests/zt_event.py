# coding: utf8

from event import Event
from unittest.case import TestCase


class TEvent(Event):

    def init(self, x, v, y):
        self.x = x
        self.v = v
        self.y = y


class EventTest(TestCase):

    def test_params(self):

        event = TEvent(x=10, v=31, y=44)
        self.assertEqual(event.params, {'x':10, 'v':31, 'y':44})
        self.assertEqual(event.x, 10)
        self.assertEqual(event.v, 31)
        self.assertEqual(event.y, 44)
