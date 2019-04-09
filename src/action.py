import random


class Action (object):
    def __init__(self):
        self.ids = []
        self.vals = {}

    def append_ids(self, ids, include=None, exclude=None, load_action=None):
        if not include:
            include = ids
        if not exclude:
            exclude = []

        selected = list(filter(lambda id: (id in include) and (id not in exclude), ids))
        if load_action:
            n = 0
            for id in selected:
                val = load_action(id)
                if val:
                    self.vals[id] = val
                    self.ids.append(id)
                    n += 1
            return n
        else:
            self.ids.extend(selected)
            return len(selected)

    def select_random_id(self, exclude=[]):
        if len(self.ids) is 1:
            return self.ids[0]

        if len(exclude) is len(self.ids):
            exclude = []

        while True:
            rand = random.randrange(len(self.ids))
            id = self.ids[rand]
            if id not in exclude:
                 return id

    def trigger(self, bot, message, exclude=[], reply=False):
        raise Exception('Not implemented')

    def __len__(self):
        return len(self.ids)
