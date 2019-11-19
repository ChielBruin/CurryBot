import sys

from bot import CurryBot
from data import Cache, Logger
from config import Config


def main():
    '''
    Main function.
    Loads the config and starts the bot.
    '''
    api_key = input('Telegram API key:')
    cache_dir = input('Cache directory:')
    cipher_pwd = input('Encryption key for secure cache (leave empty to skip, not recommended)')

    # TODO:
    #  - Padd the password if too short, error if too long
    #  - Check if cache dir exists

    curry_bot = CurryBot()
    curry_bot.set_token(api_key)

    Config.set_config_location(cache_dir)
    Cache.set_cache_location(cache_dir)

    Config.load_config(curry_bot)
    Cache.load_cache()

    curry_bot.start()

if __name__ == '__main__':
    main()
