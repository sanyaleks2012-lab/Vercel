import os
import telebot
from flask import Flask, request

# Инициализируем токен и ID админа из переменных окружения Vercel
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# Хранилище состояний, чтобы бот знал, что пользователь сейчас пишет вопрос
# В Serverless это работает для одного запроса, для масштаба лучше БД, но для базы хватит
user_states = {}

@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        return 'Invalid request', 403

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Используй /bio для ссылки или /message, чтобы написать создателю.")

# Команда /bio
@bot.message_handler(commands=['bio'])
def send_bio(message):
    bot.reply_to(message, "https://sanyaleks2012-lab.github.io/bio/")

# Команда /message (начало ввода вопроса)
@bot.message_handler(commands=['message'])
def start_message(message):
    user_states[message.chat.id] = 'waiting_for_text'
    bot.reply_to(message, "Напиши своё сообщение для создателя:")

# Обработка текста сообщения для создателя
@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == 'waiting_for_text')
def forward_to_admin(message):
    # Сбрасываем состояние
    user_states[message.chat.id] = None
    
    # Формируем красивый шаблон для админа
    report = (
        f"Имя: {message.from_user.first_name}\n"
        f"Айди: {message.chat.id}\n"
        f"Сообщение: *{message.text}*"
    )
    
    try:
        # Отправляем админу
        bot.send_message(ADMIN_ID, report, parse_mode='Markdown')
        bot.reply_to(message, "Твое сообщение отправлено создателю!")
    except Exception as e:
        bot.reply_to(message, "Не удалось отправить сообщение. Проверь настройки ADMIN_ID.")

# Команда для админа /id [USER_ID] [ТЕКСТ]
@bot.message_handler(commands=['id'])
def reply_to_user(message):
    if message.chat.id != ADMIN_ID:
        return # Игнорим, если пишет не админ

    try:
        # Разбиваем текст команды. Пример: "/id 123456 привет"
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            bot.reply_to(message, "Ошибка! Формат: /id [айди] [сообщение]")
            return
        
        target_id = int(parts[1])
        reply_text = parts[2]
        
        # Отправляем пользователю ответ напрямую от бота
        bot.send_message(target_id, reply_text)
        bot.reply_to(message, f"Ответ успешно доставлен пользователю {target_id}!")
    except ValueError:
        bot.reply_to(message, "Неверный формат ID. Он должен быть числом.")
    except Exception as e:
        bot.reply_to(message, f"Не удалось отправить: {str(e)}")
        