# CurryBot
A telegram bot that replies with stickers to commands or certain messages.  
These stickers are selected randomly from given stickerpacks.

## Usage
```bash
python3 src/main.py example_config.json
```
Note that if you want the bot to reply to messages matching a given regex, 'privacy mode' should be disabled.

### Initial Config
The bot has two types of configurations.
The first is is stored in a JSON-file that is provided when the bot is launched.
This file contains the essential information that is needed to Initialize the bot.

In this file 3 required fields must be specified:
- The Telegram API token of the bot
- The directory where the bot will store its configuration and cache
- The encryption key used for encrypting certain secret information (like API-keys) when writing to disk
Optionally a Telegram chat can be configured to be the admin chat of the bot.
Members of this chat can be assigned to update the configuration of global actions and the bot will post errors directly to this chat.

```json
{
  "API-token": "<API-Token here>",
  "cache-dir": "cache",
  "encryption-key": "VerySecretKey",
  "admin-chat": <chat-id>
}
```

### Configuring the bot
Adding actions to the bot is done by starting a conversation with the bot in a private chat.
This conversation is initiated by sending the `/config`-command.
In this conversation the bot gives you the choice to add, remove or edit an action in a chat where you are assigned admin of the bot.
When adding the bot to a chat, you are automatically assigned admin and are therefore able to configure the behaviour of the bot in that chat.
A new admin is added when a user that is already an admin replies `/makeadmin` to a message from the user this will be added.

An action is created by constructing a tree of handlers where each handler could filter on the content of the message or perform an action like sending a message.
A handler can propagate a message to its children, creating more complex behaviour (for example: message is a reply __and__ message is a command __and__ today is a Monday __then__ send a sticker).
Possible filters and actions include (among others):
- Matching the message with a regex
- Filtering based on the current time
- Monitoring user or chat activity
- Filtering on inactivity
- Sending a picture from a Flickr album
- Sending a sticker
- Forwarding a message
- Adding a video to a Youtube playlist
- Voting on messages
- Sending items from RSS feeds
