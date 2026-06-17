import telebot
from flask import Flask, request

TOKEN = "8912150974:AAHif-lx9AY2abGmo836xFz0TWHQCmTu_7Y"
# Вшил твой ID со скриншота, теперь ты официально админ для бота
ADMIN_ID = 5576359465

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def handle_root():
    if request.method == 'POST':
        if request.is_json:
            update = telebot.types.Update.de_json(request.get_json())
            bot.process_new_updates([update])
            return 'OK', 200
        return 'Not JSON', 400
    return 'Bot Flask Server is Alive!', 200

user_states = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        f"Привет! Твой числовой ID: {message.chat.id}\n\n"
        "Используй /bio для ссылки или /message, чтобы написать создателю."
    )

@bot.message_handler(commands=['bio'])
def send_bio(message):
    bot.reply_to(message, "https://sanyaleks2012-lab.github.io/bio/")

@bot.message_handler(commands=['message'])
def start_message(message):
    # Вместо словаря регистрируем функцию, которая ДОЛЖНА обработать следующее сообщение
    msg = bot.reply_to(message, "Напиши своё сообщение для создателя:")
    bot.register_next_step_handler(msg, forward_to_admin)

def forward_to_admin(message):
    from telebot.util import smart_html_escape
    safe_name = smart_html_escape(message.from_user.first_name)
    safe_text = smart_html_escape(message.text)

    report = (
        f"Имя: {safe_name}\n"
        f"Айди: {message.chat.id}\n"
        f"Сообщение: <b>{safe_text}</b>"
    )
    try:
        bot.send_message(ADMIN_ID, report, parse_mode='HTML')
        bot.reply_to(message, "Твое сообщение отправлено создателю!")
    except Exception as e:
        bot.reply_to(message, f"Ошибка при отправке админу: {str(e)}")

@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == 'waiting_for_text')
def forward_to_admin(message):
    user_states[message.chat.id] = None
    
    # Экранируем спецсимволы (вроде "_"), чтобы ник R_ED больше ничего не ломал
    from telebot.util import smart_html_escape
    safe_name = smart_html_escape(message.from_user.first_name)
    safe_text = smart_html_escape(message.text)

    report = (
        f"Имя: {safe_name}\n"
        f"Айди: {message.chat.id}\n"
        f"Сообщение: <b>{safe_text}</b>"
    )
    try:
        # Отправляем в формате HTML
        bot.send_message(ADMIN_ID, report, parse_mode='HTML')
        bot.reply_to(message, "Твое сообщение отправлено создателю!")
    except Exception as e:
        bot.reply_to(message, f"Ошибка при отправке админу: {str(e)}")

@bot.message_handler(commands=['id'])
def reply_to_user(message):
    if message.chat.id != ADMIN_ID:
        return
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            bot.reply_to(message, "Формат: /id [айди] [сообщение]")
            return
        target_id = int(parts[1])
        reply_text = parts[2]
        bot.send_message(target_id, reply_text)
        bot.reply_to(message, f"Ответ отправлен!")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")
