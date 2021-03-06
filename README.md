# CurryBot
A telegram bot that replies with stickers to commands or certain messages.  
These stickers are selected randomly from given stickerpacks.

## Usage
```bash
python src/main.py example_config.json
```
or
```bash
python src/main.py my_config.json <API-TOKEN>
```
Note that if you want the bot to reply to messages matching a given regex, 'privacy mode' should be disabled.

### Config
```json
{
    "api-token": "<API-TOKEN here>",
    "Hmmm": {
        "triggers": {
            "commands": ["hmmm"],
            "Regex": ["[Hh][mM]+(\\s.*)?$"]
        },
        "replies": {
            "stickers" : [{"pack": "thonkang", "exclude":["<sticker_id>"]}]
        },
        "amount" : 1,
        "accuracy": 0.9,
        "replyBehaviour": {
            "message": "reply -> send*",
            "reply": "transitiveReply -> send*",
        },
    },
}
```

- `telegram-api-token`*: The Telegram api-token of the bot
- `flickr-api-token`*: The Flickr api-token of the bot
- `<action name>`: A name for this reply action
  - `triggers`: Configure what triggers a reply
    - `commands`*: A list of commands that trigger this action
    - `messageRegex`*: A list of regexes that if it matches (from the start of a message) will trigger the action
    - `url`*: A list of (parts of) urls that trigger this action
    - `audio`*: boolean whether to trigger this action (`false` by default)
    - `video`*: boolean whether to trigger this action (`false` by default)
    - `image`*: boolean whether to trigger this action (`false` by default)
    - `contact`*: boolean whether to trigger this action (`false` by default)
    - `document`*: boolean whether to trigger this action (`false` by default)
    - `sticker`*: boolean whether to trigger this action (`false` by default)
    - `voice`*: boolean whether to trigger this action (`false` by default)
  - `replies`: The possible replies for this action, can be both messages and stickers
    - `stickers`*:
      - `pack`: The id of the Telegram sticker pack to select stickers from
      - `include`*: whitelisted sticker IDs
      - `exclude`*: blacklisted sticker IDs
    - `messages`*: List of messages that can be used as a reply. Messages can be templated using `\\<INT>` to insert matched groups from the original message.
    - `flickr_images`*:
      - `imageset`: The id of the Flickr album to select pictures from
      - `include`*: whitelisted image IDs
      - `exclude`*: blacklisted image IDs
    - `forward`*:
      - `chat_id`: The id of the chat the message is from
      - `message_id`: The id of the message in that chat
  - `amount`: The amount of stickers to reply
  - `accuracy`*: The chance that a trigger will result in a reply. Can be either a number between 0 an 1, or a percentage (e.g. "25%")
  - `chats`*: Whitelist or blacklist certain chats
    - `include`*: List of chat_ids to whitelist
    - `exclude`*: List of chat_ids to blacklist
  - `replyBehaviour`: The behaviour for replying to given message types. The behaviour is a list of actions separated by `->`, where valid actions are `reply`, `transitiveReply`, `send` and `none`.
    - `message`*: Rule used for normal messages
    - `reply`*: Rule used for replies
    - `forward`*: Rule used for forwarded messages


*) Optional

Use the `/info` command to print the current chat_id to console.
If this command is replied to a sticker, the sticker_id and stickerset_id will be displayed as well.
