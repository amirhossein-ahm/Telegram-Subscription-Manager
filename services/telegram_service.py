from telethon import TelegramClient

from config import Config


class TelegramService:

    async def get_messages(self, channel_name, limit=300):

        client = TelegramClient(Config.TELEGRAM_SESSION, Config.API_ID, Config.API_HASH)

        try:

            await client.connect()

            messages = []

            async for msg in client.iter_messages(channel_name, limit=limit):

                if msg.text:

                    messages.append(msg.text)

            return messages

        finally:

            await client.disconnect()


telegram_service = TelegramService()
