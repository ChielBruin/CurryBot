from filter.filter import Filter


class IsReplyFilter (Filter):
    def filter(self, message):
        if message.reply_to_message:
            return message
        else:
            return None

class InChatFilter (Filter):
    def __init__(self, id, chat_id):
        super(InChatFilter, self).__init__(id)
        self.chat_id = chat_id

    def filter(self, message):
        if str(message.chat.id) == self.chat_id:
            return message
        else:
            return None
