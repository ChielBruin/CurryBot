from filter.filter import Filter

class AbstractActivityFilter(Filter):
    # TODO: Move this to the cache, such that ActivityActions can access it
    activity = {}
    def __init__(self, id):
        super(AbstractActivityFilter, self).__init__(id)

    def get_last_activity(self, chat_id):
        if chat_id in self.activity:
            return self.activity[chat_id]
        else:
            return None

    def set_last_activity(self, chat_id, datetime):
        self.activity[chat_id] = datetime

class InactiveFilter (AbstractActivityFilter):
    def __init__(self, id, minute=None, hour=None, day=None, month=None, year=None):
        super(TimeFilter, self).__init__(id)
        self.timedelta = None

    def filter(self, message):
        time = message.date
        chat_id = message.chat.id

        now_time = datetime.datetime.now()
        last_activity = self.get_last_activity(chat_id)

        if last_activity and (last_activity + self.time_delta) <= time:
            self.set_last_activity(chat_id, time)
            return message
        else:
            return None
