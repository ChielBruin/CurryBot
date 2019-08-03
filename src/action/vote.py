from action.action import Action
from cache import Cache


class AbstractVoteAction (Action):
    def __init__(self, id, key, check_user, condition, on_condition, check_content):
        super(AbstractVoteAction, self).__init__(id)
        self.key = key
        self.check_user = check_user
        self.condition = condition
        self.on_condition = on_condition
        self.check_content = check_content


    def update(self):
        if self.on_condition:
            self.on_condition.update()

    def do_count(self, count):
        raise Exception('Not implemented')

    def get_votes(self, msg):
        if self.check_content:
            key = msg.text
        else:
            key = msg.message_id

        out = Cache.shared_get_cache(self.key, key)
        if not out:
            out = (0, [])
        return (key, out)

    def on_action(self, msg):
        key, (val, users) = self.get_votes(msg)
        new_val = self.do_count(val)
        if self.check_user:
            if msg.from_user.id in users:
                return False
            else:
                users.append(msg.from_user.id)
        Cache.shared_put_cache(self.key, key, (new_val, users))

        return self.condition and self.condition(new_val)

    def dispatch(self, bot, msg, exclude):
        if self.on_action(msg) and self.on_condition:
            return self.on_condition.dispatch(bot, msg, exclude)
        else:
            return []

    def dispatch_reply(self, bot, msg, reply_to, exclude):
        if self.on_action(msg) and self.on_condition:
            return self.on_condition.dispatch_reply(bot, msg, reply_to, exclude)
        else:
            return []


class UpVoteAction (AbstractVoteAction):
    def __init__(self, id, key, check_user=True, condition=None, on_condition=None, check_content=False):
        super(UpVoteAction, self).__init__(id, key, check_user, condition, on_condition, check_content)

    def do_count(self, count):
        return count + 1


class DownVoteAction (AbstractVoteAction):
    def __init__(self, id, key, check_user=True, condition=None, on_condition=None, check_content=False):
        super(DownVoteAction, self).__init__(id, key, check_user, condition, on_condition, check_content)

    def do_count(self, count):
        return count - 1


class GetVoteAction (AbstractVoteAction):
    def __init__(self, id, key, message, check_content=False):
        super(GetVoteAction, self).__init__(id, key, False, None, None, check_content)
        self.string = message
        if '%d' not in message:
            raise Exception('The format string for getting votes needs to accept a number')

    def dispatch(self, bot, msg, exclude):
        _ , (count, _) = self.get_votes(msg)
        text = self.string % count
        bot.send_message(chat_id=msg.chat.id,
                         text=text)
        return []

    def dispatch_reply(self, bot, msg, reply_to, exclude):
        _ , (count, _) = self.get_votes(msg)
        text = self.string % count
        bot.send_message(chat_id=msg.chat.id,
                         text=text,
                         reply_to_message_id=reply_to)
        return []
