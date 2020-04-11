import argparse, json, os

from currybot.bot import CurryBot
from currybot.data import Cache, Logger
from currybot.config import Config


def main():
    """
    Main function.
    Loads the config and starts the bot.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=argparse.FileType('r'))
    args = parser.parse_args()

    try:
        config = json.load(args.config)
    except json.JSONDecodeError:
        Logger.log_error('Invalid configuration file')
        return

    if 'API-token' not in config:
        Logger.log_error('No API token present in configuration')
        return
    api_key = config['API-token']

    if 'cache-dir' not in config:
        Logger.log_error('No cache directory present in configuration')
        return
    cache_dir = config['cache-dir']
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    if not os.path.isdir(cache_dir):
        Logger.log_error('Cache directory is a file, not a folder')
        return

    if 'encryption-key' in config:
        encryption_key = config['encryption-key']
    else:
        encryption_key = input('Enter encryption key for secure cache:\n')

    if 'admin-chat' in config:
        admin_chat = config['admin-chat']
    else:
        admin_chat = None
        Logger.log_warning('No admin chat configured')

    if len(encryption_key) > 32:
        Logger.log_error('Encryption key too long. (For some reason it is not allowed)')
    encryption_key = (encryption_key * (32 // len(encryption_key) + 1))[0:32]  # Repeat password to make it 32 characters long
    Cache.set_cipher_pwd(encryption_key)

    curry_bot = CurryBot(admin_chat)
    curry_bot.set_token(api_key)
    curry_bot.init_logger()

    Config.set_config_location(cache_dir)
    Cache.set_cache_location(cache_dir)

    Cache.load_cache()
    Config.load_config(curry_bot)

    curry_bot.start()


if __name__ == '__main__':
    main()
