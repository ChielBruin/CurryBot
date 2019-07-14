from cache import Cache
from logger import Logger

import random


class Action (object):

    '''
    Base class of Actions.
    '''
    def __init__(self, id):
        self._options = {}
        self.id = id

    def update(self):
        pass

    def clear_ids(self):
        self._options.clear()

    def append_ids_indexed(self, vals, include=None, exclude=None, cache=False):
        dict = {}
        for id, message in enumerate(vals):
            dict[id] = message
        self.append_ids(dict, include, exclude, cache=cache)

    def load_and_append_ids(self, ids, load_action, include=None, exclude=None, cache=False):
        if not include:
            include = ids
        if not exclude:
            exclude = []

        for id in ids:
            if id not in include or id in exclude:
                continue

            if cache:
                val = Cache.action_get_cache(self.id, id)
                if val is None:
                    Logger.log_debug('id \'%s\' not found in the cache' % id)
            else:
                val = None

            if val is None:
                val = load_action(id)

            self._options["%s_%s" % (self.id, id)] = val
            if cache:
                Cache.action_put_cache(self.id, id, val)

    def append_ids(self, vals, include=None, exclude=None, cache=False):
        '''
        Append the given ids to the stored ids of this action.
        Using `include` and `exclude`, filters can be applied.
        '''
        self.load_and_append_ids(vals.keys(), lambda x: vals[x], include, exclude, cache=cache)

    def select_random_option(self, exclude=[]):
        id = self._select_random_id(exclude)
        val = self._options[id]

        return (id, val)

    def _select_random_id(self, exclude):
        '''
        Select a random id excluding the ones in `exclude`.
        '''
        size = len(self._options)
        if size is 1:
            return next(iter(self._options))

        if len(exclude) is size:
            exclude = []

        keys = list(self._options.keys())
        while True:
            rand = random.randrange(size)
            id = keys[rand]
            if id not in exclude:
                 return id

    def dispatch(self, bot, msg, exclude):
        '''
        Returns the `id` of the action performed.
        '''
        raise Exception('Not implemented')

    def dispatch_reply(self, bot, msg, reply_to, exclude):
        '''
        Returns the `id` of the action performed.
        '''
        raise Exception('Not implemented')
