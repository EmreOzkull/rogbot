# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 19:13:32 2023
"""

import discord
from discord.ext import commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import nest_asyncio
import asyncio
import datetime
import requests


TOKEN = "OTQ0MTI1NjE4MDE3MTQ4OTg4.GrnuRV.Dt38blE0-4NX8RTU-ctaf6g2KN1CRcZY0Tin4k"
SPREADSHEET_NAME = 'ROGTablo'
CREDENTIALS_FILE = 'credentials.json'

GUILD_ID = 794743413345615903

YETKILI_ROLE_ID = 804097764862066728
SAVASA_HAZIR_ROLE_ID = 794925707276582932  # Savaşa Hazır rolünün ID'sini buraya girin

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
nest_asyncio.apply()  # nest_asyncio'yu etkinleştirin



@bot.event
async def on_ready():
    print('Bot is ready.')
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        error_message = await ctx.send("Geçersiz Yetki. Lütfen Ekip Sorumlularıyla iletişime geçin.\n BU MESAJ 3 SANİYE SONRA SİLİNECEKTİR!")
        await asyncio.sleep(3)  # 3 saniye bekle

        # Botun ve kullanıcının mesajlarını sil
        await ctx.message.delete()
        await error_message.delete()

@bot.command()
@commands.has_role(YETKILI_ROLE_ID)  # Yetkili rol ID'sini buraya girin
async def add_data(ctx, *, data):
    # Hizmet hesabı kimlik doğrulama bilgilerini yükle
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE)

    # Kimlik doğrulama bilgileriyle gspread'e yetkilendirme yap
    client = gspread.authorize(credentials)

    # Veri eklemek istediğiniz tabloyu seçin
    spreadsheet = client.open(SPREADSHEET_NAME)
    worksheet = spreadsheet.get_worksheet(0)  # İlk çalışma sayfasını seçin

    # Verileri tabloya ekleyin
    data_list = data.split(',')
    worksheet.append_row(data_list)

    await ctx.send('Veri başarıyla eklendi.')

@bot.command()
@commands.has_role(YETKILI_ROLE_ID)  # Yetkili rol ID'sini buraya girin
async def bilgigir(ctx, ad, karakterad, karaktersinif, numara):

    # Hizmet hesabı kimlik doğrulama bilgilerini yükle
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE)

    # Kimlik doğrulama bilgileriyle gspread'e yetkilendirme yap
    client = gspread.authorize(credentials)

    # Veri eklemek istediğiniz tabloyu seçin
    spreadsheet = client.open(SPREADSHEET_NAME)
    worksheet = spreadsheet.get_worksheet(0)  # İlk çalışma sayfasını seçin

    # Mevcut son satırın indeksini bulun
    last_row = len(worksheet.get_all_values()) + 1

    # Kullanıcının etiketlediği kullanıcıları alın
    mentioned_users = ctx.message.mentions

    # İlk etiketlenen kullanıcının ID'sini alın
    user_id = str(mentioned_users[0].id) if mentioned_users else None

    # Eğer kullanıcı ID'si tabloda varsa mesaj gönder
    if find_user(worksheet, user_id):
        await ctx.send("Bu kişi daha önce dosyaya eklenmiş.")
        return

    # Kullanıcının adını değiştirin
    member = mentioned_users[0]
    new_nickname = f"⌊ ૨σɢ ზ ⌉ {ad} & {karakterad}"
    await member.edit(nick=new_nickname)

    # Verileri tabloya yeni satır olarak ekleyin
    data_list = [ad, karakterad, karaktersinif, "+90 " + numara, user_id]
    worksheet.insert_row(data_list, last_row)

    # Kullanıcıyı etiketleyin
    member = ctx.message.author
    await ctx.send(f"Veri başarıyla eklendi. {member.mention}")

    # Veri tablosunu güncelleyin
    worksheet.update('A:Z', worksheet.get_all_values())



@bot.command()
@commands.has_role(YETKILI_ROLE_ID)  # Yetkili rol ID'sini buraya girin
async def savasahazır(ctx):
    # Kullanıcının etiketlediği kullanıcıları alın
    mentioned_users = ctx.message.mentions

    # Eğer etiketlenen kullanıcı yoksa hata mesajı gönderin
    if not mentioned_users:
        await ctx.send("Lütfen savaşa hazır rolü vermek istediğiniz bir kullanıcıyı etiketleyin.")
        return

    # İlk etiketlenen kullanıcıyı seçin
    user = mentioned_users[0]

    # Savaşa hazır rolünü alın
    savaşa_hazır_role = discord.utils.get(ctx.guild.roles, id=SAVASA_HAZIR_ROLE_ID)
    

    # Kullanıcıya savaşa hazır rolünü verin
    await user.add_roles(savaşa_hazır_role)

    # Hizmet hesabı kimlik doğrulama bilgilerini yükle
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE)

    # Kimlik doğrulama bilgileriyle gspread'e yetkilendirme yap
    client = gspread.authorize(credentials)

    # Veri eklemek istediğiniz tabloyu seçin
    spreadsheet = client.open(SPREADSHEET_NAME)
    worksheet = spreadsheet.get_worksheet(0)  # İlk çalışma sayfasını seçin

    # Kullanıcının Discord ID'sini alın
    discord_id = str(user.id)

    # Discord ID'sini tabloda arayın ve hücrenin sağındaki hücreyi yeşile boyayın
    cell = worksheet.find(discord_id)
    row_index = cell.row
    col_index = cell.col + 1

    # Hücreye "Savaşa Hazır" yazısını yazın
    worksheet.update_cell(row_index, col_index, "Savaşa Hazır")
    green_color = discord.Colour.from_rgb(0, 255, 0)
    # Kullanıcının bulunduğu hücreyi yeşile boyayın
    cell_range = f"F{row_index}"
    worksheet.format(cell_range, {
        "backgroundColor": {
            "red": 0,
            "green": 1,
            "blue": 0
        }
    })
    
    await ctx.send(f"{user.mention} savaşa hazır rolü verildi ve tabloda işaretlendi.")

def find_user(worksheet, user_id):
# Tüm verileri alın
    data = worksheet.get_all_values()
    # Verileri dolaşarak hedef kullanıcı ID'sini içeren satırı bulun
    for i, row in enumerate(data):
        if row[4] == user_id:  # Kullanıcı ID'sinin olduğu sütunu kontrol edin
            return True
    
    return False

def find_row_by_user_id(worksheet, user_id):
    # Tüm verileri alın
    data = worksheet.get_all_values()
    # Verileri dolaşarak hedef kullanıcı ID'sini içeren satırı bulun
    for i, row in enumerate(data):
        if row[4] == user_id:  # Kullanıcı ID'sinin olduğu sütunu kontrol edin
            return i + 1  # Satır indeksini döndürün (1'e ekleyin çünkü dizin 0'dan başlar)

    return None  # Kullanıcı ID'si bulunamadıysa None döndürün

    


@bot.command()
@commands.has_role(YETKILI_ROLE_ID)  # Yetkili rol ID'sini buraya girin
async def savascagır(ctx, loncaadi, saat, katilimci):
    # Hedef rolü alın
    role = discord.utils.get(ctx.guild.roles, id=SAVASA_HAZIR_ROLE_ID)
    role_mention = role.mention
    # Savaş duyurusu mesajını oluşturun
    message = f":tr: **GENESİS HÜKÜMDARLIĞI - SAVAŞ DUYURUSU**  :tr:\n\n:genesis2: RISEOFGENESIS vs {loncaadi} :genesis2:\n\n:tik: Savaş Günü : Bugün!\n:tik: Savaş Saati : {saat}!\n:tik: Katılımcı Sayısı : {katilimci}\n\n:Verify: PERFORMANCE ekibi bu akşam yargı-infaz modumuzu açıyoruz. Tüm herkes hesabındaki eksiklerini tamamlasın.\n\n **“ BİZDE KARDEŞLİK İNANÇ GİBİDİR, İNANDIKÇA GÜVENİRSİN, GÜVENDİKÇE KAZANIRSIN ”**{role_mention}"

    # Emoji simgelerini mesajda kullanmak için Unicode kodlarına dönüştürün
    message = message.replace(":tr:", "🇹🇷").replace(":genesis2:", "🔱").replace(":tik:", "✅").replace(":Verify:", "✔️").replace(":Emoji217:", "🍬")

    # Görsel URL'si
    image_url = "https://media.discordapp.net/attachments/1110276425476489347/1116842773010718730/348462846_3470325346557354_6491076697275101802_n.jpg?width=1202&height=676"

    # Görseli Discord mesajına ekleyi
    
    # Etiketlenen rolün Discord etiketini alın
    role_mention = role.mention

    # Mesajı oluşturulan rol etiketi ve görsel ile birlikte gönderin
    await ctx.send(message)
    await ctx.send(image_url)
    


@bot.command()
@commands.has_role(YETKILI_ROLE_ID)  # Yetkili rol ID'sini buraya girin
async def toplantı(ctx):
    # Tarih ve saat bilgisini internetten çek
    response = requests.get("https://worldtimeapi.org/api/timezone/Europe/Istanbul")
    if response.status_code != 200:
        await ctx.send("Tarih ve saat bilgisini alırken bir hata oluştu.")
        return

    data = response.json()
    tarih = data["datetime"].split("T")[0]
    saat = data["datetime"].split("T")[1].split(".")[0]

    # Toplantıya katılacak kullanıcıları listele
    message = f"{tarih} tarihli {saat} saatindeki toplantıya katılan kullanıcılar:"
    voice_channel = ctx.author.voice.channel
    for index, member in enumerate(voice_channel.members, start=1):
        message += f"\n{index}. {member.mention}"

    await ctx.send(message)

@bot.command()
@commands.has_role(YETKILI_ROLE_ID)  # Yetkili rol ID'sini buraya girin
async def mute(ctx):
    # Yetkili kullanıcının bulunduğu sesli kanalı kontrol et
    voice_channel = ctx.author.voice.channel
    if voice_channel is None:
        await ctx.send("Lütfen bir sesli kanala bağlanın.")
        return
    

    # Sesli kanaldaki tüm kullanıcıları sustur
    for member in voice_channel.members:
        if member != ctx.author:
            await member.edit(mute=True)

    await ctx.send(f"{voice_channel.name} kanalındaki tüm kullanıcılar susturuldu.")
    
@bot.command()
@commands.has_role(YETKILI_ROLE_ID)  # Yetkili rol ID'sini buraya girin
async def unmute(ctx):
    # Yetkili kullanıcının bulunduğu sesli kanalı kontrol et
    voice_channel = ctx.author.voice.channel
    if voice_channel is None:
        await ctx.send("Lütfen bir sesli kanala bağlanın.")
        return
    

    # Sesli kanaldaki tüm kullanıcıları sustur
    for member in voice_channel.members:
        if member != ctx.author:
            await member.edit(mute=False)

    await ctx.send(f"{voice_channel.name} kanalındaki tüm kullanıcıların sesi açıldı.")


@bot.command()
@commands.has_role(YETKILI_ROLE_ID)  # Yetkili rol ID'sini buraya girin
async def herkesitasi(ctx):
    if ctx.author.voice is None:
        await ctx.send("Sesli kanalda değilsiniz.")
        return

    source_channel = ctx.author.voice.channel
    target_channel = ctx.author.voice.channel

    members = ctx.guild.members

    for member in members:
        if member.voice is not None and member.voice.channel != source_channel:
            try:
                await member.move_to(target_channel)
            except:
                pass

    await ctx.send("Tüm kullanıcılar odaya taşındı.")
    

@bot.command()
@commands.has_role(YETKILI_ROLE_ID)  # Yetkili rol ID'sini buraya girin
async def hazırlarıgoster(ctx):
    # Hizmet hesabı kimlik doğrulama bilgilerini yükle
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE)

    # Kimlik doğrulama bilgileriyle gspread'e yetkilendirme yap
    client = gspread.authorize(credentials)

    # Veri eklemek istediğiniz tabloyu seçin
    spreadsheet = client.open(SPREADSHEET_NAME)
    worksheet = spreadsheet.get_worksheet(0)  # İlk çalışma sayfasını seçin

    # Tüm verileri alın
    data = worksheet.get_all_values()

    # Sınıflara göre kullanıcıları saklamak için boş listeler oluşturun
    savasci_kullanicilar = []
    ninja_kullanicilar = []
    sura_kullanicilar = []
    shaman_kullanicilar = []

    # Verileri dolaşarak sınıflara göre kullanıcıları ayırın
    for i, row in enumerate(data):
        if row[5] == "Savaşa Hazır":  # F sütununu kontrol edin
            karakter_sınıfı = row[2]  # C sütununu kontrol edin

            if karakter_sınıfı == "Savaşçı":
                savasci_kullanicilar.append(row)
            elif karakter_sınıfı == "Ninja":
                ninja_kullanicilar.append(row)
            elif karakter_sınıfı == "Sura":
                sura_kullanicilar.append(row)
            elif karakter_sınıfı == "Şaman":
                shaman_kullanicilar.append(row)

    # Sınıflara göre kullanıcıları gösterin
    embedsavasci = discord.Embed(title="SAVAŞÇI", description=f"**SAVAŞÇI** SINIFINA AİT **{len(savasci_kullanicilar)}** TANE SAVAŞA HAZIR OYUNCU VAR.", color=discord.Color.red())
    await ctx.send(f"**SAVAŞÇI** SINIFINA AİT **{len(savasci_kullanicilar)}** TANE SAVAŞA HAZIR OYUNCU VAR.")
    for kullanici in savasci_kullanicilar:
        kullanici_ad = kullanici[0]
        karakter_ad = kullanici[1]
        karakter_sinifi = kullanici[2]
        kullanici_id = kullanici[4]

        kullanici_etiketi = f"<@{kullanici_id}>"
        embedsavasci.add_field(name=f"Kullanıcı: <!@{kullanici_id}>", value=f"Kullanıcı Adı: {kullanici_ad}\nKarakter Adı: {karakter_ad}\nKarakter Sınıfı: {karakter_sinifi}", inline=False)
    await ctx.send(embed=embedsavasci)

    embedninja = discord.Embed(title="NİNJA", description=f"**NİNJA** SINIFINA AİT **{len(ninja_kullanicilar)}** TANE SAVAŞA HAZIR OYUNCU VAR.", color=discord.Color.blue())
    for kullanici in ninja_kullanicilar:
        kullanici_ad = kullanici[0]
        karakter_ad = kullanici[1]
        karakter_sinifi = kullanici[2]
        kullanici_id = kullanici[4]

        kullanici_etiketi = f"<@{kullanici_id}>"
        embedninja.add_field(name=f"Kullanıcı: <@!{kullanici_id}>", value=f"Kullanıcı Adı: {kullanici_ad}\nKarakter Adı: {karakter_ad}\nKarakter Sınıfı: {karakter_sinifi}", inline=False)
    await ctx.send(embed=embedninja)
        
        
    embedsura = discord.Embed(title="SURA", description=f"**SURA** SINIFINA AİT **{len(sura_kullanicilar)}** TANE SAVAŞA HAZIR OYUNCU VAR.", color=discord.Color.orange())
    for kullanici in sura_kullanicilar:
        kullanici_ad = kullanici[0]
        karakter_ad = kullanici[1]
        karakter_sinifi = kullanici[2]
        kullanici_id = kullanici[4]
    
        kullanici_etiketi = f"<@{kullanici_id}>"
        embedsura.add_field(name=f"Kullanıcı: <@!{kullanici_id}>", value=f"Kullanıcı Adı: {kullanici_ad}\nKarakter Adı: {karakter_ad}\nKarakter Sınıfı: {karakter_sinifi}", inline=False)
    await ctx.send(embed=embedsura)
    

    embedsaman = discord.Embed(title="ŞAMAN", description=f"**ŞAMAN** SINIFINA AİT **{len(shaman_kullanicilar)}** TANE SAVAŞA HAZIR OYUNCU VAR.", color=discord.Color.yellow())
    for kullanici in shaman_kullanicilar:
        kullanici_ad = kullanici[0]
        karakter_ad = kullanici[1]
        karakter_sinifi = kullanici[2]
        kullanici_id = kullanici[4]
    
        kullanici_etiketi = f"<@{kullanici_id}>"
        embedsaman.add_field(name=f"Kullanıcı: <@!{kullanici_id}>", value=f"Kullanıcı Adı: {kullanici_ad}\nKarakter Adı: {karakter_ad}\nKarakter Sınıfı: {karakter_sinifi}", inline=False)
    await ctx.send(embed=embedsaman)

@bot.command()
@commands.has_role(YETKILI_ROLE_ID)  # Yetkili rol ID'sini buraya girin
async def herkesemesaj(ctx, role_id, *, mesaj):
    # Belirtilen role sahip olan kullanıcıları alın
    role = discord.utils.get(ctx.guild.roles, id=int(role_id))
    if role is None:
        await ctx.send("Belirtilen rol bulunamadı.")
        return

    members = role.members
    print(members)
    # Aktif olmayan kullanıcılara da mesaj gönderin
    for member in role.members:
        try:
            await member.send(mesaj)
        except discord.Forbidden:
            await ctx.send(f"Mesaj gönderilemedi: {member.display_name}")

    await ctx.send("Mesaj gönderme işlemi tamamlandı.")


@bot.command()
@commands.has_role(YETKILI_ROLE_ID)  # Yetkili rol ID'sini buraya girin
async def komutlar(ctx):
    embed = discord.Embed(title="Komutlar", description="Sunucudaki mevcut komutlar:", color=discord.Color.red())

    # Örnek komutlar ekleyin
    embed.add_field(name="!bilgigir [ad] [karakter adı] [karkater sınıfı] [telefon no]", value="Kişinin bilgileri dökümana eklenir. Kişinin kullanıcı adı düzenlenir.", inline=False)
    embed.add_field(name="!savasahazır [kullanıcı etiketi]", value="Etiketlenen kullanıcıyı tabloda savaşa hazır olarak işaretler ve Hesabı HAzır rolünü discordda verir", inline=False)
    embed.add_field(name="!herkesemesaj [rol_id] [mesaj]", value="Belirtilen role sahip herkese DM mesajı gönderir.", inline=False)
    embed.add_field(name="!savascagır [lonca adı] [saat] [katılımcı]", value="Belirtilen savaş metnini Heaabı Hazır rolünü etiketleyerek gönderir.", inline=False)
    embed.add_field(name="!toplantı ", value="Komut kullanıldığında komutun kullanıldığı ses kanalına bağlı olan tüm kullanıcılar listelenir.", inline=False)
    embed.add_field(name="!mute", value="Bulunan ses kanalndaki komutu kullanan kullanıcı hariç tüm kullanıcıları susturur.", inline=False)
    embed.add_field(name="!unmute", value="Bulunan ses kanalndaki tüm kullanıcıların susturmasını kaldırır.", inline=False)
    embed.add_field(name="!herkesitasi", value="Sunucudaki ses kanallarında olan tüm kullanıcıları komutu kullanan kullanıcının bulunduğu sesli kanala taşır.", inline=False)
    embed.add_field(name="!hazırlarıgoster", value="Savaşa hazır olan tüm kullanıcıları AD, KARAKTER ADI, KARAKTER SINIFI şeklinde gösterir.", inline=False)
    await ctx.send(embed=embed)
    
bot.run(TOKEN)
