import logging
import re
import requests
import telebot
from telebot import types

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8676827395:AAHCXZPoSKp3tWKMlZi-4PdkzVh4nMcGIiw"

URL_WEEK1 = "https://dimtex73.gosuslugi.ru/svedeniya-ob-organizatsii/dokumenty/raspisanie-1-korpus-1-nedelya.html"
URL_WEEK2 = "https://dimtex73.gosuslugi.ru/netcat_files/22/4/S_2nedelya.pdf"
URL_BELLS = "https://dimtex73.gosuslugi.ru/netcat_files/22/4/zvonki.pdf"
URL_EXAMS = "https://dimtex73.gosuslugi.ru/netcat_files/22/4/S_ekz2.pdf"

# страница со списком изменений (кнопка "Смотреть")
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


# ===== ПОИСК АКТУАЛЬНОЙ ССЫЛКИ НА ИЗМЕНЕНИЯ =====
def get_latest_changes_link() -> str | None:
    """
    Загружает страницу с изменениями и находит первую ссылку на PDF
    (/netcat_files/...pdf). Её и считаем актуальной.
    """
    resp = requests.get(CHANGES_INDEX_URL, timeout=10, verify=False)
    resp.raise_for_status()
    html = resp.text

    # Ищем href="/netcat_files/22/4/....pdf"
    matches = re.findall(r'href="(?P<href>/netcat_files[^"]+\.pdf)"', html)
    if not matches:
        return None

    href = matches[0]
    if href.startswith("http"):
        return href
    return SITE_PREFIX + href


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
    bot.send_message(
        message.chat.id,
        f"Расписание 1 недели:\n{URL_WEEK1}",
    )


@bot.message_handler(func=lambda m: m.text == "Расписание 2 неделя")
def handle_week2(message: types.Message):
    bot.send_message(
        message.chat.id,
        f"Расписание 2 недели (PDF):\n{URL_WEEK2}",
    )


@bot.message_handler(func=lambda m: m.text == "Изменения")
def handle_changes(message: types.Message):
    bot.send_message(message.chat.id, "Ищу актуальные изменения расписания...")

    try:
        url = get_latest_changes_link()
    except Exception as e:
        logger.error("Ошибка при получении ссылки на изменения: %s", e)
        bot.send_message(
            message.chat.id,
            f"Не удалось получить ссылку на изменения расписания:\n{e}",
        )
        return

    if not url:
        bot.send_message(
            message.chat.id,
            "Не удалось найти ссылку на изменения на сайте.",
        )
        return

    bot.send_message(
        message.chat.id,
        f"Актуальные изменения расписания (PDF):\n{url}",
    )


@bot.message_handler(func=lambda m: m.text == "Расписание звонков")
def handle_bells(message: types.Message):
    bot.send_message(
        message.chat.id,
        f"Расписание звонков (PDF):\n{URL_BELLS}",
    )


@bot.message_handler(func=lambda m: m.text == "Расписание экзаменов")
def handle_exams(message: types.Message):
    bot.send_message(
        message.chat.id,
        f"Расписание экзаменов (PDF):\n{URL_EXAMS}",
    )


def main():
    logger.info("Бот запущен. Нажмите Ctrl+C для остановки.")
    bot.infinity_polling()


if __name__ == "__main__":
    main()
