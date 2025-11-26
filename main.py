import discord
import os
import asyncio
import json
from discord.ext import commands
from dotenv import load_dotenv

# --- PHẦN MỚI: GIỮ BOT SỐNG TRÊN RENDER ---
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_server():
    # Render yêu cầu chạy trên port 10000 hoặc biến môi trường PORT
    port = int(os.environ.get("PORT", 8000))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, SimpleHandler)
    print(f"🌍 Fake Web Server đang chạy port {port}")
    httpd.serve_forever()

Thread(target=run_server).start()
# ------------------------------------------

# 1. Load Token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 2. Cấu hình Bot
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True # Quan trọng cho nhạc

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None, application_id=None)

    async def setup_hook(self):
        # Tự động tạo folder data
        if not os.path.exists('./data'): os.makedirs('./data')
        if not os.path.exists('./data/users.json'):
            with open('./data/users.json', 'w') as f: json.dump({}, f)

        # Load cogs
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        
        await self.tree.sync()

    async def on_ready(self):
        print(f"--- 🚀 Bot đã online: {self.user} ---")
        await self.change_presence(activity=discord.Game(name="/gacha | LoL Music"))

bot = MyBot()

if __name__ == "__main__":
    bot.run(TOKEN)
