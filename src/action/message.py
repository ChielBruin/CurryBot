from action.action import Action


class MessageAction (Action):
    def __init__(self, id, message):
        super(MessageAction, self).__init__(id)
        self.append_ids_indexed([message])

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

    def dispatch(self, bot, msg, exclude):
        (id, message) = self.select_random_option(exclude=exclude)
        applied_message = self.apply_message(msg.text, message)

        bot.send_message(chat_id=msg.chat.id, text=applied_message)
        return [id]

    def dispatch_reply(self, bot, msg, reply_to, exclude):
        (id, message) = self.select_random_option(exclude=exclude)
        applied_message = self.apply_message(msg.text, message)

        bot.send_message(chat_id=msg.chat.id, text=applied_message, reply_to_message_id=reply_to)
        return [id]


class ForwardAction (Action):
    '''
    An action that forwards a message.
    '''

    def __init__(self, id, chat_id, msg_id):
        '''
        Load all the messages from the given config
        '''
        super(ForwardAction, self).__init__(id)
        self.chat_id = chat_id
        self.msg_id = msg_id

    def dispatch(self, bot, msg, exclude):
        bot.forward_message(chat_id=msg.chat.id, from_chat_id=self.chat_id, message_id=self.msg_id)
        return [self.id]

    def dispatch_reply(self, bot, msg, reply_to, exclude):
        raise Exception('You cannot reply using a forwarded message')
