from ..messageHandler import MessageHandler
from configResponse import Send, Done, AskChild, AskCacheKey, AskAPIKey, NoChild, CreateException
from data.cache import Cache
from exceptions import FilterException

import hashlib


class AbstractVote (MessageHandler):
    def __init__(self, key, children):
        super(AbstractVote, self).__init__(children)
        self.key = key

    def do_count(self, count):
        raise Exception('Not implemented')

    def get_votes(self, msg):
        hash = str(hashlib.md5(msg.text.encode()).hexdigest())

        out = Cache.get([self.key, hash])
        if not out:
            out = (0, [])
        return (hash, out)

    def apply_vote(self, msg):
        key, (val, users) = self.get_votes(msg)
        new_val = self.do_count(val)

        if msg.from_user.id in users:
            return (False, val)
        else:
            users.append(msg.from_user.id)
            Cache.put([self.key, key], (new_val, users))
            return (True, new_val)

    def call(self, bot, msg, target, exclude):
        if not msg.text:
            raise Exception('You cannot vote on an empty message')
        res, val = self.apply_vote(msg)
        if res:
            msg.text = str(val)
            return self.propagate(bot, msg, target, exclude)
        else:
            raise FilterException()

    def has_effect():
        return True

    @classmethod
    def is_entrypoint(cls):
        return False

    def _to_dict(self):
        return {'key': self.key}

    @classmethod
    def create(cls, stage, data, arg):
        if stage is 0:
            return (1, None, AskCacheKey(default={}))
        elif stage is 1 and arg:
            return (2, (arg, []), AskChild())
        elif stage is 2 and arg:
            if isinstance(arg, MessageHandler):
                data[1].append(arg)
                return (2, data, AskChild())
            else:
                key, children = data
                return (-1, None, Done(cls._from_dict({'key': key}, children)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for Vote')


class UpVote (AbstractVote):
    def __init__(self, key, children):
        super(UpVote, self).__init__(key, children)

    def do_count(self, count):
        return count + 1

    @classmethod
    def get_name(cls):
        return "Upvote message"

    @classmethod
    def _from_dict(cls, dict, children):
        return UpVote(dict['key'], children)


class DownVote (AbstractVote):
    def __init__(self, key, children):
        super(DownVote, self).__init__(key, children)

    def do_count(self, count):
        return count - 1

    @classmethod
    def get_name(cls):
        return "Downvote message"

    @classmethod
    def _from_dict(cls, dict, children):
        return UpVote(dict['key'], children)


class GetVote (AbstractVote):
    def __init__(self, key, children):
        super(GetVote, self).__init__(key, children)

    @classmethod
    def get_name(cls):
        return "Get number of votes"

    @classmethod
    def _from_dict(cls, dict, children):
        return GetVote(dict['key'], children)

    def call(self, bot, msg, target, exclude):
        key, (val, users) = self.get_votes(msg)
        msg.text = str(val)
        return self.propagate(bot, msg, target, exclude)

    @classmethod
    def is_entrypoint(cls):
        return True
