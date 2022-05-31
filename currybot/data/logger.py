from telegram.error import TimedOut
import traceback, sys


class Logger(object):
    '''
    0: TRACE
    1: DEBUG
    2: INFO
    3: WARNING
    4: ERROR
    '''
    _log_handlers = {'console': 0}

    @classmethod
    def init(cls, bot, log_chats={}):
        for chat_id in log_chats:
            cls._log_handlers[chat_id] = int(log_chats[chat_id])

        cls.bot = bot

    @classmethod
    def log_exception(cls, ex, msg, chat=None):
        text = (msg + '\n' if msg else '') + str(type(ex).__name__) + ': ' + str(ex)
        cls.log_error(text, chat=chat)

    @classmethod
    def log_trace(cls, msg, details=None, chat=None):
        cls._log(0, msg, details, chat)

    @classmethod
    def log_debug(cls, msg, details=None, chat=None):
        cls._log(1, msg, details, chat)

    @classmethod
    def log_info(cls, msg, details=None, chat=None):
        cls._log(2, msg, details, chat)

    @classmethod
    def log_warning(cls, msg, details=None, chat=None):
        cls._log(3, msg, details, chat)

    @classmethod
    def log_error(cls, msg, details=None, chat=None):
        cls._log(4, msg, details, chat)

    @classmethod
    def _log(cls, level, msg, details, chat, console_only=False):
        (level_str, level_color) = cls._get_level_string(level)
        if (not chat is None) and not console_only:
            line = '*[%s]*\t- %s' % (level_str, msg.replace('_', '\\_'))
            cls.bot.send_message(chat_id=chat, text=line, parse_mode='Markdown')

        for chat_id in cls._log_handlers:
            if level < cls._log_handlers[chat_id]:
                continue

            if chat_id == 'console':
                line = '[%s%s\033[0m]\t- %s' % ('\033[%dm' % level_color, level_str, msg)
                print(line)
            elif not console_only:
                try:
                    line = '*[%s]*\t- %s' % (level_str, msg.replace('_', '\\_'))
                    cls.bot.send_message(chat_id=chat_id, text=line, parse_mode='Markdown')
                except TimedOut:
                    cls.log_error('Sending log message timed out')

            if details:
                cls.log_debug(details)

    @classmethod
    def _get_level_string(cls, level):
        if level == 0:
            return ('TRACE', 39)
        elif level == 1:
            return ('DEBUG', 96)
        elif level == 2:
            return ('INFO', 92)
        elif level == 3:
            return ('WARNING', 93)
        elif level == 4:
            return ('ERROR', 31)
        else:
            cls.log_error('Undefined level log %d' % level)
            return ('UNDEFINED (%d)' % level, '')
