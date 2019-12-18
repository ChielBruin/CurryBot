import re

from ..messageHandler import MessageHandler
from exceptions       import FilterException
from data             import Cache
from configResponse   import Send, Done, AskChild, NoChild, CreateException


class IntFilter (MessageHandler):
    def __init__(self, condition, value, children):
        super(IntFilter, self).__init__(children)
        self.condition = condition
        self.value = value
        if condition == '<':
            self.condition_lambda = lambda x: x < value
        elif condition == '<=':
            self.condition_lambda = lambda x: x <= value
        elif condition == '>':
            self.condition_lambda = lambda x: x > value
        elif condition == '>=':
            self.condition_lambda = lambda x: x >= value
        elif condition == '==':
            self.condition_lambda = lambda x: x == value
        elif condition == '!=':
            self.condition_lambda = lambda x: x != value
        else:
            raise Exception('Unknown operator %s' % condition)

    def call(self, bot, message, target, exclude):
        if re.match(r'-?[\d]+', message.text):
            if self.condition_lambda(int(message.text)):
                return self.propagate(bot, message, target, exclude)
            else:
                raise FilterException()
        else:
            raise Exception('Message content is not an integer, found %s' % message.text)

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def get_name(cls):
        return "Integer compare"

    @classmethod
    def _from_dict(cls, dict, children):
        return IntFilter(dict['comp'], dict['val'], children)

    def _to_dict(self):
        return {'comp': self.condition, 'val':self.value}

    @classmethod
    def create(cls, stage, data, arg):
        buttons = [[
            InlineKeyboardButton(text='>',  callback_data='>'),
            InlineKeyboardButton(text='<',  callback_data='<'),
            InlineKeyboardButton(text='>=', callback_data='>='),
            InlineKeyboardButton(text='<=', callback_data='<='),
            InlineKeyboardButton(text='==', callback_data='=='),
            InlineKeyboardButton(text='!=', callback_data='!=')
        ]]
        if stage == 0:
            return (1, None, Send('What comparison operator should be used?', buttons=buttons))
        elif stage == 1:
            if isinstance(arg, str):
                return (2, arg, Send('Which value should be at the right hand side of the comparison?'))
            else:
                return (1, None, Send('No, thats not the right button......', buttons=buttons))
        elif stage == 2:
            if re.match(r'-?[\d]+', arg.text):
                return (-1, None, Done(IntFilter(data, int(arg.text)))
            else:
                return (2, data, Send('That is not an integer, examples are 1, 2, -4 and 112'))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for SenderIsBotAdmin')
