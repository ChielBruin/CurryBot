from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message
from currybot.configResponse import Send, Done, AskChild, CreateException
from currybot.handlers.messageHandler import MessageHandler

class UrlButton(MessageHandler):
    def __init__(self, button_text):
        super(UrlButton, self).__init__([])
        self.text = button_text

    def call(self, bot, msg, target, exclude):
        buttons = InlineKeyboardMarkup([[InlineKeyboardButton(text=self.text, url=msg.text)]])
        bot.send_message(chat_id=msg.chat.id,
                         text='🔎',
                         reply_to_message_id=target,
                         reply_markup=buttons)
        return []

    @classmethod
    def is_entrypoint(cls):
        return False

    def has_effect(self):
        return True

    @classmethod
    def get_name(cls):
        return "Make a clickable button from the message as url"

    def _to_dict(self):
        return {'text': self.text}

    @classmethod
    def _from_dict(cls, dict, children):
        return UrlButton(dict['text'])

    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            msg = 'Please send me the text for on the button'
            return (1, None, Send(msg))
        elif stage == 1:
            if isinstance(arg, Message):
                return (1, None, Done(UrlButton(arg.text)))
            return (1, None, Send('I don\'t like that name, please send me a different one'))
