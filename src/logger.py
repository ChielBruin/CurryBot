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
    def log_exception(cls, ex, msg):
        text = (msg + '\n' if msg else '') + str(type(ex).__name__) + ': ' + str(ex)
        cls.log_error(text)

    @classmethod
    def log_trace(cls, msg, details=None):
        cls._log(0, msg, details)

    @classmethod
    def log_debug(cls, msg, details=None):
        cls._log(1, msg, details)

    @classmethod
    def log_info(cls, msg, details=None):
        cls._log(2, msg, details)

    @classmethod
    def log_warning(cls, msg, details=None):
        cls._log(3, msg, details)

    @classmethod
    def log_error(cls, msg, details=None):
        cls._log(4, msg, details)

    @classmethod
    def _log(cls, level, msg, details):
        level_str = cls._get_level_string(level)
        for chat_id in cls._log_handlers:
            if cls._log_handlers[chat_id] >= level:
                continue

            if chat_id == 'console':
                line = '[%s]\t- %s' % (level_str, msg)
                print(line)
            else:
                line = '*[%s]*\t- %s' % (level_str, msg.replace('_', '\\_'))
                cls.bot.send_message(chat_id=chat_id, text=line, parse_mode='Markdown')

            if details:
                self.log_debug(details)

    @classmethod
    def _get_level_string(cls, level):
        if level is 0:
            return 'TRACE'
        elif level is 1:
            return 'DEBUG'
        elif level is 2:
            return 'INFO'
        elif level is 3:
            return 'WARNING'
        elif level is 4:
            return 'ERROR'
        else:
            cls.log_error('Undefined level log %d' % level)
            return 'UNDEFINED (%d)' % level
