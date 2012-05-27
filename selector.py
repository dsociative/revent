# coding: utf8

from collections import defaultdict


class SelectList(list):

    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)
        self.mapper = defaultdict(list)

    def append(self, item):
        self.mapper[item.type].append(item)
        return list.append(self, item)

    def __getitem__(self, name):
        if type(name) is str:
            return self.mapper.get(name, [])
        else:
            return list.__getitem__(self, name)


class Selector(object):

    def __init__(self, keywords):
        self.keywords = keywords
        self.store = defaultdict(dict)
        self.events = []

    def get(self, name):
        return self.store.get(name, {})

    def remove(self, event):
        if event in self.events:
            self.events.remove(event)
            self.build()

    def has_entry(self, params):
        for key in self.keywords:
            if key in params:
                return True

    def entry(self, kw):
        for key in self.keywords:
            value = kw.get(key)
            if value:
                yield key, value

    def process(self, event):
        if self.has_entry(event.params):
            self.events.append(event)

        self.build()

    def build(self):
        rt = defaultdict(dict)

        for event in self.events:
            for key, value in self.entry(event.params):
                rt[key].setdefault(value, SelectList()).append(event)

        self.store = rt

