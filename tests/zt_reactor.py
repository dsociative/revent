# coding: utf8
from event import Event
from reactor import Reactor, itime
from sorteddict import SortedDict
from unittest.case import TestCase
import time


class TEevent(Event):

    done = False

    type = 'tevent'

    def do(self, reactor, time):
        self.done = True
        return

class EventWithArgs(Event):

    type = 'event_with_args'

    def init(self, x, y):
        self.x = x
        self.y = y


class ReactorTest(TestCase):

    def setUp(self):
        self.reactor = Reactor()
        self.reactor.db.remove()

    def test_(self):
        self.assertEqual(self.reactor.get(itime()), [])
        event = TEevent()
        self.reactor.append(event, 30)

        event_time = itime() + 30
        self.assertEqual(self.reactor.get(event_time), [event])

        self.reactor.calc(event_time)
        self.assertEqual(self.reactor.get(event_time), [])
        self.assertEqual(event.done, True)

    def test_calc_with_previous(self):
        event = TEevent()

        event_time = itime() + 30
        event_time2 = itime() + 20
        self.reactor.append(event, 30)
        self.reactor.append(event, 20)

        self.reactor.calc(event_time)

        self.assertEqual(self.reactor.timeline, {})
        self.assertEqual(self.reactor.get(event_time), [])
        self.assertEqual(self.reactor.get(event_time2), [])

    def test_save_load(self):
        self.reactor.mapper['event_with_args'] = EventWithArgs
        event_time = itime() + 30
        event = EventWithArgs(x=10, y=15)
        self.reactor.append(event, 30)
        self.reactor.append(event, 30)

        event_db = self.reactor.db.get(event_time).get(1)
        self.assertEqual(event_db.type, event.type)
        self.assertEqual(event_db.params, event.params)

        self.reactor.timeline = SortedDict()
        self.reactor.load()

        event, event2 = self.reactor.get(event_time)
        self.assertIsInstance(event, EventWithArgs)
        self.assertEqual(event.x, 10)
        self.assertEqual(event.y, 15)

        self.assertIsInstance(event2, EventWithArgs)
        self.assertEqual(event2.x, 10)
        self.assertEqual(event2.y, 15)

        self.reactor.calc(event_time)

        self.assertEqual(self.reactor.db.get(event_time), None)


