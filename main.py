import asyncio
from telethon import TelegramClient

api_id = 6
api_hash = 'eb06d4abfb49ad3eeb1aeb98ae0f581e'
bot_token = '8411624697:AAFvOz2GmTwTslHVQ592H6ayqDhtxnR6L-s'

async def main():
    client = TelegramClient(None, api_id, api_hash)
    try:
        await client.start(bot_token=bot_token)
        me = await client.get_me()
        print(f"SUCCESS! Connected as: {me.username}")
    except Exception as e:
        print(f"STILL ERROR: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
