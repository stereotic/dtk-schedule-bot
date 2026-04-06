import logging
import re
import requests
import telebot
from telebot import types

# --- Flask (чтобы Render не засыпал) ---
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I am alive"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()


# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8676827395:AAHCXZPoSKp3tWKMlZi-4PdkzVh4nMcGIiw"

URL_WEEK1 = "https://dimtex73.gosuslugi.ru/netcat_files/22/4/S_1nedelya.pdf"
URL_WEEK2 = "https://dimtex73.gosuslugi.ru/netcat_files/22/4/S_2nedelya.pdf"
URL_BELLS = "https://dimtex73.gosuslugi.ru/netcat_files/22/4/zvonki.pdf"
URL_EXAMS = "https://dimtex73.gosuslugi.ru/netcat_files/22/4/S_ekz2.pdf"

CHANGES_INDEX_URL = "https://dimtex73.gosuslugi.ru/svedeniya-ob-organizatsii/dokumenty/izmeneniya-1-korpus.html"
SITE_PREFIX = "https://dimtex73.gosuslugi.ru"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)


# ===== КЛАВИАТУРА =====
def main_keyboard() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Расписание 1 неделя", "Расписание 2 неделя")
    kb.row("Изменения")
    kb.row("Расписание звонков", "Расписание экзаменов")
    return kb


# ===== ПОЛУЧЕНИЕ ИЗМЕНЕНИЙ =====
def get_latest_changes_link():
    resp = requests.get(CHANGES_INDEX_URL, timeout=10, verify=False)
    resp.raise_for_status()
    html = resp.text

    matches = re.findall(r'href="(/netcat_files[^"]+\.pdf)"', html)
    if not matches:
        return None

    return SITE_PREFIX + matches[0]


# ===== ХЕНДЛЕРЫ =====
@bot.message_handler(commands=["start"])
def handle_start(message: types.Message):
    bot.send_message(
        message.chat.id,
        "Выбери нужное расписание:",
        reply_markup=main_keyboard(),
    )


@bot.message_handler(func=lambda m: m.text == "Расписание 1 неделя")
def handle_week1(message: types.Message):
    bot.send_message(message.chat.id, f"{URL_WEEK1}")


@bot.message_handler(func=lambda m: m.text == "Расписание 2 неделя")
def handle_week2(message: types.Message):
    bot.send_message(message.chat.id, f"{URL_WEEK2}")


@bot.message_handler(func=lambda m: m.text == "Изменения")
def handle_changes(message: types.Message):
    bot.send_message(message.chat.id, "Ищу изменения...")

    try:
        url = get_latest_changes_link()
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")
        return

    if not url:
        bot.send_message(message.chat.id, "Не найдено.")
        return

    bot.send_message(message.chat.id, url)


@bot.message_handler(func=lambda m: m.text == "Расписание звонков")
def handle_bells(message: types.Message):
    bot.send_message(message.chat.id, URL_BELLS)


@bot.message_handler(func=lambda m: m.text == "Расписание экзаменов")
def handle_exams(message: types.Message):
    bot.send_message(message.chat.id, URL_EXAMS)


# ===== ЗАПУСК =====
def main():
    logger.info("Бот запущен")
    bot.infinity_polling()


if __name__ == "__main__":
    keep_alive()
    main()
