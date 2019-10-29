from messageHandler import MessageHandler

import feedparser, hashlib

class SendRSS (MessageHandler):
    '''
    An action that sends items from RSS feeds.
    '''

    def __init__(self, url, show=['title', 'link'], index=0):
        super(RSSAction, self).__init__([])
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

    def dispatch_reply(self, bot, msg, target, exclude):
        (id, item) = self.select_item(exclude)
        text = self.build_text(item)
        bot.send_message(chat_id=chat_id, text=msg, reply_to_message_id=target)
        return [id]

class SendReddit (SendRSS):
    def __init__(self, subreddit, show=['title', 'link'], index=0):
        url = 'https://www.reddit.com/r/%s.rss' % subreddit
        super(SendReddit, self).__init__(url, show=show, index=index)
