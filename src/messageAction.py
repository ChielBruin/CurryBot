from action import Action

import hashlib, re


class MessageAction (Action):
    def __init__(self, config, regex):
        super(MessageAction, self).__init__()

        self.regex = regex

        messages = map(lambda x: (hashlib.md5(x.encode()).hexdigest(), x), config)
        for (msg_id, msg_text) in messages:
            self.ids.append(msg_id)
            self.vals[msg_id] = msg_text
        print('\t%d messages loaded' % len(self.ids))

    def apply_message(self, message_text, reply_text):
        if self.regex and '\\' in reply_text:
            try:
                return re.sub(self.regex, reply_text, message_text)
            except Exception:
                pass
        return reply_text

    def trigger(self, bot, message, exclude=[], reply=None):
        chat_id = message.chat_id

        reply_text_id = self.select_random_id(exclude=exclude)
        reply_text = self.vals[reply_text_id]

        applied_message = self.apply_message(message.text, reply_text)
        if reply:
            bot.send_message(chat_id=chat_id, text=applied_message, reply_to_message_id=reply)
        else:
            bot.send_message(chat_id=chat_id, text=applied_message)
        return reply_text_id
