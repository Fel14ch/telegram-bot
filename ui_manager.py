import asyncio

class UIManager:
    def __init__(self):
        self.messages = {}

    async def send(self, bot, chat_id, text, **kwargs):
        msg = await bot.send_message(chat_id, text, **kwargs)
        self.messages.setdefault(chat_id, []).append(msg.message_id)
        return msg

    async def clear(self, bot, chat_id):
        for msg_id in self.messages.get(chat_id, []):
            try:
                await bot.delete_message(chat_id, msg_id)
            except:
                pass
        self.messages[chat_id] = []

    async def auto_delete(self, bot, chat_id, msg_id, delay):
        await asyncio.sleep(delay)
        try:
            await bot.delete_message(chat_id, msg_id)
        except:
            pass

ui = UIManager()
