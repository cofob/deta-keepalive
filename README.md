# Bypass [Deta](https://deta.sh/)'s limit of 10 seconds of Micro execution.

⚠️ Be careful! It may be considered as an abusive service and you can be banned! THE AUTHOR DOES NOT TAKE ANY RESPONSIBILITY. ⚠️

![Telegram example](https://bin.frsqr.xyz/5a7e26d4-7f5d-4e2c-80f5-95fbfcb23bf7)

![Deta Base view](https://bin.frsqr.xyz/63820b6f-e755-440e-8d38-221f77e2abda)

## How it works?

Micro starts itself and by communicating through the database it runs only 1 copy.

When you run `Pinger.run()` it blocks main thread and waiting for the completion of the other Micro

## Quickstart

1. Create new python Micro
2. Disable auth on it (`deta auth disable`)
3. Add `deta-keepalive` to `requirements.txt`
4. Write code!

### How I can stop this?

Simply enable auth back `deta auth enable`.

## Examples

> See "examples" folder.

### [Telegram bot](examples/telegrambot/main.py)

```python
from deta_keepalive import Pinger
import telebot
import deta
import os

bot = telebot.TeleBot("your token here")
pinger = Pinger(deta.Deta(os.environ["DETA_PROJECT_KEY"]))


@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, f"Hello from Deta!")


def app(event):
    pinger.run()
    bot.polling(none_stop=True, interval=0)
```

### Run other Micro (Node.js, for example)

```python
from deta_keepalive import Pinger
from requests import get
import deta
import os


def app(event):
    pinger = Pinger(deta.Deta(os.environ["DETA_PROJECT_KEY"]))
    pinger.run()
    get("https://somemicroname.deta.dev/")
```
