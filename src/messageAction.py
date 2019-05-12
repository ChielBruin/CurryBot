from action import Action

import hashlib, re


class MessageAction (Action):
    '''
    An action that sends messages when triggered.
    These messages can use matched groups from the original message.
    '''

    def __init__(self, config, regexes):
        '''
        Load all the messages from the given config
        '''
        super(MessageAction, self).__init__(config)

        self.regexes = regexes

        messages = map(lambda x: (hashlib.md5(x.encode()).hexdigest(), x), config)
        for (msg_id, msg_text) in messages:
            self.ids.append(msg_id)
            self.vals[msg_id] = msg_text
        print('\t%d messages loaded' % len(self.ids))

    def apply_message(self, message_text, reply_text):
        '''
        Given the original message and the reply text pattern,
        try filling in the holes in the reply pattern.
        '''
        if '\\' in reply_text:
            if len(self.regexes) > 0:
                for regex in self.regexes:
                    try:
                        return re.sub(regex, reply_text, message_text)
                    except Exception:
                        continue
            elif '\\$' in reply_text:
                return reply_text.replace('\\$', message_text)
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
