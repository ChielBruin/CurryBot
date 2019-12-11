from telegram import InlineKeyboardMarkup
import re


class Send (object):
    YES_NO = [[InlineKeyboardButton(text='yes', callback_data='yes'), InlineKeyboardButton(text='no', callback_data='no')]]

    def __init__(self, msg=None, buttons=None):
        self.msg = msg if msg else ''
        if buttons is None:
            self.buttons = None
        else:
            for button_row in buttons:
                for button in button_row:
                    if not re.match(r'[A-Za-z].*', button.callback_data):
                        raise Exception('Invalid button argument \'%s\', must start with a letter' % button.callback_data)
            self.buttons = buttons

class AskChild (object):
    pass

class NoChild (object):
    pass

class AskCacheKey (object):
    pass

class AskAPIKey (object):
    pass

class Done (object):
    def __init__(self, handler):
        self.handler = handler

class CreateException (Exception):
    pass
