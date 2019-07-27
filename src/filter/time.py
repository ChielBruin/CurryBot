from filter.filter import Filter


class TimeFilter (Filter):
    def __init__(self, id, minute=None, hour=None, day=None, weekday=None, week=None, month=None, monthweek=None, year=None):
        super(TimeFilter, self).__init__(id)

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

    def filter(self, message):
        time = message.date
        if (
                ((not self.minute    is None) or self.minute    is time.minute)
            and ((not self.hour      is None) or self.hour      is time.hour)
            and ((not self.day       is None) or self.day       is time.day)
            and ((not self.weekday   is None) or self.weekday   is time.isoweekday())
            and ((not self.week      is None) or self.week      is time.isocalendar()[1])
            and ((not self.month     is None) or self.month     is time.month)
            and ((not self.monthweek is None) or self.monthweek is self.calc_monthweek(time))
            and ((not self.year      is None) or self.year      is time.year)
           ):
            return message
        else:
            return None
