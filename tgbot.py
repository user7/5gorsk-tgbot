#!/bin/env python3

import asyncio
import telegram

async def main():
    token = ""
    with open('token.txt') as f:
        token = f.readline().rstrip()
    print("token {t}".format(t = token))
    bot = telegram.Bot(token)
    async with bot:
        print(await bot.get_me())

if __name__ == '__main__':
    asyncio.run(main())
