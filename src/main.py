import sys, json

from bot import CurryBot


def main():
    '''
    Main function.
    Loads the config and starts the bot.
    '''
    if len(sys.argv) == 1:
        print('Please specify the config file')
        exit(-1)

    config = {}
    with open(sys.argv[1], "r") as config_file:
        config = json.load(config_file)

    curry_bot = None
    if 'telegram-api-token' in config:
        curry_bot = CurryBot(config['telegram-api-token'])
    elif len(sys.argv) > 2:
        curry_bot = CurryBot(sys.argv[2])
    else:
        token = input('What is your Telegram API token?\n')
        curry_bot = CurryBot(token)

    update_bot_config(curry_bot, config)
    curry_bot.start()


def update_bot_config(bot, config):
    '''
    For each action in the config, create/update the actions config.
    '''
    #TODO: The message and ommand handlers should be removed when updating
    for action in config:
        if 'api-token' in action:
            bot.add_api_key(action[:-10], config[action])
            continue

        action_config = config[action]
        print('Initializing action %s' % action)
        bot.config_action(action, action_config)
    print('All actions initialized')

if __name__ == '__main__':
    main()
