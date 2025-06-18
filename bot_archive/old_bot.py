from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Настройки (ApplicationBuilder вместо Updater)
application = ApplicationBuilder().token("7713136125:AAFasp35wApuyqsWqka2qCeajpFnjSs6kdc").build()

# Обработка команд
async def startCommand(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Привет, давай пообщаемся?')

async def textMessage(update, context):
    response = 'Получил Ваше сообщение: ' + update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

# Хендлеры
application.add_handler(CommandHandler("start", startCommand))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), textMessage))

# Запуск бота
application.run_polling()