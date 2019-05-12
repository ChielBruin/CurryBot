from action import Action

import hashlib, re


class ForwardAction (Action):
    '''
    An action that forwards messages when triggered.
    '''

    def __init__(self, config):
        '''
        Load all the messages from the given config
        '''
        super(ForwardAction, self).__init__(config)

        for msg in config:
            chat_id = msg['chat_id']
            msg_id = msg['message_id']

            id = "FWD_%d_%d" % (chat_id, msg_id)
            self.ids.append(id)
            self.vals[id] = (chat_id, msg_id)
        print('\t%d messages loaded' % len(self.ids))

    def trigger(self, bot, message, exclude=[], reply=None):
        chat_id = message.chat_id

        reply_id = self.select_random_id(exclude=exclude)
        (fwd_chat_id, fwd_msg_id) = self.vals[reply_id]

        bot.forward_message(chat_id=chat_id, from_chat_id=fwd_chat_id, message_id=fwd_msg_id)
        return reply_id
