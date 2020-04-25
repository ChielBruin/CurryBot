import hashlib
import re

from currybot.configResponse import Done, AskChild, AskCacheKey, CreateException, Send
from currybot.data.cache import Cache
from currybot.exceptions import FilterException
from currybot.handlers.messageHandler import MessageHandler


class AbstractVote(MessageHandler):
    def __init__(self, key, children, multivote=False):
        super(AbstractVote, self).__init__(children)
        self.key = key
        self.multivote = multivote

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
            if self.multivote:
                return (True, new_val)
            else:
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

    def has_effect(self):
        return True

    @classmethod
    def is_entrypoint(cls):
        return False

    def _to_dict(self):
        return {'key': self.key, 'multivote': self.multivote}

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
            raise CreateException('Invalid create state for Vote')


class UpVote(AbstractVote):
    def do_count(self, count):
        return count + 1

    @classmethod
    def get_name(cls):
        return "Upvote message"

    @classmethod
    def _from_dict(cls, dict, children):
        return UpVote(dict['key'], children, dict['multivote'])


class DownVote(AbstractVote):
    def do_count(self, count):
        return count - 1

    @classmethod
    def get_name(cls):
        return "Downvote message"

    @classmethod
    def _from_dict(cls, dict, children):
        return UpVote(dict['key'], children, dict['multivote'])


class SetVote(AbstractVote):
    def __init__(self, key, votes, children):
        super(SetVote, self).__init__(key, children)
        self.votes = votes

    def do_count(self, count):
        return self.votes

    @classmethod
    def get_name(cls):
        return "Set the number of votes"

    @classmethod
    def _from_dict(cls, dict, children):
        return UpVote(dict['key'], dict['votes'], children)

    def _to_dict(self):
        return {'key': self.key, 'votes': self.votes}

    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            return (1, None, AskCacheKey(default={}))
        elif stage == 1 and arg:
            return (2, arg, Send('Which value should the votes be updated to?'))
        elif stage == 2 and arg:
            if arg.text and re.match(r'-?[\d]+', arg.text):
                return (3, (arg, int(arg.text), []), AskChild())
            else:
                return (2, arg, Send('That is not a valid number of votes'))
        elif stage == 3 and arg:
            if isinstance(arg, MessageHandler):
                data[2].append(arg)
                return (3, data, AskChild())
            else:
                key, votes, children = data
                return (-1, None, Done(SetVote(key, votes, children)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for Vote')


class GetVote(AbstractVote):
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
