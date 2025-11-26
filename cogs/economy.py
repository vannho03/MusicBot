import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import random
import time

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users_path = './data/users.json'

    def get_data(self):
        with open(self.users_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_data(self, data):
        with open(self.users_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def update_balance(self, user_id, amount):
        data = self.get_data()
        uid = str(user_id)
        if uid not in data:
            data[uid] = {"gold": 0, "inventory": []}
        
        # Cộng/Trừ tiền (amount có thể âm)
        data[uid]['gold'] = data[uid].get('gold', 0) + amount
        self.save_data(data)
        return data[uid]['gold']

    # --- LỆNH KIẾM TIỀN ---

    @app_commands.command(name="daily", description="Điểm danh nhận 500 vàng (Mỗi 24h)")
    async def daily(self, interaction: discord.Interaction):
        # (Ở đây có thể thêm check thời gian cooldown, nhưng tạm bỏ qua để test cho nhanh)
        new_bal = self.update_balance(interaction.user.id, 500)
        await interaction.response.send_message(f"☀️ **Điểm danh!** Bạn nhận được **500 vàng**. (Số dư: {new_bal})")

    @app_commands.command(name="work", description="Làm việc kiếm tiền ngẫu nhiên")
    async def work(self, interaction: discord.Interaction):
        earnings = random.randint(50, 200)
        new_bal = self.update_balance(interaction.user.id, earnings)
        
        jobs = ["đi rửa bát thuê", "code dạo", "bán trà đá", "đi rừng gank team", "ks mạng của AD"]
        job = random.choice(jobs)
        
        await interaction.response.send_message(f"🔨 Bạn đã **{job}** và kiếm được **{earnings} vàng**. (Số dư: {new_bal})")

    @app_commands.command(name="balance", description="Xem ví tiền")
    async def balance(self, interaction: discord.Interaction):
        data = self.get_data()
        bal = data.get(str(interaction.user.id), {}).get('gold', 0)
        await interaction.response.send_message(f"💰 Ví của {interaction.user.name}: **{bal} vàng**")

async def setup(bot):
    await bot.add_cog(Economy(bot))