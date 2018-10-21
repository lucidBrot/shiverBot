# shiverBot
This started out as a means to get back into python syntax and learning to work with git submodules. Now it's this:
* A Telegram bot to see if your password was in the [BreachCompilation](https://www.reddit.com/r/netsec/comments/7kqpx9/recent_14_billion_password_breach_compilation_as/)
* * Group support: `/q@shi_ver_bot some@email.net`
* * Regex support: `/q test@test|(?i)alri` will perform a case-insensitive search and instead a wall of results will only return `test@test.net:!Alright1`
* An easy way to put some text _above_ an image - cross-platform. Using [MakeAboveMeme](https://github.com/lucidBrot/MakeAboveMeme)
* * Input sanitizing in a way that html tags except for <br> will be displayed as entered
* * Option for empty title or text by using `.`
* * Option for only a dot as text or title by using `\.`
* * * If you wanted `\.` as text, you're out of luck

https://t.me/shi_ver_bot

823 unique users since 09.03.2018 (number from 05.10.18), and before that about another 30 but not rigorously counted.

Requirements to build it yourself, in case you want to use my structure as a template for your own bot:
```
pip install telepot
pip install pyyaml
```
