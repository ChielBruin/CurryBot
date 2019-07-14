import traceback, sys


class Logger(object):
    @classmethod
    def init(cls, bot):
        cls._logger = {
            'TRACE': ['console'],
            'DEBUG': ['console'],
            'INFO':  ['console', '310311697'],
            'WARNING': ['console'],
            'ERROR': ['console']
        }
        cls.bot = bot

    @classmethod
    def log(cls, level, msg, details=None):
        if not level in cls._logger:
            cls.log('ERROR', 'Unknown log level {} while logging "{}"' % (level, msg))
            return

        for chat_id in cls._logger[level]:
            if chat_id == 'console':
                line = '[%s]\t- %s' % (level, msg)
                print(line)
            else:
                line = '*[%s]*\t- %s' % (level, msg.replace('_', '\\_'))
                cls.bot.send_message(chat_id=chat_id, text=line, parse_mode='Markdown')

            if details:
                self.log('DEBUG', details)

    @classmethod
    def log_exception(cls, level, ex, msg=None):
        text = (msg + '\n' if msg else '') + str(type(ex).__name__) + ': ' + str(ex)
        cls.log(level, text)
