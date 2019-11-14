from telegram import InlineKeyboardMarkup


class Send (object):
    def __init__(self, msg=None, buttons=None):
        self.msg = msg if msg else ''
        self.buttons = InlineKeyboardMarkup(buttons) if buttons else None

class AskChild (object):
    pass

class NoChild (object):
    pass

class AskCacheKey (object):
    pass

class Done (object):
    def __init__(self, handler):
        self.handler = handler

class CreateException (Exception):
    pass
