from telegram import InlineKeyboardButton, Message
from currybot.configResponse import Send, Done, AskChild, CreateException
from currybot.handlers.messageHandler import MessageHandler


class Pin(MessageHandler):
    def __init__(self, do_replace):
        super(Pin, self).__init__([])
        self.do_replace = do_replace

    def call(self, bot, msg, target, exclude):
        if self.do_replace:
            # Check if there is something pinned before unpinning
            chat = bot.get_chat(msg.chat.id)
            if chat.pinned_message:
                bot.unpin_chat_message(msg.chat.id)
        bot.pin_chat_message(msg.chat.id, msg.message_id)
        return []

    @classmethod
    def is_entrypoint(cls):
        return False

    def has_effect(self):
        return True

    @classmethod
    def get_name(cls):
        return "Pin the message"

    def _to_dict(self):
        return {'doReplace': self.do_replace}

    @classmethod
    def _from_dict(cls, dict, children):
        return Pin(dict['doReplace'])

    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            buttons = [[InlineKeyboardButton(text='yes', callback_data='yes')], [InlineKeyboardButton(text='no', callback_data='no')]]
            msg = 'Should an existing pin be replaced?'
            return (1, None, Send(msg=msg, buttons=buttons))
        elif stage == 1:
            if isinstance(arg, Message):
                buttons = [[InlineKeyboardButton(text='yes', callback_data='yes')], [InlineKeyboardButton(text='no', callback_data='no')]]
                msg = 'Please use the buttons'
                return (1, None, Send(msg=msg, buttons=buttons))
            return (-1, None, Done(Pin(arg == 'yes')))
