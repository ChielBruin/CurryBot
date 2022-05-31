from telegram import InlineKeyboardButton, Message

from currybot.handlers.messageHandler import MessageHandler
from currybot.exceptions import FilterException
from currybot.configResponse import Send, Done, AskChild, NoChild, CreateException


class TimeFilter(MessageHandler):
    def __init__(self, minute=None, hour=None, day=None, weekday=None, week=None, month=None, monthweek=None, year=None, children=[]):
        super(TimeFilter, self).__init__(children)

        self.minute    = minute
        self.hour      = hour
        self.day       = day
        self.weekday   = weekday
        self.week      = week
        self.month     = month
        self.monthweek = monthweek
        self.year      = year

    def calc_monthweek(self, date):
        day = date.weekday()
        first_day_of_this_week = date.day - day
        return 1 + (first_day_of_this_week // 7)

    def call(self, bot, message, target, exclude):
        time = message.date
        if (
                ((self.minute    is None) or self.minute    == time.minute)
            and ((self.hour      is None) or self.hour      == time.hour)
            and ((self.day       is None) or self.day       == time.day)
            and ((self.weekday   is None) or self.weekday   == time.isoweekday())
            and ((self.week      is None) or self.week      == time.isocalendar()[1])
            and ((self.month     is None) or self.month     == time.month)
            and ((self.monthweek is None) or self.monthweek == self.calc_monthweek(time))
            and ((self.year      is None) or self.year      == time.year)
           ):
            return self.propagate(bot, message, target, exclude)
        else:
            raise FilterException()

    @classmethod
    def is_entrypoint(cls):
        return True

    @classmethod
    def get_name(cls):
        return "Filter on time"

    @classmethod
    def _create_step(cls, stage, data, arg, current_string, next_string, min, max, opt_string=''):
        buttons = [[InlineKeyboardButton(text='yes', callback_data='yes'), InlineKeyboardButton(text='no', callback_data='no')]]

        if stage % 2 == 1:
            if isinstance(arg, Message):
                return (stage, data, Send('Please reply by clicking the buttons', buttons=buttons))
            else:
                if arg == 'yes':
                    return (stage + 1, data, Send('Send me a number to filter the %s on. %s' % (current_string, opt_string)))
                else:
                    data.append(None)
                    if next_string is None:
                        return data
                    else:
                        return (stage + 2, data, Send('Do you want to filter on the %s?' % next_string, buttons=buttons))
        elif stage % 2 is 0:
            if arg.text:
                try:
                    val = int(arg.text)
                    if val < min or val >= max:
                        raise ValueError()
                    data.append(val)
                    if next_string is None:
                        return data
                    else:
                        return (stage + 1, data, Send('Do you want to filter on the %s?' % next_string, buttons=buttons))
                except ValueError:
                    return (stage, data, Send('Invalid value, please try again'))
            else:
                return (stage, data, Send('It would be nice if you actually tried to send text'))

    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            buttons = [[InlineKeyboardButton(text='yes', callback_data='yes'), InlineKeyboardButton(text='no', callback_data='no')]]
            return (1, [], Send('Do you want to filter on minutes?', buttons=buttons))
        if stage in (1, 2):
            return cls._create_step(stage, data, arg,
                'minutes', 'hour', 0, 60
            )
        elif stage in (3, 4):
            return cls._create_step(stage, data, arg,
                'hour', 'day', 0, 24
            )
        elif stage in (5, 6):
            return cls._create_step(stage, data, arg,
                'day', 'weekday', 1, 32
            )
        elif stage in (7, 8):
            return cls._create_step(stage, data, arg,
                'weekday', 'week', 0, 7, opt_string='Monday is 0 and Sunday is 6'
            )
        elif stage in (9, 10):
            return cls._create_step(stage, data, arg,
                'week', 'month', 1, 53
            )
        elif stage in (11, 12):
            return cls._create_step(stage, data, arg,
                'month', 'week of the month', 1, 13
            )
        elif stage in (13, 14):
            return cls._create_step(stage, data, arg,
                'week of the month', 'year', 1, 5
            )
        elif stage in (15, 16):
            res = cls._create_step(stage, data, arg,
                'year', None, 2000, 3000
            )
            if isinstance(res, tuple):
                return res
            else:
                return (17, ([], res), AskChild())

        elif stage == 17 and isinstance(arg, MessageHandler):
            data[0].append(arg)
            return (17, data, AskChild())
        elif stage == 17 and isinstance(arg, NoChild):
            children, config = data
            return (-1, None, Done(TimeFilter(config[0], config[1], config[2], config[3], config[4], config[5], config[6], config[7], children=children)))

        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for timeFilter')

    @classmethod
    def _from_dict(cls, dict, children):
        return TimeFilter(
            dict['min'],
            dict['hour'],
            dict['day'],
            dict['weekday'],
            dict['week'],
            dict['month'],
            dict['monthweek'],
            dict['year'],
            children=children
        )

    def _to_dict(self):
        return {
            'min': self.minute,
            'hour': self.hour,
            'day': self.day,
            'weekday': self.weekday,
            'week': self.week,
            'month': self.month,
            'monthweek': self.monthweek,
            'year': self.year
        }
