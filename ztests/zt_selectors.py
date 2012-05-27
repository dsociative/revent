# coding: utf8

from event import Event
from selector import Selector
from unittest.case import TestCase


class TEvent1(Event):

    def init(self, **kw):
        self.kw = kw


class TEvent2(TEvent1):

    pass


class SelectorsTest(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.selector = Selector([])

    def test_entry(self):
        selector = Selector(['uid', 'pid'])
        self.assertEqual(list(selector.entry({'ol': 3, 'uid': 3})),
                         [('uid', 3)])
        self.assertEqual(list(selector.entry({'pid': 's', 'uid': 3})),
                         [('uid', 3), ('pid', 's')])
        self.assertEqual(list(selector.entry({'id': 's'})), [])

    def test_has_entry(self):
        selector = Selector(['uid', 'pid'])
        self.assertTrue(selector.has_entry({'uid': 1}))
        self.assertTrue(selector.has_entry({'uid': 1, 'pid': 2}))
        self.assertTrue(selector.has_entry({'pid': 2}))
        self.assertFalse(selector.has_entry({'id': 2}))

    def test_build(self):
        self.assertEqual(self.selector.get('uid'), {})
        events = [TEvent1(uid='1'), TEvent1(uid='2'), TEvent1(other_kw=True)]

        for e in events:
            self.selector.process(e)

        self.assertEqual(self.selector.get('uid'), {})

        self.selector = Selector(['uid'])
        for e in events:
            self.selector.process(e)

        self.assertTrue(events[0] in self.selector.events)
        self.assertTrue(events[1] in self.selector.events)
        self.assertEqual(self.selector.get('uid'), {'1': [events[0]],
                                                    '2': [events[1]]})

        self.selector.remove(events[0])
        self.assertEqual(self.selector.events, [events[1]])
        self.assertEqual(self.selector.get('uid'), {'2': [events[1]]})

    def test_select_list(self):
        selector = Selector(['uid', 'pid'])
        events = [TEvent1(uid='1'), TEvent1(uid='2'), TEvent2(uid='1')]
        for e in events:
            selector.process(e)

        select_list = selector.get('uid')
        self.assertEqual(select_list['1'], [events[0], events[2]])
        self.assertEqual(select_list['1']['TEvent1'], [events[0]])
        self.assertEqual(select_list['1']['TEvent2'], [events[2]])
        self.assertEqual(select_list['1'][0:1], [events[0]])
