from datetime import datetime, timedelta
import re
from telegram import InlineKeyboardButton

from data import Cache
from ..messageHandler import MessageHandler
from exceptions     import FilterException

from configResponse import Send, Done, AskChild, AskCacheKey, NoChild, CreateException


class ActivityFilter (MessageHandler):
    def __init__(self, id, is_user, cache_key, timedelta, children):
        super(ActivityFilter, self).__init__(children)
        self.timedelta = timedelta
        self.cache_key = cache_key
        self.id = id
        self.type = 'user' if is_user else 'chat'

    def call(self, bot, msg, target, exclude):
        time = datetime.now()

        cached = Cache.get([self.cache_key, self.type, str(self.id)])
        if cached:
            last_activity = datetime.fromtimestamp(cached)
        else:
            last_activity = datetime.fromtimestamp(0)

        if (last_activity + self.timedelta) <= time:
            Cache.put([self.cache_key, self.type, str(self.id)], time.timestamp())
            return self.propagate(bot, msg, target, exclude)
        else:
            raise FilterException()

    @classmethod
    def is_entrypoint(cls):
        return True

    @classmethod
    def create(cls, stage, data, arg):
        buttons = [[InlineKeyboardButton(text='User', callback_data='user'), InlineKeyboardButton(text='Chat', callback_data='chat')]]
        if stage == 0:
            return (1, data['user_id'], Send('Do you want to filter on user or chat inactivity?', buttons=buttons))
        elif stage == 1:
            if isinstance(arg, str):
                check_user = arg == 'user'
                if check_user:
                    return (2, check_user, Send('Now forward me a message from the user to filter on'))
                else:
                    chats = [[InlineKeyboardButton(text=Cache.get_chat_title(chat_id), callback_data='c_%s' % chat_id)] for chat_id in Cache.get_admin_chats(data)]
                    return (2, check_user, Send('Which chat should be filtered on?', buttons=chats))
            else:
                return (1, None, Send('Please use the buttons', buttons=buttons))
        elif stage == 2:
            default = {'chat':{}, 'user':{}}
            if isinstance(arg, str):
                return (3, (data, arg[2:]), AskCacheKey(default))
            elif arg.forward_from:
                id = arg.forward_from.id
                return (3, (data, id), AskCacheKey(default))
            else:
                return (2, data, Send('I asked you to forward a message, it shouldn\'t be too hard '))
        elif stage == 3 and arg:
            return (4, (data[0], data[1], arg), Send('Send me the amout of minutes of inactivity'))
        elif stage == 4:
            if arg.text and re.match(r'[\d]+$', arg.text):
                type, id, key = data
                minutes = int(arg.text)
                return (5, (type, id, key, minutes, []), AskChild())
            else:
                return (4, arg, Send('Invalid input, try again'))
        elif stage == 5:
            if isinstance(arg, MessageHandler):
                data[4].append(arg)
                return (5, data, AskChild())
            else:
                type, id, key, minutes, children = data
                return (-1, None, Done(cls._from_dict({'type': type, 'id': id, 'key': key, 'timedelta': (0, minutes * 60)}, children)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for activity')

    @classmethod
    def _from_dict(cls, dict, children):
        days, seconds = dict['timedelta']
        return ActivityFilter(dict['id'], dict['type'], dict['key'], timedelta(days=days, seconds=seconds), children)

    def _to_dict(self):
        td = self.timedelta
        return {'id': self.id, 'type': self.type, 'key': self.cache_key, 'timedelta': (td.days, td.seconds)}

    @classmethod
    def get_name(cls):
        return 'Chat or user is inactive'
