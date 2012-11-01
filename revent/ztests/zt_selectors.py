# coding: utf8

from revent.event import Event
from revent.selector import Selector, SelectList
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

        self.selector = Selector(['uid', 'pid'])
        self.events = [TEvent1(uid='1'), TEvent1(uid='2'), TEvent2(uid='1')]
        for e in self.events:
            self.selector.process(e)

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
        selector = Selector([])
        self.assertEqual(selector.get('uid'), {})
        events = [TEvent1(uid='1'), TEvent1(uid='2'), TEvent1(other_kw=True)]

        for e in events:
            self.selector.process(e)

        self.assertEqual(selector.get('uid'), {})

        selector = Selector(['uid'])
        for e in events:
            selector.process(e)

        self.assertTrue(events[0] in selector.events)
        self.assertTrue(events[1] in selector.events)
        self.assertEqual(selector.get('uid'), {'1': [events[0]],
                                               '2': [events[1]]})

        selector.remove(events[0])
        self.assertEqual(selector.events, [events[1]])
        self.assertEqual(selector.get('uid'), {'2': [events[1]]})

    def test_select_list(self):
        select_list = self.selector.get('uid')
        self.assertEqual(select_list['1'], [self.events[0], self.events[2]])
        self.assertEqual(select_list['1']['TEvent1'], [self.events[0]])
        self.assertEqual(select_list['1']['TEvent2'], [self.events[2]])
        self.assertEqual(select_list['1'][0:1], [self.events[0]])

    def test_clear(self):
        self.selector.clear()
        self.assertEqual(self.selector.events, [])
        self.assertEqual(self.selector.get('uid'), {})


class SelectListTest(TestCase):

    def test_append(self):
        event = TEvent1(uid='1')
        slist = SelectList()
        slist.append(event)
        self.assertEqual(slist['TEvent1'], [event])
