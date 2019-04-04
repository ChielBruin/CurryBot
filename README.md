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
        "commands": ["hmmm"],
        "messageRegex": "[Hh][mM]+(\\s.*)?$",
        "replies": {
            "stickers" : [{"pack": "thonkang", "exclude":["<sticker_id>"]}]
        },
        "amount" : 1,
        "transitiveReply": true,
        "replyTo": "all"
    },
}
```

- `api-token`*: The Telegram api-token of the bot
- `<action name>` A name for this reply action
  - `commands`*: A list of commands that trigger this action
  - `messageRegex`*: A regex that if it matches (from the start of a message) will trigger the action
  - `replies`: The possible replies for this action, can be both messages and stickers
    - `stickers`*: 
      - `pack`: The ids of the Telegram sticker pack to select stickers from
      - `include`*: whitelisted sticker IDs 
      - `exclude`*: blackliste sticker IDs 
    - `messages`*: Messages that can be used as a reply. Messages can be templated using `\\<INT>` to insert matched groups from the original message.
  - `amount`: The amount of stickers to reply
  - `transitiveReply`: Whether replying with a trigger will reply to the original message (`true`), or the reply that triggered the action (`false`)
  - `replyTo`: Specify what type of messages should trigger this action. Can be either `replies` (only replies), `messages` (only non-reply messages) or `all`

*) Optional
