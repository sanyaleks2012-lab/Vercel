import telebot
from flask import Flask, request

# Вшиваем токен прямо в код
TOKEN = "8912150974:AAHif-lx9AY2abGmo836xFz0TWHQCmTu_7Y"

# Впиши сюда свой числовой ID (например, 123456789), если бот напишет его тебе в чате.
# Пока оставим 0 или твой ID, если ты его помнишь.
ADMIN_ID = 0  

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.is_json:
        update = telebot.types.Update.de_json(request.get_json())
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Invalid', 400

@app.route('/', methods=['GET'])
def index():
    return 'Bot is running...', 200

user_states = {}

# Команда /start также покажет пользователю его ID (полезно, чтобы узнать свой ADMIN_ID)
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
    
    # Если ты еще не поменял ADMIN_ID в коде, бот напишет это тебе прямо в чат
    if ADMIN_ID == 0:
        bot.reply_to(message, f"Ошибка: ADMIN_ID не настроен в коде. Твой ID: {message.chat.id}. Вшей его в переменную ADMIN_ID!")
        return

    report = (
        f"Имя: {message.from_user.first_name}\n"
        f"Айди: {message.chat.id}\n"
        f"Сообщение: *{message.text}*"
    )
    try:
        bot.send_message(ADMIN_ID, report, parse_mode='Markdown')
        bot.reply_to(message, "Твое сообщение отправлено создателю!")
    except Exception as e:
        bot.reply_to(message, f"Не удалось отправить админу. Ошибка: {str(e)}")

@bot.message_handler(commands=['id'])
def reply_to_user(message):
    # Если ADMIN_ID еще 0, разрешаем команду для теста
    if ADMIN_ID != 0 and message.chat.id != ADMIN_ID:
        return
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            bot.reply_to(message, "Ошибка! Формат: /id [айди] [сообщение]")
            return
        target_id = int(parts[1])
        reply_text = parts[2]
        bot.send_message(target_id, reply_text)
        bot.reply_to(message, f"Ответ отправлен пользователю {target_id}!")
    except Exception as e:
        bot.reply_to(message, f"Ошибка отправки: {str(e)}")
