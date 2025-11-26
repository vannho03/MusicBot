import discord
import os
import asyncio
import json
from discord.ext import commands
from dotenv import load_dotenv

# 1. Load Token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 2. Cấu hình Bot
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None, application_id=None)

    async def setup_hook(self):
        # Tự động tạo folder data
        if not os.path.exists('./data'):
            os.makedirs('./data')
        
        # Tự động tạo users.json
        if not os.path.exists('./data/users.json'):
            with open('./data/users.json', 'w') as f:
                json.dump({}, f)

        # Load cogs
        print("--- ⚙️ Đang tải Modules... ---")
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"✅ Đã tải: {filename}")
                except Exception as e:
                    print(f"❌ Lỗi tải {filename}: {e}")
        
        # Sync lệnh slash
        print("--- 🔄 Đang đồng bộ lệnh... ---")
        try:
            synced = await self.tree.sync()
            print(f"✅ Đã đồng bộ {len(synced)} lệnh Slash Command!")
        except Exception as e:
            print(f"❌ Lỗi đồng bộ: {e}")

    async def on_ready(self):
        print(f"--- 🚀 Bot đã online: {self.user} ---")
        await self.change_presence(activity=discord.Game(name="/gacha | LoL Music"))

bot = MyBot()

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ LỖI: Chưa có Token trong file .env")