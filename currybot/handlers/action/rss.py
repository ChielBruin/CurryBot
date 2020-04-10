import hashlib
import feedparser
import re

from currybot.configResponse import Send, Done, CreateException
from currybot.data.logger import Logger
from currybot.handlers.messageHandler import MessageHandler


class SendRSS(MessageHandler):
    """
    An action that sends items from RSS feeds.
    """
    def __init__(self, url, show=None, index=0):
        super(SendRSS, self).__init__([])
        self.url = url
        self.index = index
        self.show = show if show else ['title', 'link']

    def get_item(self, offset):
        feed = feedparser.parse(self.url)
        items = feed['items']
        if not items:
            Logger.log_warning('Empty feed for %s' % self.url)
            return None
        return items[min(len(items) - 1, self.index + offset)]

    def build_text(self, item):
        texts = []
        for elem in self.show:
            texts.append(item[elem])
        return '\n'.join(texts)

    def select_item(self, exclude, offset=0):
        item = self.get_item(offset)
        if item is None:
            return (None, None)
        id = str(hashlib.md5(item['title'].encode()).hexdigest())

        if id in exclude:
            return self.select_item(exclude, offset+1)
        else:
            return (id, item)

    def call(self, bot, msg, target, exclude):
        (id, item) = self.select_item(exclude)
        if item is None:
            return []
        text = self.build_text(item)
        bot.send_message(chat_id=msg.chat.id, text=text, reply_to_message_id=target)
        return [id]

    def has_effect(self):
        return True

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def get_name(cls):
        return "Send an item from an RSS feed"

    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            return (1, None, Send(cls._initial_message()))
        elif stage == 1 and arg:
            if arg.text:
                url = cls._parse_url(arg.text)
                if url:
                    return (2, url, Send('What is the start index? (0 for the first item)'))
            return (1, None, Send('Please reply with a url to an RSS feed'))
        elif stage == 2 and arg:
            if arg.text and re.match(r'[\d]+$', arg.text):
                return (3, (data, int(arg.text), []), Send('Should the title be shown?', buttons=Send.YES_NO))
            else:
                return (2, None, Send('Ivalid index, try again'))
        elif stage == 3:
            if isinstance(arg, str):
                if arg == 'yes':
                    data[2].append('title')
                return (4, data, Send('Should the discription be shown?', buttons=Send.YES_NO))
            else:
                return (3, data, Send('I created those buttons for a reason...', buttons=Send.YES_NO))
        elif stage == 4:
            if isinstance(arg, str):
                if arg == 'yes':
                    data[2].append('description')
                return (5, data, Send('Should the link be shown?', buttons=Send.YES_NO))
            else:
                return (4, data, Send('Please use these buttons:', buttons=Send.YES_NO))
        elif stage == 5:
            if isinstance(arg, str):
                if arg == 'yes':
                    data[2].append('link')
                (url, index, show) = data
                return (-1, None, Done(SendRSS(url, show, index)))
            else:
                return (5, data, Send('I\'m just a bot, I cannot read human', buttons=Send.YES_NO))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for sendTextMessage')

    @classmethod
    def _initial_message(cls):
        return 'Please send me the URL of the RSS feed'

    @classmethod
    def _parse_url(cls, url):
        if re.match(r'https?://[^\s]+\.rss$', url):
            return url
        else:
            return None

    def _to_dict(self):
        return {'url': self.url, 'show': self.show, 'index': self.index}

    @classmethod
    def _from_dict(cls, dict, children):
        return SendRSS(dict['url'], dict['show'], dict['index'])


class SendReddit(SendRSS):
    @classmethod
    def get_name(cls):
        return "Send Reddit post"

    @classmethod
    def _initial_message(cls):
        return 'Please send me the name of the subreddit'

    @classmethod
    def _parse_url(cls, subreddit):
        if re.match(r'[^\s]+$', subreddit):
            return 'https://www.reddit.com/r/%s.rss' % subreddit
        else:
            return None
