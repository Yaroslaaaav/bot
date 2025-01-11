import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


DEEPSEEK_API_KEY = "sk-cb4cefac20a54b53a48424583d7678b4"  
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"  
TELEGRAM_BOT_TOKEN = "7836111015:AAH3qAA-2b44JLUvJzaC5QDx-5ERXP-11AM"  


async def get_deepseek_response(prompt):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "DeepSeek--chat",  
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Ошибка при запросе к API DeepSeek."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот, использующий DeepSeek API. Напиши мне что-нибудь!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = await get_deepseek_response(user_message)
    await update.message.reply_text(response)


def main():
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    
    application.run_polling()

if __name__ == "__main__":
    main()