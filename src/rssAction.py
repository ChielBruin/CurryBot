from action import Action

import feedparser

class RSSAction (Action):
    '''
    An action that sends items from RSS feeds.
    '''

    def __init__(self, config):
        super(RSSAction, self).__init__(config)
        self.url = config['url']
        self.index = int(config['index']) if 'index' in config else 0
        self.config = config

        if not self.weight:
            self.weight = 1

    def get_item(self, offset):
        feed = feedparser.parse(self.url)
        items = feed['items']
        item = items[min(len(items) - 1, self.index + offset)]
        return (item['title'], item['link'], item['description'])

    def trigger(self, bot, message, exclude=[], reply=None):
        chat_id = message.chat_id

        (title, link, description) = self.get_item(len(exclude))
        msg = []
        if 'showTitle' in self.config and self.config['showTitle']:
            msg.append(title)
        if 'showDescription' in self.config and self.config['showDescription']:
            msg.append(description)
        if 'showLink' in self.config and self.config['showLink']:
            msg.append(link)

        msg = '\n'.join(msg)
        if reply:
            bot.send_message(chat_id=chat_id, text=msg, reply_to_message_id=reply)
        else:
            bot.send_message(chat_id=chat_id, text=msg)

        return link
