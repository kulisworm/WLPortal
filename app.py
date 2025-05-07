#В файлах templates/index.html и templates/success.html 
#вы можете отредактировать заголовки и всю Веб Страницу.

from flask import Flask, render_template, request, send_from_directory
from rcon.source import Client
import telebot
import threading

# --- Настройки ---
RCON_HOST = "IP Minecraft сервера"
RCON_PASSWORD = "RCON пароль сервера"
RCON_PORT = 25575
TOKEN = 'Токен бота Telegram'
ADMIN_CHAT_ID = 'Chat ID администратора(ваш)'

# --- Инициализация ---
app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

# --- Маршруты сайта ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route('/wwwroot/<path:path>')
def wwwroot(path):
    return send_from_directory('wwwroot', path)

@app.route("/add_whitelist", methods=["POST"])
def add_whitelist():
    print("Получен запрос на добавление в whitelist")
    username = request.form.get("username_minecaft")
    username_tg = request.form.get("username_tg")
    print(f"Делаем запрос в тг бота на добавление {username} в whitelist, tg: {username_tg}")

    keyboard = telebot.types.InlineKeyboardMarkup()
    button_save = telebot.types.InlineKeyboardButton(text="✅", callback_data=f'passed:{username}')
    button_change = telebot.types.InlineKeyboardButton(text="❌", callback_data='deny')
    keyboard.add(button_save, button_change)

    bot.send_message(
        ADMIN_CHAT_ID,
        f'Новый запрос на добавление в whitelist от пользователя с ником {username} и тг {username_tg}',
        reply_markup=keyboard
    )
    return render_template('success.html')

# --- Потоки ---
def start_web():
    app.run(host='0.0.0.0')  # или port=5000 при необходимости

def start_bot():
    @bot.message_handler(commands=['start'])
    def start_command(message):
        bot.send_message(message.chat.id, "Админ панель активна!")

    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        if call.data.startswith("passed:"):
            nickname = call.data.split(":", 1)[1]
            with Client(RCON_HOST, RCON_PORT, passwd=RCON_PASSWORD) as client:
                response = client.run(f'whitelist add {nickname}')
                bot.send_message(call.message.chat.id, f"✅ Игрок `{nickname}` добавлен в вайтлист.\nОтвет сервера: {response}", parse_mode="Markdown")
        elif call.data == "deny":
            bot.send_message(call.message.chat.id, "❌ Запрос отклонён.")

    bot.infinity_polling()

# --- Запуск ---
if __name__ == '__main__':
    flask_thread = threading.Thread(target=start_web)
    bot_thread = threading.Thread(target=start_bot)

    flask_thread.start()
    bot_thread.start()

    flask_thread.join()
    bot_thread.join()
