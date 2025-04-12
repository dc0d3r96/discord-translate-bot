import discord
from discord.ext import commands
from discord import app_commands, Interaction, ui
from deep_translator import GoogleTranslator
import json
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DIL_DOSYASI = "dil_ayarlari.json"

def kullanici_dil_getir(user_id):
    try:
        with open(DIL_DOSYASI, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(str(user_id), "en")
    except:
        return "en"

def kullanici_dil_kaydet(user_id, dil_kodu):
    try:
        with open(DIL_DOSYASI, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {}

    data[str(user_id)] = dil_kodu
    with open(DIL_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

class TranslateView(ui.View):
    def __init__(self, message_content):
        super().__init__(timeout=None)
        self.message_content = message_content

    @ui.button(label="Tercüme Et", style=discord.ButtonStyle.primary, custom_id="translate_button")
    async def translate(self, interaction: Interaction, button: ui.Button):
        hedef_dil = kullanici_dil_getir(interaction.user.id)
        try:
            ceviri = GoogleTranslator(source='auto', target=hedef_dil).translate(self.message_content)
            await interaction.response.send_message(f"**Çeviri ({hedef_dil}):** {ceviri}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("Çeviri yapılamadı.", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Bot aktif: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Slash komutları senkronize edildi: {len(synced)} komut")
    except Exception as e:
        print(f"Hata oluştu: {e}")

@bot.tree.command(name="dil-ayarla", description="Kendi dilini ayarla (örnek: tr, en, sk, de...)")
@app_commands.describe(dil="Dil kodunu gir (örnek: en, tr, sk)")
async def dil_ayarla(interaction: Interaction, dil: str):
    kullanici_dil_kaydet(interaction.user.id, dil)
    await interaction.response.send_message(f"Dil ayarın **{dil}** olarak kaydedildi.", ephemeral=True)

@bot.event
async def on_message(message):
    if message.author == bot.user or message.content.startswith("/"):
        return

    view = TranslateView(message.content)
    try:
        await message.channel.send(f"{message.author.mention} bir mesaj yazdı.", view=view)
    except Exception as e:
        print(f"Hata: {e}")

bot.run(TOKEN)
