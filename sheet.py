import os
import logging
from typing import List, Dict, Any
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters
import requests

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
TELEGRAM_BOT_TOKEN: str = os.getenv("7836111015:AAH3qAA-2b44JLUvJzaC5QDx-5ERXP-11AM")
DEEPSEEK_API_KEY: str = os.getenv("sk-cb4cefac20a54b53a48424583d7678b4")

# Создание Flask-приложения
app: Flask = Flask(__name__)

# Инициализация бота
bot: Bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher: Dispatcher = Dispatcher(bot, None, workers=0)

# Обработчик команды /start
def start(update: Update, context: Any) -> None:
    update.message.reply_text("Привет! Я твой бот с интеграцией DeepSeek. Используй /search <запрос> для поиска.")

# Обработчик команды /search
def search(update: Update, context: Any) -> None:
    query: str = " ".join(context.args)
    if not query:
        update.message.reply_text("Пожалуйста, укажите запрос для поиска.")
        return

    try:
        # Запрос к API DeepSeek
        response: requests.Response = requests.get(
            "https://api.deepseek.com/v1/search",
            params={"query": query, "api_key": DEEPSEEK_API_KEY},
        )
        results: List[Dict[str, str]] = response.json().get("results", [])

        if results:
            # Отправка первых 3 результатов
            message: str = "\n\n".join(
                [f"{i + 1}. {result['title']}\n{result['url']}" for i, result in enumerate(results[:3])]
            )
            update.message.reply_text(f"Результаты поиска:\n\n{message}")
        else:
            update.message.reply_text("По вашему запросу ничего не найдено.")
    except Exception as e:
        logger.error(f"Ошибка при запросе к DeepSeek API: {e}")
        update.message.reply_text("Произошла ошибка при поиске. Попробуйте позже.")

# Обработчик текстовых сообщений
def echo(update: Update, context: Any) -> None:
    update.message.reply_text("Я не понимаю эту команду. Попробуй /search <запрос>.")

# Регистрация обработчиков
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("search", search))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Вебхук для Telegram
@app.route("/webhook", methods=["POST"])
def webhook() -> jsonify:
    update: Update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return jsonify({"status": "ok"})

# Запуск сервера
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 3000)))
