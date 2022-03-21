# Archive Note
This repository is archived because  
* I added no new passwords anymore. New passwords adding takes so long on my weak server that it is not worth it.
* The bot is based on python 2, using an old and I believe deprecated library for communication with telegram
* Honestly, nothing of value is in this repository
* I will likely shut the bot down unannounced at some point when I feel like it.

# shiverBot

https://t.me/shi_ver_bot

13000 unique users since 09.03.2018, 236 Mio entries. (numbers from 01.09.20).

This started out as a means to get back into python syntax and learning to work with git submodules. Now it's this:
* A Telegram bot to see if your password was in the [BreachCompilation](https://www.reddit.com/r/netsec/comments/7kqpx9/recent_14_billion_password_breach_compilation_as/)
* * Group support: `/q@shi_ver_bot some@email.net`
* * Regex support: `/q test@test|(?i)alri` will perform a case-insensitive search and instead a wall of results will only return `test@test.net:!Alright1`
* An easy way to put some text _above_ an image - cross-platform. Using [MakeAboveMeme](https://github.com/lucidBrot/MakeAboveMeme)
* * Input sanitizing in a way that html tags except for <br> will be displayed as entered
* * Option for empty title or text by using `.`
* * Option for only a dot as text or title by using `\.`
* * * If you wanted `\.` as text, you're out of luck

Requirements to build it yourself, in case you want to use my structure as a template for your own bot:
```
pip install telepot
pip install pyyaml
```
