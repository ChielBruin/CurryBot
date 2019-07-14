from action.action import Action

import feedparser, hashlib

class RSSAction (Action):
    '''
    An action that sends items from RSS feeds.
    '''

    def __init__(self, id, url, show=['title', 'link'], index=0):
        super(RSSAction, self).__init__(id)
        self.url = url
        self.index = index
        self.show = show

    def get_item(self, offset):
        feed = feedparser.parse(self.url)
        items = feed['items']
        return items[min(len(items) - 1, self.index + offset)]

    def build_text(self, item):
        texts = []
        for elem in self.show:
            texts.append(item[elem])
        return '\n'.join(texts)

    def select_item(self, exclude, offset=0):
        item = self.get_item(offset)
        hash = hashlib.md5(item['title'].encode()).hexdigest()
        id = "%s_%s" % (self.id, hash)
        
        if id in exclude:
            return self.select_item(exclude, offset+1)
        else:
            return (id, item)

    def dispatch(self, bot, msg, exclude):
        (id, item) = self.select_item(exclude)
        text = self.build_text(item)
        bot.send_message(chat_id=msg.chat.id, text=text)
        return [id]

    def dispatch_reply(self, bot, msg, reply_to, exclude):
        (id, item) = self.select_item(exclude)
        text = self.build_text(item)
        bot.send_message(chat_id=chat_id, text=msg, reply_to_message_id=reply_to)
        return [id]
