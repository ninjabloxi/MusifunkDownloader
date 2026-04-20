import discord
from discord.ext import commands
import yt_dlp
import aiohttp
import asyncio
import os
import tempfile
import shutil
from pathlib import Path

# ──────────────────────────────────────────
# CONFIG (REMPLACE ICI)
# ──────────────────────────────────────────
BOT_TOKEN = "MTQ5NTgwMDAwMDgzODYzMTcxNA.GQiK5C.PEg4EH64zL153s-2JztAjDqpVFWZjoQyqVWA-Q"

SPOTIFY_CLIENT_ID = "522eb68818d84450bf03dee246b91fd0"
SPOTIFY_CLIENT_SECRET = "afabdc3d3c83408294c0317c59f2c8ab"

MAX_FILE_SIZE_MB = 25
DOWNLOAD_DIR = tempfile.mkdtemp()

# ──────────────────────────────────────────
# INTENTS
# ──────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)


# ──────────────────────────────────────────
# DETECTION SOURCE
# ──────────────────────────────────────────
def detect_source(url: str):
    u = url.lower()

    if "youtube.com" in u or "youtu.be" in u:
        return "YouTube", "🎬"
    if "open.spotify.com" in u:
        return "Spotify", "🟢"
    if "soundcloud.com" in u:
        return "SoundCloud", "🔶"
    if "deezer.com" in u:
        return "Deezer", "🎵"
    if u.endswith(".mp3"):
        return "Direct MP3", "🔗"

    return "Source inconnue", "🌐"


# ──────────────────────────────────────────
# YT-DLP DOWNLOAD
# ──────────────────────────────────────────
async def download_ytdlp(url: str, out_dir: str) -> str:
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(out_dir, "%(title)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
        "no_warnings": True,
    }

    loop = asyncio.get_event_loop()

    def _run():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)
            return str(Path(file).with_suffix(".mp3"))

    return await loop.run_in_executor(None, _run)


# ──────────────────────────────────────────
# DIRECT DOWNLOAD
# ──────────────────────────────────────────
async def download_direct(url: str, out_dir: str) -> str:
    filename = url.split("/")[-1].split("?")[0]
    if not filename.endswith(".mp3"):
        filename += ".mp3"

    path = os.path.join(out_dir, filename)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"HTTP {resp.status}")

            with open(path, "wb") as f:
                while True:
                    chunk = await resp.content.read(1024 * 64)
                    if not chunk:
                        break
                    f.write(chunk)

    return path


# ──────────────────────────────────────────
# SPOTIFY SAFE HANDLING
# ──────────────────────────────────────────
async def handle_spotify(url: str):
    # Spotify ne permet pas le téléchargement direct
    return url


# ──────────────────────────────────────────
# COMMAND
# ──────────────────────────────────────────
@bot.tree.command(
    name="mdownload",
    description="Télécharge un audio depuis YouTube / SoundCloud / lien direct"
)
async def mdownload(interaction: discord.Interaction, lien: str):
    await interaction.response.defer(thinking=True)

    job_dir = tempfile.mkdtemp(dir=DOWNLOAD_DIR)

    try:
        platform, emoji = detect_source(lien)

        # Spotify bloqué proprement
        if "open.spotify.com" in lien:
            embed = discord.Embed(
                title="🟢 Spotify détecté",
                description="Spotify ne permet pas le téléchargement direct.\nUtilise un lien YouTube équivalent.",
                color=0x1DB954
            )
            embed.add_field(name="Lien", value=lien, inline=False)

            await interaction.followup.send(embed=embed)
            return

        # MP3 direct
        if lien.endswith(".mp3"):
            path = await download_direct(lien, job_dir)
        else:
            try:
                path = await download_ytdlp(lien, job_dir)
            except Exception:
                path = await download_direct(lien, job_dir)

        # Taille
        size_mb = os.path.getsize(path) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            await interaction.followup.send(
                f"⚠️ Fichier trop lourd ({size_mb:.1f} Mo)"
            )
            return

        filename = os.path.basename(path)

        embed = discord.Embed(
            title="✅ Téléchargement terminé",
            color=0x00ff99
        )
        embed.add_field(name="Source", value=f"{emoji} {platform}", inline=True)
        embed.add_field(name="Taille", value=f"{size_mb:.2f} Mo", inline=True)
        embed.add_field(name="Fichier", value=f"`{filename}`", inline=False)

        await interaction.followup.send(
            embed=embed,
            file=discord.File(path, filename=filename)
        )

    except Exception as e:
        embed = discord.Embed(
            title="❌ Erreur",
            description=str(e),
            color=0xff4444
        )
        await interaction.followup.send(embed=embed)

    finally:
        shutil.rmtree(job_dir, ignore_errors=True)


# ──────────────────────────────────────────
# READY
# ──────────────────────────────────────────
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot connecté : {bot.user}")


bot.run(BOT_TOKEN)