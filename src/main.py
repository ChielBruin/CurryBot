import sys

from bot import CurryBot
from configLoader import ConfigLoader
from cache import Cache
from logger import Logger
from signal import signal, SIGTERM

def sigterm_handler(_signo, _stack_frame):
    Logger.log_info('Gracefully exiting')

    # Get singleton of bot
    bot = CurryBot()

    sys.exit(0)


def main():
    '''
    Main function.
    Loads the config and starts the bot.
    '''
    if len(sys.argv) == 1:
        print('Please specify the config file')
        exit(-1)

    if len(sys.argv) == 3:
        Cache.set_cipher_pwd(sys.argv[2])

    curry_bot = CurryBot()
    with open(sys.argv[1], "r") as config_file:
        loader = ConfigLoader(config_file)
        loader.apply_config(curry_bot)
    
    # Gracefully handle kill
    signal(SIGTERM, sigterm_handler)

    curry_bot.start()

if __name__ == '__main__':
    main()
