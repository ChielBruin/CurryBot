from messageHandler import MessageHandler, TickHandler
from sendBehaviour import SendBehaviour
from cache import Cache
from config import Config
from logger import Logger


class ConfigLoader (object):
    def __init__(self, config_file):
        # Config file is currently unused
        pass

    def apply_config(self, bot):
        Logger.init(bot, {})
        bot.set_token('TELEGRAM-API-TOKEN')
        telegram_bot = bot.updater.bot
        Cache.set_cache_location('cache')
        Config.set_config_location('cache')

        Cache.load_cache()
        Config.load_config()

        # Register handlers here

        Cache.store_cache()
        Config.store_config()
