import os
from dotenv import load_dotenv
import json
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telebot import TeleBot, types

load_dotenv()

TOKEN = '8141145532:AAHwme6p9d6WKmC08I0M-05AUV1AhJT9RiY'
bot = TeleBot(TOKEN)

creds_dict = {
    "type": "service_account",
    "project_id": os.getenv("GOOGLE_PROJECT_ID"),
    "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('GOOGLE_CLIENT_EMAIL').replace('@', '%40')}",
    "universe_domain": "googleapis.com"
}

with open("temp_credentials.json", "w") as f:
    json.dump(creds_dict, f)

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name("temp_credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Athlon Registration").sheet1

CHANNEL_USERNAME = '@athlonuz'
user_data = {}
STEP_CITY, STEP_PHONE, STEP_FULLNAME = range(3)

@bot.message_handler(commands=['start'])
def start(message):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, message.from_user.id)
        if member.status in ['left', 'kicked']:
            bot.send_message(message.chat.id, f"Iltimos, avvalo @{CHANNEL_USERNAME[1:]} kanaliga obuna bo‘ling.")
            return
    except Exception:
        bot.send_message(message.chat.id, "Kanalga obuna bo‘lishni tekshira olmadi. Iltimos, qayta urinib ko‘ring.")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Ro‘yxatdan o‘tish"))
    bot.send_message(message.chat.id, "Assalomu alaykum! Athlon Group botiga xush kelibsiz.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Ro‘yxatdan o‘tish")
def register_start(message):
    msg = bot.send_message(message.chat.id, "Iltimos, yashayotgan shaharingizni tanlang:", reply_markup=city_keyboard())
    bot.register_next_step_handler(msg, process_city_step)

def city_keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    cities = ['Namangan', 'Toshkent', 'Samarqand', 'Boshqa']
    for city in cities:
        markup.add(types.KeyboardButton(city))
    return markup

def process_city_step(message):
    user_data[message.chat.id] = {'city': message.text}
    msg = bot.send_message(message.chat.id, "Telefon raqamingizni yuboring:", reply_markup=phone_keyboard())
    bot.register_next_step_handler(msg, process_phone_step)

def phone_keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("Telefon raqamni yuborish", request_contact=True))
    return markup

def process_phone_step(message):
    if message.contact is not None:
        phone = message.contact.phone_number
    else:
        phone = message.text
    user_data[message.chat.id]['phone'] = phone
    msg = bot.send_message(message.chat.id, "To‘liq ism va familiyangizni kiriting:")
    bot.register_next_step_handler(msg, process_fullname_step)

def process_fullname_step(message):
    user_data[message.chat.id]['fullname'] = message.text
    chat_id = message.chat.id
    try:
        sheet.append_row([
            chat_id,
            user_data[chat_id]['city'],
            user_data[chat_id]['phone'],
            user_data[chat_id]['fullname'],
            str(datetime.datetime.now().date())
        ])
        bot.send_message(chat_id, "Siz muvaffaqiyatli ro‘yxatdan o‘tdingiz! Rahmat.")
    except Exception:
        bot.send_message(chat_id, "Ro‘yxatdan o‘tishda xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko‘ring.")

bot.polling(none_stop=True)
