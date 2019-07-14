from messageHandler import MessageHandler, TickHandler
from sendBehaviour import SendBehaviour
from cache import Cache

from filter.regex    import MatchFilter, SearchFilter, CommandFilter
from filter.composit import PercentageFilter, AndFilter, OrFilter, NoFilter
from filter.type     import IsReplyFilter
from filter.time     import TimeFilter

from action.message  import MessageAction
from action.composit import AndAction, OrAction, PercentageAction
from action.sticker  import StickerAction
from action.flickr   import FlickrAction
from action.rss      import RSSAction
from action.util     import InfoAction, UpdateAction
from action.youtube  import YtPlaylistAppendAction

class ConfigLoader (object):
    def __init__(self, config_file):
        # Config file is currently unused
        pass

    def apply_config(self, bot):
        bot.set_token('TELEGRAM-API-TOKEN')
        telegram_bot = bot.updater.bot
        Cache.set_cache_location('/path/to/cache')
        Cache.load_cache()

        # Redigster handlers here

        Cache.store_cache()
