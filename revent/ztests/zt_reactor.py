# coding: utf8
from StringIO import StringIO
from unittest.case import TestCase
import sys

from redis import Redis

from revent.event import Event
from revent.reactor import Reactor, itime
from revent.sorteddict import SortedDict


class TEevent(Event):

    done = False

    def do(self, reactor, time):
        self.done = True
        return


class EventWithArgs(Event):

    def init(self, x, y):
        self.x = x
        self.y = y


class ErrorEvent(Event):

    def do(self, reactor, time):
        error


class ReactorTest(TestCase):

    def setUp(self):
        redis = Redis()
        redis.flushdb()
        self.reactor = Reactor(redis, [])

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

    def test_mapper_gen(self):
        mapper = dict(self.reactor.mapper_gen([EventWithArgs, TEevent]))
        self.assertEqual(mapper['EventWithArgs'], EventWithArgs)
        self.assertEqual(mapper['TEevent'], TEevent)

    def test_save_load(self):
        self.reactor.mapper['EventWithArgs'] = EventWithArgs
        event_time = itime() + 30
        event = EventWithArgs(x=10, y=15)
        self.reactor.append(event, 30)
        self.reactor.append(event, 30)

        event_db = self.reactor.db.get(event_time).get(1)
        self.assertEqual(event_db.type.get(), event.type())
        self.assertEqual(event_db.params.get(), event.params)

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

    def test_periodic(self):
        event = TEevent()
        self.assertEqual(event.done, False)
        reactor = Reactor(Redis(), [], [event])
        reactor.calc()
        self.assertEqual(event.done, True)

    def test_remove(self):
        reactor = Reactor(Redis(), [EventWithArgs], [], ['x'])
        event = EventWithArgs(x=1, y=2)
        reactor.append(event, 0)

        self.assertEqual(reactor['x'][1], [event])
        reactor.calc(itime() + 10)
        self.assertEqual(reactor['x'], {})

    def test_try_calc(self):
        sys.stderr = StringIO()
        event = ErrorEvent()
        self.reactor.append(event, time=1)
        self.reactor.try_calc()
        self.assertIn('Traceback', sys.stderr.getvalue())


