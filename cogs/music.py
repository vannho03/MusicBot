import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import asyncio

# 1. Cấu hình YoutubeDL (Để tải link nhạc)
# 1. Cấu hình YoutubeDL (Đã thêm Cookies)
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'cookiefile': 'cookies.txt',  # <--- DÒNG MỚI QUAN TRỌNG NHẤT
}

# 2. Cấu hình FFmpeg (Để xử lý âm thanh)
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

# Class xử lý nguồn phát nhạc
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # Nếu là playlist, lấy bài đầu tiên
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="play", description="Phát nhạc từ YouTube (Gõ tên hoặc Link)")
    async def play(self, interaction: discord.Interaction, search: str):
        # Kiểm tra user có trong kênh voice chưa
        if not interaction.user.voice:
            await interaction.response.send_message("❌ Bạn phải vào kênh Voice trước!", ephemeral=True)
            return

        # Báo hiệu bot đang xử lý (Defer) để tránh timeout
        await interaction.response.defer()

        try:
            # Kết nối vào kênh voice của user
            channel = interaction.user.voice.channel
            if interaction.guild.voice_client is None:
                await channel.connect()
            elif interaction.guild.voice_client.channel != channel:
                await interaction.guild.voice_client.move_to(channel)
            
            voice_client = interaction.guild.voice_client

            # Nếu đang phát bài khác thì dừng lại
            if voice_client.is_playing():
                voice_client.stop()

            # Tải và phát nhạc (Stream trực tiếp không cần tải file về máy)
            async with interaction.channel.typing():
                player = await YTDLSource.from_url(search, loop=self.bot.loop, stream=True)
                voice_client.play(player, after=lambda e: print(f'Lỗi Player: {e}') if e else None)
            
            await interaction.followup.send(f'🎶 Đang phát: **{player.title}**')

        except Exception as e:
            await interaction.followup.send(f"❌ Có lỗi xảy ra: {e}")
            print(e)

    @app_commands.command(name="stop", description="Dừng nhạc và đuổi bot ra")
    async def stop(self, interaction: discord.Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("👋 Đã dừng nhạc. Tạm biệt!")
        else:
            await interaction.response.send_message("❌ Bot có đang trong kênh voice nào đâu?", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Music(bot))