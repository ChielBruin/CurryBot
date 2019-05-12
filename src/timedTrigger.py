from datetime import datetime, timedelta

class TimedTrigger (object):
    def __init__(self, job_queue, when, groups, handler):
        self.when = when
        self.chats = groups
        self.queue = job_queue
        self.handler = handler

        time = self.schedule_next()
        print(datetime.strftime(time, "\t%Y-%m-%d (%w):%H-%M-%S"))


    def on_trigger(self, bot, job):
        self.schedule_next()
        text = self.when['param'] if 'param' in self.when else ''

        for chat_id in self.chats:
            self.handler.on_receive_anonymous(bot, chat_id, datetime.now(), msg_text=text)

    def schedule_next(self):
        next_time = self.next_valid_time()
        self.queue.run_once(lambda bot, job, self=self: self.on_trigger(bot, job), next_time)
        return next_time

    def next_valid_time(self):
        now_time = datetime.now() + timedelta(seconds=5)

        desired_second  = int(self.when['second']) if 'second' in self.when else 0

        desired_minute  = int(self.when['minute']) if 'minute' in self.when else None
        desired_hour    = int(self.when['hour'])   if 'hour'   in self.when else None

        desired_day     = int(self.when['day'])    if 'day'    in self.when else None
        desired_month   = int(self.when['month'])  if 'month'  in self.when else None
        desired_year    = int(self.when['year'])   if 'year'   in self.when else None
        desired_weekday = (int(self.when['weekday']) + 6) % 7 if 'weekday' in self.when else None

        while(not(now_time.second is desired_second)):
            now_time += timedelta(seconds=1)

        while(not(
            ((desired_minute  is None) or (now_time.minute    is desired_minute)) and
            ((desired_hour    is None) or (now_time.hour      is desired_hour))
            )):
            now_time += timedelta(minutes=1)

        while(not(
            ((desired_day     is None) or (now_time.day       is desired_day))    and
            ((desired_month   is None) or (now_time.month     is desired_month))  and
            ((desired_year    is None) or (now_time.year      is desired_year))   and
            ((desired_weekday is None) or (now_time.weekday() is desired_weekday))
            )):
            now_time += timedelta(days=1)

        return now_time
