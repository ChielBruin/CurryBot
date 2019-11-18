from messageHandler import MessageHandler
from exceptions import FilterException


class TimeFilter (MessageHandler):
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
