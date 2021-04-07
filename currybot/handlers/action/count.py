import hashlib
import re

from currybot.configResponse import Done, AskChild, AskCacheKey, CreateException, Send
from currybot.data.cache import Cache
from currybot.exceptions import FilterException
from currybot.handlers.messageHandler import MessageHandler


# Abstract base class for the counting actions
class AbstractCount(MessageHandler):
    def __init__(self, key, children):
        super(AbstractCount, self).__init__(children)
        self.key = key

    # The function that distinguishes between the different subclasses
    def do_count(self, count):
        raise Exception('Not implemented')

    # Getter for the current count
    def get_count(self):
        out = int(Cache.get(self.key))
        if not out:
            return 0
        return out

    # When called, we get the count, apply the modifier and return the result
    def call(self, bot, msg, target, exclude):
        val = self.get_count()
        new_val = self.do_count(val)
        Cache.put(self.key, new_val)

        msg.text = msg.text.replace('%d', str(val)) if msg.text and '%d' in msg.text else str(val)
        return self.propagate(bot, msg, target, exclude)

    def has_effect(self):
        return True

    @classmethod
    def is_entrypoint(cls):
        return False

    def _to_dict(self):
        return {'key': self.key}

    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            return (1, None, AskCacheKey(default={}))
        elif stage == 1 and arg:
            return (2, (arg, []), AskChild())
        elif stage == 2 and arg:
            if isinstance(arg, MessageHandler):
                data[1].append(arg)
                return (2, data, AskChild())
            else:
                key, children = data
                return (-1, None, Done(cls._from_dict({'key': key}, children)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for Count')


# Action that increments a counter
class Increment(AbstractCount):
    # Do the increment
    def do_count(self, count):
        return count + 1

    @classmethod
    def get_name(cls):
        return "Increment counter"

    @classmethod
    def _from_dict(cls, dict, children):
        return Increment(dict['key'], children)


# Action for decrementing a counter
class Decrement(AbstractCount):
    # Decrement the count
    def do_count(self, count):
        return count - 1

    @classmethod
    def get_name(cls):
        return "Decrement counter"

    @classmethod
    def _from_dict(cls, dict, children):
        return Decrement(dict['key'], children)


# Action to set the count
class SetCount(AbstractCount):
    def __init__(self, key, count, children):
        super(SetCount, self).__init__(key, children)
        self.count = count

    # We do not use the current value, but overwrite it with the stored one
    def do_count(self, count):
        return self.count

    @classmethod
    def get_name(cls):
        return "Set the value of a counter"

    @classmethod
    def _from_dict(cls, dict, children):
        return SetCount(dict['key'], dict['count'], children)

    def _to_dict(self):
        return {'key': self.key, 'count': self.count}

    # This action does not use the common create function
    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            return (1, None, AskCacheKey(default={}))
        elif stage == 1 and arg:
            return (2, arg, Send('Which value should the counter be updated to?'))
        elif stage == 2 and arg:
            if arg.text and re.match(r'-?[\d]+', arg.text):
                return (3, (data, int(arg.text), []), AskChild())
            else:
                return (2, arg, Send('That is not a valid number of votes'))
        elif stage == 3 and arg:
            if isinstance(arg, MessageHandler):
                data[2].append(arg)
                return (3, data, AskChild())
            else:
                key, count, children = data
                return (-1, None, Done(SetCount(key, count, children)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for Count')


# Action to get the number of votes
class GetCount(AbstractCount):
    @classmethod
    def get_name(cls):
        return "Get counter value"

    @classmethod
    def _from_dict(cls, dict, children):
        return GetCount(dict['key'], children)

    # To get the current number, we do not have to change this value
    def do_count(self, count):
        return count

    @classmethod
    def is_entrypoint(cls):
        return True
