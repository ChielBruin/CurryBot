from action.action import Action


class AbstractMessageAction (Action):
    def __init__(self, id, message, parse_mode, show_preview):
        super(AbstractMessageAction, self).__init__(id)
        self.parse_mode = parse_mode
        self.show_preview = show_preview
        self.append_ids_indexed([message])

    def apply_message(self, message_text, reply_text):
        '''
        Given the original message and the reply text pattern,
        try filling in the holes in the reply pattern.
        '''
        if '%s' in reply_text:
            return reply_text % message_text
        else:
            return reply_text

    def dispatch(self, bot, msg, exclude):
        (id, message) = self.select_random_option(exclude=exclude)
        applied_message = self.apply_message(msg.text, message)

        bot.send_message(chat_id=msg.chat.id,
                         text=applied_message,
                         parse_mode=self.parse_mode,
                         disable_web_page_preview=not self.show_preview)
        return [id]

    def dispatch_reply(self, bot, msg, reply_to, exclude):
        (id, message) = self.select_random_option(exclude=exclude)
        applied_message = self.apply_message(msg.text, message)

        bot.send_message(chat_id=msg.chat.id,
                         text=applied_message,
                         reply_to_message_id=reply_to,
                         parse_mode=self.parse_mode,
                         disable_web_page_preview=not self.show_preview)
        return [id]

class TextMessageAction (AbstractMessageAction):
    def __init__(self, id, message, show_preview=True):
        super(TextMessageAction, self).__init__(id, message, parse_mode=None, show_preview=show_preview)


class MarkdownMessageAction (AbstractMessageAction):
    def __init__(self, id, message, show_preview=True):
        super(MarkdownMessageAction, self).__init__(id, message, parse_mode='Markdown', show_preview=show_preview)


class HTMLMessageAction (AbstractMessageAction):
    def __init__(self, id, message, show_preview=True):
        super(HTMLMessageAction, self).__init__(id, message, parse_mode='HTML', show_preview=show_preview)


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
