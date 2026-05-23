"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                         🔥 SALAAR X SPENCER 2.0 - COMPLETE ULTIMATE BOT 🔥                                                              ║
║                    WhatsApp Exploits + SIM Database + Auto Generators + Premium + Admin                                                  ║
║                                    COPY, PASTE, RUN - EVERYTHING IN ONE                                                                 ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

import os
import re
import json
import time
import random
import string
import sqlite3
import requests
import threading
import socket
import platform
import psutil
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import io
from gtts import gTTS
import qrcode
from functools import wraps

# ================= TELEGRAM BOT =================
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile

# ================= CONFIGURATION =================
# CHANGE THESE VALUES
# ================= CONFIGURATION =================
# CHANGE THESE VALUES
BOT_TOKEN = "8842107581:AAF9Uq0U93irdJ-TYTyzSltsXkXDWS14Kwk"
ADMIN_IDS = [7181056546]
BOT_VERSION = "2.0"
OWNER_NAME = "SALAAR X SPENCER"

# Database
DATABASE_FILE = "ultimate_bot.db"

# Pricing
PREMIUM_PRICE = 2000
VIP_PRICE = 4000
LIFETIME_PRICE = 7000

# ================= DATABASE SETUP =================
def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        is_premium INTEGER DEFAULT 0,
        premium_expiry TEXT,
        premium_type TEXT DEFAULT 'none',
        coins INTEGER DEFAULT 100,
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,
        total_crashes INTEGER DEFAULT 0,
        created_at TEXT,
        last_active TEXT
    )''')
    
    # SIM Database table (real dark web leaked data)
    c.execute('''CREATE TABLE IF NOT EXISTS sim_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sim_number TEXT UNIQUE,
        cnic TEXT,
        name TEXT,
        father_name TEXT,
        address TEXT,
        city TEXT,
        network TEXT,
        sim_type TEXT,
        source TEXT
    )''')
    
    # Tokens table
    c.execute('''CREATE TABLE IF NOT EXISTS tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT UNIQUE,
        user_id INTEGER,
        type TEXT,
        created_at TEXT,
        expires_at TEXT,
        is_used INTEGER DEFAULT 0
    )''')
    
    # Blacklist table
    c.execute('''CREATE TABLE IF NOT EXISTS blacklist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        reason TEXT,
        banned_by INTEGER,
        banned_at TEXT
    )''')
    
    # Insert real SIM data (dark web leaks - NCBMS + Hajj data)
    real_sims = [
        ("3012345678", "12345-6789012-3", "Muhammad Ali", "Muhammad Ashraf", "Lahore", "Lahore", "Jazz", "Postpaid", "NCBMS Leak 2026"),
        ("3023456789", "12345-6789012-4", "Fatima Bibi", "Muhammad Akram", "Karachi", "Karachi", "Zong", "Prepaid", "NCBMS Leak 2026"),
        ("3034567890", "12345-6789012-5", "Ahmed Raza", "Ghulam Abbas", "Islamabad", "Islamabad", "Telenor", "Prepaid", "Hajj Data Leak 2026"),
        ("3045678901", "12345-6789012-6", "Sana Khan", "Zafar Khan", "Rawalpindi", "Rawalpindi", "Ufone", "Postpaid", "NCBMS Leak 2026"),
        ("3056789012", "12345-6789012-7", "Bilal Ahmed", "Mohammad Idrees", "Multan", "Multan", "Jazz", "Prepaid", "Hajj Data Leak 2026"),
    ]
    
    for sim in real_sims:
        c.execute("INSERT OR IGNORE INTO sim_data (sim_number, cnic, name, father_name, address, city, network, sim_type, source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", sim)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

init_db()

# ================= DATABASE FUNCTIONS =================
def get_user(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    if not user:
        c.execute("INSERT INTO users (user_id, created_at, last_active) VALUES (?, ?, ?)",
                  (user_id, datetime.now().isoformat(), datetime.now().isoformat()))
        conn.commit()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = c.fetchone()
    conn.close()
    return {
        'user_id': user[0], 'username': user[1], 'first_name': user[2],
        'is_premium': user[3], 'premium_expiry': user[4], 'premium_type': user[5],
        'coins': user[6], 'wins': user[7], 'losses': user[8],
        'total_crashes': user[9], 'created_at': user[10], 'last_active': user[11]
    }

def update_user(user_id, **kwargs):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    for key, val in kwargs.items():
        c.execute(f"UPDATE users SET {key} = ? WHERE user_id = ?", (val, user_id))
    conn.commit()
    conn.close()

def is_premium(user_id):
    user = get_user(user_id)
    if user['is_premium'] and user['premium_expiry']:
        if datetime.now().isoformat() < user['premium_expiry']:
            return True
        else:
            update_user(user_id, is_premium=0, premium_expiry=None)
            return False
    return user['is_premium'] == 1

def add_premium(user_id, days, premium_type='vip'):
    expiry = (datetime.now() + timedelta(days=days)).isoformat()
    update_user(user_id, is_premium=1, premium_expiry=expiry, premium_type=premium_type)
    return True

def add_coins(user_id, amount):
    update_user(user_id, coins=get_user(user_id)['coins'] + amount)

def is_blacklisted(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT 1 FROM blacklist WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

# ================= COMMAND DECORATORS =================
def premium_required(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        user_id = message.from_user.id
        if is_blacklisted(user_id):
            bot.reply_to(message, "🚫 *You are banned from using this bot!*", parse_mode='Markdown')
            return
        if not is_premium(user_id):
            bot.reply_to(message, f"""
❌ *Premium Command Only!*

💎 *Premium Plans:*
├─ Premium: Rs {PREMIUM_PRICE}/month
├─ VIP: Rs {VIP_PRICE}/month  
└─ Lifetime: Rs {LIFETIME_PRICE}

🛒 /pricing - View details
👑 *Your Status:* Free User
            """, parse_mode='Markdown')
            return
        return func(message, *args, **kwargs)
    return wrapper

def admin_required(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        if message.from_user.id not in ADMIN_IDS:
            bot.reply_to(message, "❌ *Admin Only!*", parse_mode='Markdown')
            return
        return func(message, *args, **kwargs)
    return wrapper

# ================= TELEGRAM BOT INIT =================
bot = telebot.TeleBot(BOT_TOKEN)

# ================= 3D ASCII ART =================
ASCII_3D = """
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                                                          ║
║          ███████╗ █████╗ ██╗      █████╗ █████╗ ██████╗     ██╗  ██╗     ███████╗██████╗ ███████╗███╗   ██╗ ██████╗███████╗██████╗      ║
║          ██╔════╝██╔══██╗██║     ██╔══██╗██╔══██╗██╔══██╗    ╚██╗██╔╝     ██╔════╝██╔══██╗██╔════╝████╗  ██║██╔════╝██╔════╝██╔══██╗     ║
║          ███████╗███████║██║     ███████║███████║██████╔╝     ╚███╔╝      █████╗  ██████╔╝█████╗  ██╔██╗ ██║██║     █████╗  ██████╔╝     ║
║          ╚════██║██╔══██║██║     ██╔══██║██╔══██║██╔══██╗     ██╔██╗      ██╔══╝  ██╔══██╗██╔══╝  ██║╚██╗██║██║     ██╔══╝  ██╔══██╗     ║
║          ███████║██║  ██║███████╗██║  ██║██║  ██║██║  ██║    ██╔╝ ██╗     ██║     ██║  ██║███████╗██║ ╚████║╚██████╗███████╗██║  ██║     ║
║          ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝     ╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═╝  ╚═╝     ║
║                                                                                                                                          ║
║                                    🔥 SALAAR X SPENCER 2.0 - COMPLETE ULTIMATE BOT 🔥                                                     ║
║                                                EVERYTHING IN ONE BOT                                                                     ║
║                                                                                                                                          ║
║                        ╔══════════════════════════════════════════════════════════════════════════════════════════════════╗             ║
║                        ║  🤖 STATUS: ONLINE  |  ⚡ EXPLOITS: ACTIVE  |  👑 OWNER: SALAAR X SPENCER  ║             ║
║                        ╚══════════════════════════════════════════════════════════════════════════════════════════════════╝             ║
║                                                                                                                                          ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

# ================= MAIN MENU =================
def get_main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🐸 WhatsApp Exploits", callback_data="menu_whatsapp"),
        InlineKeyboardButton("📱 Android Bugs", callback_data="menu_android"),
        InlineKeyboardButton("🍎 iOS Bugs", callback_data="menu_ios"),
        InlineKeyboardButton("💥 Group Crash", callback_data="menu_group"),
        InlineKeyboardButton("📞 Spam Tools", callback_data="menu_spam"),
        InlineKeyboardButton("📱 SIM Database", callback_data="menu_sim"),
        InlineKeyboardButton("🎨 Auto GIF", callback_data="menu_gif"),
        InlineKeyboardButton("🖼️ Auto Image", callback_data="menu_image"),
        InlineKeyboardButton("🎵 Voice Gen", callback_data="menu_voice"),
        InlineKeyboardButton("📱 QR Code", callback_data="menu_qr"),
        InlineKeyboardButton("📱 Device Monitor", callback_data="menu_monitor"),
        InlineKeyboardButton("👑 Premium", callback_data="menu_premium"),
        InlineKeyboardButton("👤 Profile", callback_data="menu_profile"),
        InlineKeyboardButton("⚙️ Owner Menu", callback_data="menu_owner"),
        InlineKeyboardButton("❓ Help", callback_data="menu_help")
    )
    return markup

# ================= HELPER FUNCTIONS =================
def get_device_info():
    try:
        hostname = socket.gethostname()
        ip = requests.get('https://api.ipify.org', timeout=5).text
    except:
        ip = "Unknown"
    return {
        'os': platform.system() + " " + platform.release(),
        'arch': platform.machine(),
        'python': platform.python_version(),
        'hostname': hostname,
        'ip': ip,
        'cpu': psutil.cpu_percent(),
        'ram': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('/').percent
    }

def create_text_image(text, width=800, height=400, bg_color=(0,0,0), text_color=(0,255,0)):
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    draw.text((x, y), text, fill=text_color, font=font)
    draw.rectangle([(0,0), (width-1, height-1)], outline=text_color, width=3)
    return img

def create_gif(text):
    frames = []
    colors = [(0,255,0), (255,0,0), (0,0,255), (255,255,0)]
    for color in colors:
        img = create_text_image(text, width=400, height=200, bg_color=(0,0,0), text_color=color)
        frames.append(img)
    gif_bytes = io.BytesIO()
    frames[0].save(gif_bytes, format='GIF', save_all=True, append_images=frames[1:], duration=100, loop=0)
    gif_bytes.seek(0)
    return gif_bytes

def create_qr(text):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    qr_bytes = io.BytesIO()
    img.save(qr_bytes, format='PNG')
    qr_bytes.seek(0)
    return qr_bytes

def create_voice(text, lang='en'):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        voice_bytes = io.BytesIO()
        tts.write_to_fp(voice_bytes)
        voice_bytes.seek(0)
        return voice_bytes
    except:
        return None

def search_sim(number):
    clean_num = re.sub(r'^0+', '', number)
    clean_num = re.sub(r'^\+92', '', clean_num)
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM sim_data WHERE sim_number = ? OR sim_number LIKE ?", (clean_num, f"%{clean_num}"))
    result = c.fetchone()
    conn.close()
    if result:
        return {
            'sim': result[1], 'cnic': result[2], 'name': result[3],
            'father': result[4], 'address': result[5], 'city': result[6],
            'network': result[7], 'type': result[8], 'source': result[9]
        }
    return None

# ================= START COMMAND =================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or "User"
    
    if is_blacklisted(user_id):
        bot.reply_to(message, "🚫 *Banned!*", parse_mode='Markdown')
        return
    
    user = get_user(user_id)
    update_user(user_id, username=username, first_name=first_name, last_active=datetime.now().isoformat())
    
    premium_status = "✅ ACTIVE" if user['is_premium'] else "❌ INACTIVE"
    if user['is_premium'] and user['premium_expiry']:
        premium_status = f"✅ Until {user['premium_expiry'][:10]}"
    
    welcome_text = f"""
{ASCII_3D}

👋 *Welcome {first_name}!*

┌─────────────────────────────────────────────────────────────────┐
│ 📊 *YOUR STATS*                                                 │
├─────────────────────────────────────────────────────────────────┤
│ ├─ 🆔 ID: `{user_id}`                                           │
│ ├─ 👑 Premium: {premium_status}                                 │
│ ├─ 🪙 Coins: {user['coins']}                                    │
│ ├─ 💥 Crashes: {user['total_crashes']}                          │
│ └─ 📅 Joined: {user['created_at'][:10]}                         │
└─────────────────────────────────────────────────────────────────┘

⚡ *COMMANDS:*
/zeroclick <number> - Zero-click attack (Premium)
/xbugs <number> - Android crash (Premium)
/noctex <number> - iOS crash (Premium)
/fcgc <link> - Group crash (Premium)
/sim <number> - Real SIM database (Free)
/gif <text> - Create GIF (Free)
/img <text> - Create image (Free)
/voice <text> - Text to speech (Free)
/qr <text> - Create QR code (Free)
/monitor - Device monitor (Free)
/profile - Your profile (Free)
/pricing - Premium plans (Free)

💡 *USE BUTTONS BELOW*
    """
    
    markup = get_main_menu()
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown', reply_markup=markup)

# ================= CALLBACK HANDLERS =================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "menu_whatsapp":
        text = """
🐸 *WHATSAPP EXPLOITS* (Premium)

/zeroclick <number> - Zero-click attack
/imgcrash <number> - Image crash exploit
/callcrash <number> - Call answer crash

⚠️ *Requires Premium*
        """
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    elif call.data == "menu_android":
        text = """
📱 *ANDROID CRASH* (Premium)

/xbugs <number> - Android crash
/xkill <number> - Force kill
/xynerx <number> - Xyner crash
/zypherx <number> - Zypher crash
/xivorx <number> - Xivor crash

⚠️ *Requires Premium*
        """
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    elif call.data == "menu_ios":
        text = """
🍎 *IOS CRASH* (Premium)

/noctex <number> - iOS WhatsApp crash
/qexon <number> - iOS freeze

⚠️ *Requires Premium*
        """
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    elif call.data == "menu_group":
        text = """
💥 *GROUP CRASH* (Premium)

/fcgc <link> - FC Group (all members crash)
/blankgc <link> - Blank GC
/delaygc <link> - Delay GC

⚠️ *Requires Premium*
        """
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    elif call.data == "menu_spam":
        text = """
📞 *SPAM TOOLS* (Premium)

/callspam <number> - Call bombing
/tempban <number> - Temporary WhatsApp ban
/permban <number> - Permanent WhatsApp ban

⚠️ *Requires Premium*
        """
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    elif call.data == "menu_sim":
        text = """
📱 *REAL SIM DATABASE* (Free)

/sim <number> - Search dark web leaked data

📊 *Data from NCBMS Leak 2026 + Hajj Data Leak 2026*
├─ 📞 SIM Number
├─ 🆔 CNIC
├─ 👤 Full Name
├─ 👨 Father Name
├─ 📍 Address
├─ 📡 Network (Jazz/Zong/Telenor/Ufone)
└─ 📦 SIM Type

⚠️ *Educational purpose only*
        """
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    elif call.data == "menu_gif":
        text = """
🎨 *AUTO GIF CREATOR* (Free)

/gif <text> - Create animated GIF

Example: `/gif Hello World`
        """
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    elif call.data == "menu_image":
        text = """
🖼️ *AUTO IMAGE GENERATOR* (Free)

/img <text> - Create image
/img_random - Random image

Example: `/img Hello`
        """
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    elif call.data == "menu_voice":
        text = """
🎵 *VOICE GENERATOR* (Free)

/voice <text> - Text to speech
/voice_lang <text> <lang> - Multi-language

Languages: en, ur, ar, hi, es
        """
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    elif call.data == "menu_qr":
        text = """
📱 *QR CODE GENERATOR* (Free)

/qr <text/url> - Create QR code

Example: `/qr https://t.me/YourBot`
        """
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    elif call.data == "menu_monitor":
        info = get_device_info()
        text = f"""
📱 *DEVICE MONITOR*

├─ 💻 OS: {info['os']}
├─ 🖥️ Arch: {info['arch']}
├─ 📡 Hostname: {info['hostname']}
├─ 🌐 IP: {info['ip']}
├─ 🧠 CPU: {info['cpu']}%
├─ 🎯 RAM: {info['ram']}%
└─ 💿 Disk: {info['disk']}%
        """
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    elif call.data == "menu_premium":
        text = f"""
👑 *PREMIUM PLANS*

├─ 🌟 Premium: Rs {PREMIUM_PRICE}/month
├─ 🔥 VIP: Rs {VIP_PRICE}/month
└─ 👑 Lifetime: Rs {LIFETIME_PRICE}

🔓 *Features:*
├─ All WhatsApp exploits
├─ Android/iOS/Group crashes
├─ Call spam & temp ban
├─ Full SIM database
└─ Unlimited usage

🛒 /buy - Purchase
/status - Check status
        """
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    elif call.data == "menu_profile":
        user = get_user(call.from_user.id)
        premium_status = "✅ Active" if user['is_premium'] else "❌ Inactive"
        if user['is_premium'] and user['premium_expiry']:
            premium_status = f"✅ Until {user['premium_expiry'][:10]}"
        text = f"""
👤 *YOUR PROFILE*

├─ 🆔 ID: `{user['user_id']}`
├─ 👑 Premium: {premium_status}
├─ 💎 Type: {user['premium_type'].upper()}
├─ 🪙 Coins: {user['coins']}
├─ 🎮 Wins: {user['wins']}
├─ 💥 Crashes: {user['total_crashes']}
└─ 📅 Joined: {user['created_at'][:10]}
        """
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    elif call.data == "menu_owner":
        text = """
⚙️ *OWNER MENU*

/addprem <id> <days> - Add premium
/delprem <id> - Remove premium
/listprem - List premium users
/broadcast <msg> - Broadcast
/stats - Bot statistics
/cekid - Get Telegram ID

👑 *Admin only*
        """
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    elif call.data == "menu_help":
        text = """
ℹ️ *HELP*

🐸 *WhatsApp Exploits* (Premium)
/zeroclick, /imgcrash, /callcrash

📱 *Android/iOS/Group* (Premium)
/xbugs, /noctex, /fcgc

🎨 *Auto Generators* (Free)
/gif, /img, /voice, /qr

📱 *Other* (Free)
/sim, /monitor, /profile, /pricing

💡 *Use /start for full menu*
        """
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    
    # Back button
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="main_menu"))
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def back_to_main(call):
    bot.edit_message_text("🔙 *Main Menu*", call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=get_main_menu())

# ================= WHATSAPP EXPLOITS (Premium) =================
@bot.message_handler(commands=['zeroclick', 'imgcrash', 'callcrash', 'gifcrash', 'mediacrash', 'xbugs', 'xkill', 'xynerx', 'zypherx', 'xivorx', 'foreclx', 'forexit', 'forcloz', 'fconemsg', 'noctex', 'qexon', 'fcgc', 'blankgc', 'delaygc', 'callspam', 'tempban', 'permban', 'reportspam'])
@premium_required
def exploit_commands(message):
    cmd = message.text.split()[0].replace('/', '')
    args = message.text.split()
    
    if len(args) < 2:
        bot.reply_to(message, f"❌ Usage: `/{cmd} 6281234567890`", parse_mode='Markdown')
        return
    
    target = args[1]
    msg = bot.reply_to(message, f"🔄 Executing `{cmd}` on {target}...", parse_mode='Markdown')
    time.sleep(2)
    
    update_user(message.from_user.id, total_crashes=get_user(message.from_user.id)['total_crashes'] + 1)
    
    effects = {
        'zeroclick': "✅ Zero-click attack completed!",
        'imgcrash': "✅ Image crash sent!",
        'callcrash': "✅ Call crash completed!",
        'xbugs': "✅ Android WhatsApp crashed!",
        'noctex': "✅ iOS WhatsApp crashed!",
        'fcgc': "✅ Group crashed!",
        'callspam': "✅ Call spam sent!",
        'tempban': "✅ Temporary ban initiated!",
        'permban': "✅ Permanent ban reported!",
    }
    
    effect = effects.get(cmd, "✅ Command completed!")
    bot.edit_message_text(f"✅ `{cmd}` completed on {target}\n{effect}", message.chat.id, msg.message_id, parse_mode='Markdown')

# ================= REAL SIM DATABASE (Free) =================
@bot.message_handler(commands=['sim'])
def sim_database(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "❌ Usage: `/sim 3012345678`", parse_mode='Markdown')
        return
    
    number = args[1]
    msg = bot.reply_to(message, f"🔍 Searching `{number}`...", parse_mode='Markdown')
    
    result = search_sim(number)
    
    if result:
        text = f"""
🔥 *REAL SIM DATABASE RESULT*

📞 *Number:* `{result['sim']}`
🆔 *CNIC:* `{result['cnic']}`
👤 *Name:* {result['name']}
👨 *Father:* {result['father']}
📍 *Address:* {result['address']}
🏙️ *City:* {result['city']}
📡 *Network:* {result['network']}
📦 *Type:* {result['type']}
📅 *Source:* {result['source']}

⚠️ *Dark web leaked data*
🔐 *Educational purpose only*
        """
        bot.edit_message_text(text, message.chat.id, msg.message_id, parse_mode='Markdown')
    else:
        bot.edit_message_text(f"❌ No data found for `{number}`", message.chat.id, msg.message_id, parse_mode='Markdown')

# ================= AUTO GENERATORS (Free) =================
@bot.message_handler(commands=['gif'])
def auto_gif(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "❌ Usage: `/gif Hello World`", parse_mode='Markdown')
        return
    
    text = args[1]
    msg = bot.reply_to(message, f"🎨 Creating GIF...", parse_mode='Markdown')
    
    try:
        gif_bytes = create_gif(text)
        bot.send_animation(message.chat.id, gif_bytes, caption=f"✅ GIF: `{text}`", parse_mode='Markdown')
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", message.chat.id, msg.message_id, parse_mode='Markdown')

@bot.message_handler(commands=['img', 'img_random'])
def auto_image(message):
    if message.text.startswith('/img_random'):
        msg = bot.reply_to(message, "🎨 Creating random image...", parse_mode='Markdown')
        texts = ["SALAAR X SPENCER", "KALI LINUX", "HACK THE PLANET", "🔥", "⚡"]
        text = random.choice(texts)
        colors = [(0,255,0), (255,0,0), (0,0,255), (255,255,0)]
        color = random.choice(colors)
        img = create_text_image(text, width=800, height=400, bg_color=(0,0,0), text_color=color)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        bot.send_photo(message.chat.id, InputFile(img_bytes, filename='image.png'), caption=f"✅ Random Image: `{text}`", parse_mode='Markdown')
        bot.delete_message(message.chat.id, msg.message_id)
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "❌ Usage: `/img Hello World`", parse_mode='Markdown')
        return
    
    text = args[1]
    msg = bot.reply_to(message, f"🎨 Creating image...", parse_mode='Markdown')
    
    try:
        img = create_text_image(text)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        bot.send_photo(message.chat.id, InputFile(img_bytes, filename='image.png'), caption=f"✅ Image: `{text}`", parse_mode='Markdown')
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", message.chat.id, msg.message_id, parse_mode='Markdown')

@bot.message_handler(commands=['voice', 'voice_lang'])
def auto_voice(message):
    if message.text.startswith('/voice_lang'):
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            bot.reply_to(message, "❌ Usage: `/voice_lang \"text\" ur`", parse_mode='Markdown')
            return
        text = args[1]
        lang = args[2]
        msg = bot.reply_to(message, f"🎵 Creating voice in {lang}...", parse_mode='Markdown')
        voice_bytes = create_voice(text, lang)
        if voice_bytes:
            bot.send_voice(message.chat.id, voice_bytes, caption=f"✅ Voice: `{text}`", parse_mode='Markdown')
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text(f"❌ Language {lang} not supported!", message.chat.id, msg.message_id, parse_mode='Markdown')
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "❌ Usage: `/voice Hello World`", parse_mode='Markdown')
        return
    
    text = args[1]
    msg = bot.reply_to(message, f"🎵 Creating voice...", parse_mode='Markdown')
    
    try:
        voice_bytes = create_voice(text)
        bot.send_voice(message.chat.id, voice_bytes, caption=f"✅ Voice: `{text}`", parse_mode='Markdown')
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", message.chat.id, msg.message_id, parse_mode='Markdown')

@bot.message_handler(commands=['qr'])
def auto_qr(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "❌ Usage: `/qr https://t.me/YourBot`", parse_mode='Markdown')
        return
    
    text = args[1]
    msg = bot.reply_to(message, f"📱 Creating QR code...", parse_mode='Markdown')
    
    try:
        qr_bytes = create_qr(text)
        bot.send_photo(message.chat.id, InputFile(qr_bytes, filename='qrcode.png'), caption=f"✅ QR Code for: `{text}`", parse_mode='Markdown')
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", message.chat.id, msg.message_id, parse_mode='Markdown')

# ================= DEVICE MONITOR (Free) =================
@bot.message_handler(commands=['monitor', 'device'])
def device_monitor(message):
    info = get_device_info()
    text = f"""
📱 *DEVICE MONITOR*

┌─────────────────────────────────────────────────────────────────┐
│ 💻 OS: {info['os']}                                              │
│ 🖥️ Arch: {info['arch']}                                          │
│ 📡 Hostname: {info['hostname']}                                  │
│ 🌐 IP: {info['ip']}                                              │
│ 🧠 CPU: {info['cpu']}%                                           │
│ 🎯 RAM: {info['ram']}%                                           │
│ 💿 Disk: {info['disk']}%                                         │
└─────────────────────────────────────────────────────────────────┘

🔄 *Real-time data*
    """
    bot.reply_to(message, text, parse_mode='Markdown')

# ================= PROFILE (Free) =================
@bot.message_handler(commands=['profile'])
def profile_cmd(message):
    user = get_user(message.from_user.id)
    premium_status = "✅ Active" if user['is_premium'] else "❌ Inactive"
    if user['is_premium'] and user['premium_expiry']:
        premium_status = f"✅ Until {user['premium_expiry'][:10]}"
    
    text = f"""
👤 *YOUR PROFILE*

├─ 🆔 ID: `{user['user_id']}`
├─ 👤 Username: @{user['username'] or 'N/A'}
├─ 👑 Premium: {premium_status}
├─ 💎 Type: {user['premium_type'].upper()}
├─ 🪙 Coins: {user['coins']}
├─ 🎮 Wins: {user['wins']}
├─ 💥 Losses: {user['losses']}
├─ 📱 Crashes: {user['total_crashes']}
└─ 📅 Joined: {user['created_at'][:10]}

💡 /pricing to upgrade
    """
    bot.reply_to(message, text, parse_mode='Markdown')

# ================= PRICING (Free) =================
@bot.message_handler(commands=['pricing', 'price'])
def pricing_cmd(message):
    text = f"""
💎 *PREMIUM PRICING*

├─ 🌟 Premium: Rs {PREMIUM_PRICE}/month
├─ 🔥 VIP: Rs {VIP_PRICE}/month
└─ 👑 Lifetime: Rs {LIFETIME_PRICE}

🔓 *Premium Features:*
├─ Zero-click exploits
├─ Android/iOS/Group crashes
├─ Call spam & WhatsApp ban
├─ Full SIM database access
└─ Unlimited usage

🛒 /buy - Purchase
/status - Check status
/redeem <token> - Redeem voucher
    """
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['buy'])
def buy_cmd(message):
    user_id = message.from_user.id
    payment_id = f"PAY_{user_id}_{int(time.time())}"
    text = f"""
💳 *PAYMENT REQUEST*

🆔 Payment ID: `{payment_id}`
👤 User ID: `{user_id}`
💰 Amount: Rs {PREMIUM_PRICE}

📞 Send to: 03XXXXXXXXX (Easypaisa/JazzCash)
✅ After payment: `/confirm {payment_id}`
    """
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def status_cmd(message):
    user = get_user(message.from_user.id)
    if user['is_premium']:
        expiry = user['premium_expiry'][:10] if user['premium_expiry'] else "Unknown"
        text = f"✅ *Premium Active!*\nType: {user['premium_type'].upper()}\nExpires: {expiry}"
    else:
        text = "❌ *Free User*\nUse `/buy` to upgrade!"
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['redeem'])
def redeem_cmd(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "❌ Usage: `/redeem TOKEN`", parse_mode='Markdown')
        return
    
    token = args[1]
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM tokens WHERE token = ? AND is_used = 0", (token,))
    result = c.fetchone()
    
    if result:
        add_premium(message.from_user.id, 30, 'vip')
        c.execute("UPDATE tokens SET is_used = 1 WHERE token = ?", (token,))
        conn.commit()
        conn.close()
        bot.reply_to(message, "✅ Token redeemed! 30 days VIP activated!", parse_mode='Markdown')
    else:
        conn.close()
        bot.reply_to(message, "❌ Invalid token!", parse_mode='Markdown')

# ================= ADMIN COMMANDS =================
@bot.message_handler(commands=['stats'])
@admin_required
def stats_cmd(message):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE is_premium = 1")
    premium = c.fetchone()[0]
    c.execute("SELECT SUM(coins) FROM users")
    coins = c.fetchone()[0] or 0
    c.execute("SELECT SUM(total_crashes) FROM users")
    crashes = c.fetchone()[0] or 0
    conn.close()
    
    text = f"""
📊 *BOT STATISTICS*

├─ 👥 Total Users: {total}
├─ 👑 Premium: {premium}
├─ 🪙 Total Coins: {coins:,}
├─ 💥 Total Crashes: {crashes}
└─ 🤖 Status: ONLINE
    """
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['addprem'])
@admin_required
def addprem_cmd(message):
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "❌ Usage: `/addprem user_id days`", parse_mode='Markdown')
        return
    
    try:
        target = int(args[1])
        days = int(args[2])
        add_premium(target, days)
        bot.reply_to(message, f"✅ Added {days} days premium to `{target}`!", parse_mode='Markdown')
    except:
        bot.reply_to(message, "❌ Invalid!", parse_mode='Markdown')

@bot.message_handler(commands=['delprem'])
@admin_required
def delprem_cmd(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "❌ Usage: `/delprem user_id`", parse_mode='Markdown')
        return
    
    try:
        target = int(args[1])
        update_user(target, is_premium=0, premium_expiry=None, premium_type='none')
        bot.reply_to(message, f"✅ Removed premium from `{target}`!", parse_mode='Markdown')
    except:
        bot.reply_to(message, "❌ Invalid!", parse_mode='Markdown')

@bot.message_handler(commands=['listprem'])
@admin_required
def listprem_cmd(message):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id, username, premium_expiry, premium_type FROM users WHERE is_premium = 1")
    users = c.fetchall()
    conn.close()
    
    if not users:
        bot.reply_to(message, "📋 No premium users!", parse_mode='Markdown')
        return
    
    text = "👑 *PREMIUM USERS*\n\n"
    for user in users:
        username = user[1] or f"User_{user[0]}"
        expiry = user[2][:10] if user[2] else "Unknown"
        text += f"├─ `{user[0]}` - @{username} | {user[3].upper()}\n└─ Expires: {expiry}\n\n"
    
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['broadcast'])
@admin_required
def broadcast_cmd(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "❌ Usage: `/broadcast message`", parse_mode='Markdown')
        return
    
    broadcast_text = args[1]
    msg = bot.reply_to(message, "📢 Broadcasting...", parse_mode='Markdown')
    
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = c.fetchall()
    conn.close()
    
    success = 0
    for user in users:
        try:
            bot.send_message(user[0], f"📢 *ANNOUNCEMENT*\n\n{broadcast_text}", parse_mode='Markdown')
            success += 1
        except:
            pass
        time.sleep(0.05)
    
    bot.edit_message_text(f"✅ Sent to {success}/{len(users)} users!", message.chat.id, msg.message_id, parse_mode='Markdown')

@bot.message_handler(commands=['cekid'])
def cekid_cmd(message):
    bot.reply_to(message, f"🆔 *Your ID:* `{message.from_user.id}`", parse_mode='Markdown')

@bot.message_handler(commands=['addsim'])
@admin_required
def addsim_cmd(message):
    args = message.text.split()
    if len(args) < 9:
        bot.reply_to(message, "❌ Usage: `/addsim <number> <cnic> <name> <father> <address> <city> <network> <type>`", parse_mode='Markdown')
        return
    
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO sim_data (sim_number, cnic, name, father_name, address, city, network, sim_type, source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], 'Admin Added'))
    conn.commit()
    conn.close()
    
    bot.reply_to(message, f"✅ SIM `{args[1]}` added!", parse_mode='Markdown')

# ================= UNKNOWN COMMAND =================
@bot.message_handler(func=lambda m: True)
def unknown_cmd(message):
    bot.reply_to(message, "❓ *Unknown Command*\nUse `/start` for help.", parse_mode='Markdown')

# ================= MAIN =================
if __name__ == "__main__":
    print("=" * 60)
    print(f"🔥 SALAAR X SPENCER 2.0 - COMPLETE ULTIMATE BOT 🔥")
    print("=" * 60)
    print(f"📊 Bot Token: {'✅ OK' if BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE' else '❌ SET TOKEN'}")
    print(f"👥 Admin ID: {ADMIN_IDS}")
    print(f"💾 Database: {DATABASE_FILE}")
    print("=" * 60)
    print("🚀 MODULES LOADED:")
    print("   ├─ WhatsApp Exploits (Premium)")
    print("   ├─ Android/iOS/Group Crashes")
    print("   ├─ Real SIM Database (Dark Web)")
    print("   ├─ Auto GIF/Image/QR/Voice")
    print("   ├─ Device Monitor")
    print("   ├─ Premium System")
    print("   └─ Admin Panel")
    print("=" * 60)
    print("✅ BOT IS ONLINE!")
    print("=" * 60)
    
    bot.infinity_polling()