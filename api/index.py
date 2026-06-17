import telebot
from flask import Flask, request

TOKEN = "8912150974:AAHif-lx9AY2abGmo836xFz0TWHQCmTu_7Y"
ADMIN_ID = 5576359465

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# Слушаем САМЫЙ КОРЕНЬ сайта. Сюда будут приходить и GET (от тебя), и POST (от Telegram)
@app.route('/', methods=['GET', 'POST'])
def handle_root():
    if request.method == 'POST':
        if request.is_json:
            update = telebot.types.Update.de_json(request.get_json())
            bot.process_new_updates([update])
            return 'OK', 200
        return 'Not JSON', 400
    # Если зашли через браузер — покажет эту строку
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
    user_states[message.chat.id] = 'waiting_for_text'
    bot.reply_to(message, "Напиши своё сообщение для создателя:")

@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == 'waiting_for_text')
def forward_to_admin(message):
    user_states[message.chat.id] = None
    if ADMIN_ID == 0:
        bot.reply_to(message, f"ADMIN_ID не настроен. Твой ID: {message.chat.id}")
        return
    report = f"Имя: {message.from_user.first_name}\nАйди: {message.chat.id}\nСообщение: *{message.text}*"
    try:
        bot.send_message(ADMIN_ID, report, parse_mode='Markdown')
        bot.reply_to(message, "Твое сообщение отправлено создателю!")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

@bot.message_handler(commands=['id'])
def reply_to_user(message):
    if ADMIN_ID != 0 and message.chat.id != ADMIN_ID:
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
