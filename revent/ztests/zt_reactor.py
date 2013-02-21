# coding: utf8
from StringIO import StringIO
import logging
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
        raise Exception('error')



class ReactorTest(TestCase):

    def setUp(self):
        redis = Redis()
        redis.flushdb()
        self.reactor = Reactor(redis, [])
        self.errors = StringIO()
        self.reactor.logger.addHandler(logging.StreamHandler(self.errors))


    def test_append(self):
        self.assertEqual(self.reactor.get(itime()), [])
        event = TEevent()
        self.reactor.append(event, 30)

        event_time = itime() + 30
        self.assertEqual(self.reactor.get(event_time), [event])
        self.assertEqual(self.reactor.db.get(event_time).data(),
                         {'1': {'params': {}, 'type': 'TEevent'}})

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

        queue = self.reactor.db.get(event_time)
        event_db = queue.get(1)
        self.assertEqual(event_db.type.get(), event.type())
        self.assertEqual(event_db.params.get(), event.params)
        self.assertEqual(len(queue), 2)

        self.reactor.timeline = SortedDict()
        self.reactor.load()

        event, event2 = self.reactor.get(event_time)
        self.assertIsInstance(event, EventWithArgs)
        self.assertEqual(event.x, 10)
        self.assertEqual(event.y, 15)

        self.assertIsInstance(event2, EventWithArgs)
        self.assertEqual(event2.x, 10)
        self.assertEqual(event2.y, 15)
        self.assertEqual(len(queue), 2)

        self.reactor.calc(event_time)
        self.assertEqual(queue.get(event_time), None)

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
        time = self.reactor.time()
        event = ErrorEvent()
        self.reactor.append(event, time=1)
        self.reactor.calc()
        self.assertIn(
            '<ErrorEvent:{}> executing at %s' % time,
            self.errors.getvalue()
        )

    def test_execute(self):
        event = ErrorEvent()
        self.reactor.execute(event, time=500)
        self.assertIn(
            '<ErrorEvent:{}> executing at 500',
            self.errors.getvalue()
        )
