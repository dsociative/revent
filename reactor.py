# coding: utf8
from fields.rfield import rfield
from rmodel import RModel
from rmodel_store import RModelStore
from selector import Selector
from sorteddict import SortedDict
import time


def itime():
    return int(time.time())


class EventDB(RModel):

    type = rfield()
    params = rfield(eval)

    def set_data(self, event):
        self.type.set(event.type())
        self.params.set(str(event.params))


class EventQueueDB(RModelStore):

    assign = EventDB


class ReactorDB(RModelStore):

    prefix = 'reactor'
    root = True

    assign = EventQueueDB

    @property
    def event_models(self):
        for model in self.models():
            yield int(model.prefix), model.models()

    def dump(self, time, event):
        queue = self.get(time)
        if not queue:
            queue = self.set(time)

        event_db = queue.add()
        event_db.set_data(event)


class Reactor(object):

    def __init__(self, events, periodics=[], select=[]):
        self.selector = Selector(select)
        self.db = ReactorDB()
        self.mapper = dict(self.mapper_gen(events))

        self.periodics = periodics
        self.timeline = SortedDict()

        self.load()

    def time(self):
        return itime()

    def mapper_gen(self, events):
        for event in events:
            yield event.type(), event

    def __getitem__(self, name):
        return self.selector.get(name)

    def load(self):
        for time, event_queue in self.db.event_models:
            for event_db in event_queue:
                event = self.mapper.get(event_db.type.get())
                if event:
                    self.append(event(**event_db.params.get()), time=time)

    def flush(self):
        self.timeline.clear()
        self.selector.clear()

    def get(self, time):
        queue = self.timeline.get(time)
        if queue is None:
            queue = self.timeline[time] = []
        return queue

    def append(self, event, tdelta=None, time=None):
        time = time or self.time() + tdelta

        self.selector.process(event)
        self.get(time).append(event)
        self.db.dump(time, event)
        return time

    def wait_for_calc(self, time):
        done = False
        while self.timeline and not done:
            smallest_time, events = self.timeline.smallest_item()
            if smallest_time <= time:
                yield smallest_time, events
            else:
                done = True

    def remove_events(self, time):
        if time in self.timeline:
            del self.timeline[time]
        self.db.remove_item(time)

    def calc(self, time=None):
        time = time or self.time()

        for event in self.periodics:
            event.do(self, time)

        for expected_time, events in self.wait_for_calc(time):
            for event in events:
                event.do(self, time)
                self.selector.remove(event)
            self.remove_events(expected_time)


