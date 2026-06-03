from telethon import TelegramClient

from config import Config


async def main():

    client = TelegramClient(Config.TELEGRAM_SESSION, Config.API_ID, Config.API_HASH)

    await client.start()

    me = await client.get_me()

    print()
    print("===================================")
    print(" Telegram Login Successful")
    print("===================================")
    print(f"Name: {me.first_name}")

    if me.username:
        print(f"Username: @{me.username}")

    print(f"User ID: {me.id}")
    print()
    print("Session saved to:")
    print(f"{Config.TELEGRAM_SESSION}.session")
    print()

    await client.disconnect()


if __name__ == "__main__":

    Config.validate()

    import asyncio

    asyncio.run(main())
