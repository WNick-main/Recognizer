#!/usr/bin/env python

import logging
import recognizer
import datetime
import os

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

token = ""
DEVELOPER_CHAT_ID = 

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

CONV_END = 0
origin_path =  '/scripts/recognizer' # os.path.abspath("") #


async def to_log(message):
    with open(origin_path + '/com_hist.log', 'a') as f:
        f.write(f'{datetime.datetime.now()} - {message}\n')
        print(message)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды Старт, выведение преветственного сообщения"""
    user = update.message.from_user
    await to_log(f'''{user.username}({user.id}) - "{update.message.text}"''')
    await update.message.reply_text(
        "Привет! Это бот распознавания изображений.\n"
        "Выполнен группой №3.\n\n"
        "Направь мне картинку, и я скажу, что там изображено.",
    )


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Загрузка фото, обработка и выдача сообщения о результате обработки"""
    reply_keyboard = [["Да", "Нет"]]

    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    file_name = origin_path + '/Photos/' + str(user.id) + '_' + str(int(datetime.datetime.now().timestamp())) + '.jpg'
    await photo_file.download_to_drive(file_name)
    await to_log(f"Photo of {user}: {file_name}")
    await update.message.reply_text(
        "Отлично! Теперь мне нужно немного времени для анализа."
    )

    probabilities, result = recognizer.start_recognition(file_name)
    str_probabilities = '\n'.join(str(key) +': ' + str(value) for key, value in probabilities.items())
    await update.message.reply_text(
        f"{str_probabilities}\n"
        f"Класс объекта на картинке: {result}, Верно?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Верно?"
        ),
    )
    return CONV_END


async def conv_end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Завершение разговора"""
    user = update.message.from_user
    await to_log(f"Reply of {user.first_name}: {update.message.text}")
    await update.message.reply_text(
        "Спасибо!", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена со стороны пользователя"""
    user = update.message.from_user
    await to_log(f"User {user.first_name} canceled the conversation.", )
    await update.message.reply_text(
        "Пока! Буду ждать твоего возвращения.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Запись в лог"""
    user = update.message.from_user
    await to_log(f'''{user.username}({user.id}) - "{update.message.text}"''')
    await send_logs(update, context)


async def send_logs(update, context):
    '''Отправка логов'''
    chat_id = update.message.chat_id
    document = open(origin_path + '/com_hist.log', 'rb')
    await context.bot.send_document(chat_id, document)


def main() -> None:
    """Запуск бота"""
    application = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.PHOTO, photo)],
        states={
            CONV_END: [MessageHandler(filters.TEXT & ~filters.COMMAND, conv_end)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("logs", logs_command))

    application.run_polling()


if __name__ == "__main__":
    main()
