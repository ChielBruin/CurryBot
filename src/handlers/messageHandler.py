import random, string, copy
import inspect, sys

from telegram import Message, Chat

from exceptions import FilterException
from configResponse import CreateException
from data import Cache

class Handler (object):
    def __init__(self, children=[]):
        if isinstance(children, list):
            self.children = children
        else:
            self.children = [children]

    def extend_children(self, new_children):
        if not isinstance(new_children, list):
            new_children = [new_children]

        self.children.extend(new_children)
        self.on_children_update(new_children)

    def update(self):
        self.on_update()
        for child in self.children:
            child.update()

    def propagate(self, bot, message, target, exclude):
        res = []
        do_copy = len(self.children) > 1
        for child in self.children:
            res.extend(child.call(bot, message, target, copy.copy(exclude) if do_copy else exclude))
        return res

    def on_children_update(self, children):
        pass

    def on_update(self):
        pass

    def has_effect():
        if len(self.children) > 0:
            for child in self.children:
                if child.has_effect():
                    return True
            return False
        else:
            return False

    @classmethod
    def class_from_dict(cls, dict):
        class_name = dict['name']
        return [c for (name, c) in inspect.getmembers(sys.modules['handlers'], inspect.isclass) if name == class_name][0]

    @classmethod
    def from_dict(cls, dict):
        return cls._from_dict(dict, [cls.class_from_dict(child).from_dict(child) for child in dict['children']])

    def to_dict(self):
        dict = self._to_dict()
        dict['children'] = [d.to_dict() for d in self.children]
        dict['name'] = type(self).__name__
        return dict

    @classmethod
    def is_entrypoint(cls):
        raise Exception('is_entrypoint not implemented for %s' % cls)

    @classmethod
    def is_private(cls):
        '''
        Some handlers should not be copied to other chats, as this will expose their API keys.
        These handlers should return True.
        '''
        return False

    @classmethod
    def get_name(cls):
        raise Exception('get_name not implemented for %s' % cls)

    @classmethod
    def _from_dict(cls, dict, children):
        raise Exception('_from_dict not implemented for %s' % cls)

    def _to_dict(self):
        raise Exception('_to_dict not implemented for %s' % self)

    @classmethod
    def create(cls, stage, data, arg):
        raise CreateException('create not implemented for %s' % cls)

    @classmethod
    def create_api(cls, stage, data, arg):
        raise CreateException('create_api not implemented for %s' % cls)

class MessageHandler (Handler):
    def call(self, bot, message, target):
        raise Exception('Filter not implemented')

class RandomMessageHandler (MessageHandler):
    from data import Cache

    def __init__(self, id, children, do_cache=False):
        super(RandomMessageHandler, self).__init__(children)
        self._id = id
        Cache.config_entry(id, do_cache)

    @staticmethod
    def get_random_id(length=8):
        letters = string.ascii_lowercase + string.ascii_uppercase
        return '$' + ''.join(random.choice(letters) for i in range(length-1))

    def clear(self):
        Cache.clear(self._id)

    def add_options(self, options, get_value=None, include=None, exclude=[]):
        if isinstance(options, list):
            self._add_options(options, get_value, include, exclude)
        else:
            self._add_options([options], get_value, include, exclude)

    def _add_options(self, options, get_value, include, exclude):
        """
        options == [(k, v)] -> direct key value store
        options == [v] && get_value == None -> store values indexed
        options == [x] && get_value == lambda(x) -> store result of lambda indexed
        """

        # If no include filter is given, make sure the include filter contains all keys
        if not include:
            include = []
            for option in options:
                if isinstance(option, tuple):
                    (key, _) = option
                    include.append(key)
                else:
                    include.append(option)

        for idx, option in enumerate(options):
            idx = '%s_%d' % (self._id, idx)
            if isinstance(option, tuple):
                (key, val) = option
                if key not in include or key in include:
                    continue
                Cache.put([self._id, key], val)
            else:
                if option not in include or option in exclude:
                    continue
                if get_value is None:
                    Cache.put([self._id, idx], option)
                else:
                    # Make sure that we only apply the load action when it is not in the cache yet.
                    # This because the load action might be very expensive
                    if not Cache.contains([self._id, idx]):
                        Cache.put([self._id, idx], get_value(option))

    def select_random_option(self, exclude=[]):
        id = self._select_random_id(exclude)
        val = Cache.get([self._id, id])

        return (id, val)

    def _select_random_id(self, exclude):
        '''
        Select a random id excluding the ones in `exclude`.
        '''
        options = Cache.get(self._id)
        size = len(options)
        if size is 1:
            return next(iter(options))

        if len(exclude) is size:
            exclude = []

        keys = list(options.keys())
        while True:
            rand = random.randrange(size)
            id = keys[rand]
            if id not in exclude:
                 return id
