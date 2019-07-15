from telegram import Message, Chat

from logger import Logger


class MessageHandler (object):
    def __init__(self, name, filter, behaviour, action):
        self.name = name
        self.filter = filter
        self.behaviour = behaviour
        self.action = action
        Logger.log_info('Action \'%s\' Initialized' % self.name)

    def update(self):
        try:
            self.filter.update()
            self.action.update()
        except Exception as ex:
            Logger.log_exception(ex, msg='Exception while updating the cache of %s' % self.name)

    def call(self, bot, message):
        try:
            msg = self.filter.filter(message)
            if not msg:
                return

            if msg.chat.id is None:
                Logger.log_error('No chat ID specified in rule %s' % self.name)
                return

            selected = []

            if msg:
                for reply_to in self.behaviour.apply(msg):
                    if reply_to:
                        reply_ids = self.action.dispatch_reply(bot, msg, reply_to, exclude=selected)
                    else:
                        reply_ids = self.action.dispatch(bot, msg, exclude=selected)
                    selected.extend(reply_ids)
        except Exception as ex:
            Logger.log_exception(ex, msg=self.name)


class TickHandler (MessageHandler):
    def __init__(self, name, groups, filter, behaviour, action):
        super(TickHandler, self).__init__(name, filter, behaviour, action)
        self.groups = groups

    def call(self, bot, time):
        for group_id in self.groups:
            msg = Message(-1, None, time, Chat(group_id, 'tick_group %s' % group_id), text='tick @ %s' % time.strftime('%Y-%m-%d %H:%M:%S'))
            super(TickHandler, self).call(bot, msg)
