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
Note that if you want the bot to reply to messages matching a given regex, 'privacy mode' should be enabled.

### Config
```json
{
    "api-token": "<API-TOKEN here>",
    "Hmmm": {
        "commands": ["Hmmm"],
        "messageRegex": "[Hh][mM]+(\\s.*)?$",
        "packs" : ["thonkang"],
        "amount" : 1,
        "transitiveReply": true
    }
}
```

- `api-token`*: The Telegram api-token of the bot
- `commands`*: A list of commands that trigger this action
- `messageRegex`*: A regex that if it matches (from the start of a message) will trigger the action
- `packs`: The ids of the Telegram sticker packs to select stickers from
- `amount`: The amount of stickers to reply
- `transitiveReply`: Whether replying with a trigger will reply to the original message (`true`), or the reply that triggered the action (`false`)

*) Optional
