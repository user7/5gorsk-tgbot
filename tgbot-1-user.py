#!/bin/env python3

import asyncio
import telegram

savedToken = ''
def getToken():
    global savedToken
    if savedToken == '':
        with open('token.txt') as f:
            savedToken = f.readline().rstrip()
    return savedToken

async def main():
    token = getToken()
    print("token {t}".format(t = token))
    bot = telegram.Bot(token)
    async with bot:
        print(await bot.get_me())

if __name__ == '__main__':
    asyncio.run(main())
