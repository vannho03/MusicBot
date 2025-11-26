import discord
from discord import app_commands
from discord.ext import commands
import json
import random
import os

class Gacha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cards_path = './data/cards.json'
        self.users_path = './data/users.json'

    # --- HÀM HỖ TRỢ ---
    def load_json(self, path):
        if not os.path.exists(path):
            return [] if 'cards' in path else {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return [] if 'cards' in path else {}

    def save_users(self, data):
        with open(self.users_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_user_data(self, user_id):
        users = self.load_json(self.users_path)
        str_id = str(user_id)
        if str_id not in users:
            users[str_id] = {"gold": 1000, "inventory": []}
            self.save_users(users)
        return users, str_id

    # --- LỆNH GACHA (CÓ TRỪ TIỀN) ---
    @app_commands.command(name="gacha", description="Quay tướng (Giá: 100 vàng/lượt)")
    async def gacha(self, interaction: discord.Interaction):
        # 1. Load Data
        cards = self.load_json(self.cards_path)
        if not cards:
            await interaction.response.send_message("❌ Admin chưa chạy tool crawl_lol.py!", ephemeral=True)
            return
            
        users, user_id = self.get_user_data(interaction.user.id)
        
        # 2. KIỂM TRA TIỀN
        current_gold = users[user_id].get('gold', 0)
        PRICE = 100 # Giá quay
        
        if current_gold < PRICE:
            await interaction.response.send_message(f"💸 **Nghèo quá!** Bạn cần **{PRICE} vàng** để quay (Đang có: {current_gold}).\nDùng `/daily` hoặc `/work` để kiếm tiền đi!", ephemeral=True)
            return
        
        # 3. Trừ tiền
        users[user_id]['gold'] -= PRICE
        
        # 4. Random thẻ (Có trọng số - Weighted Random)
        # Tỷ lệ: UR(2), SSR(5), SR(15), R(30), N(48)
        weights = []
        for c in cards:
            r = c.get('rarity', 'N')
            if r == 'UR': w = 2
            elif r == 'SSR': w = 5
            elif r == 'SR': w = 15
            elif r == 'R': w = 30
            else: w = 48
            weights.append(w)
            
        card = random.choices(cards, weights=weights, k=1)[0]
        
        # 5. Lưu vào túi đồ
        users[user_id]['inventory'].append(card['id'])
        self.save_users(users)

        # 6. Hiển thị kết quả
        embed = discord.Embed(
            title=f"✨ {interaction.user.name} triệu hồi!",
            description=f"Tiêu tốn: **{PRICE} vàng**\nNhận được: **{card['name']}** - {card['title']}",
            color=card.get('color', 0xFFFFFF)
        )
        embed.set_image(url=card['image_url'])
        embed.add_field(name="Độ hiếm", value=f"**{card.get('rarity', 'N')}**", inline=True)
        embed.add_field(name="Sức mạnh", value=f"⚔️ {card.get('atk', 0)}", inline=True)
        embed.set_footer(text=f"Số dư còn lại: {users[user_id]['gold']} vàng")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="inventory", description="Xem chi tiết túi đồ")
    async def inventory(self, interaction: discord.Interaction):
        # 1. Load dữ liệu
        users, user_id = self.get_user_data(interaction.user.id)
        inventory_ids = users[user_id]['inventory']
        
        if not inventory_ids:
            await interaction.response.send_message("🎒 Túi đồ trống trơn! Hãy đi Gacha ngay.", ephemeral=True)
            return

        # 2. Load thông tin tướng để lấy Tên thật từ ID
        cards = self.load_json(self.cards_path)
        # Tạo từ điển để tra cứu nhanh: "yasuo" -> "Yasuo"
        # Nếu data chưa crawl đủ thì dùng ID tạm
        id_to_name = {c['id']: c['name'] for c in cards}

        # 3. Đếm số lượng (Ví dụ: Yasuo x2, Zed x1)
        from collections import Counter
        counts = Counter(inventory_ids)

        # 4. Tạo danh sách hiển thị
        description = ""
        # Sắp xếp theo tên cho đẹp (A->Z)
        sorted_items = sorted(counts.items(), key=lambda x: id_to_name.get(x[0], x[0]))

        for card_id, count in sorted_items:
            # Lấy tên tướng, nếu lỗi data thì hiện ID tạm
            name = id_to_name.get(card_id, f"Unknown ({card_id})") 
            description += f"🔹 **{name}** `x{count}`\n"

        # 5. Kiểm tra giới hạn tin nhắn Discord (4096 ký tự)
        if len(description) > 4000:
            description = description[:3900] + "\n\n... (Túi đầy quá, không hiện hết được!)"

        # 6. Gửi Embed
        embed = discord.Embed(
            title=f"🎒 Túi đồ của {interaction.user.name}",
            description=description,
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Tổng tài sản: {len(inventory_ids)} thẻ")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Gacha(bot))