#!/usr/bin/env python

import recognizer
import c_sql
from datetime import datetime
from os import path

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
db_path = 'recognizer_DB.db'

CONV_END = 0
origin_path = path.dirname(__file__)

async def to_log(message):
    with open(origin_path + '/com_hist.log', 'a') as f:
        f.write(f'{datetime.now()} - {message}\n')
        print(message)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the conversation and asks the user about their gender."""
    user = update.message.from_user
    await to_log(f'''{user.username}({user.id}) - "{update.message.text}"''')
    await update.message.reply_text(
        "Привет! Это бот распознавания изображений.\n"
        "Выполнен группой №3.\n\n"
        "Я умею определять следующие классы: \n"
        "buildings, forest, glacier, mountain, sea, street \n"
        "Направь мне картинку, и я скажу, что на ней изображено.",
    )


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for a verification."""
    reply_keyboard = [["Да", "Нет"]]
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    start_time = datetime.now()
    file_name = origin_path + '/Photos/' + str(user.id) + '_' + str(int(start_time.timestamp())) + '.jpg'
    await photo_file.download_to_drive(file_name)
    del photo_file
    await to_log(f"Photo of {user}: {file_name}")
    await update.message.reply_text(
        "Отлично! Теперь мне нужно немного времени для анализа."
    )

    st_time = datetime.now()
    probabilities, result = recognizer.start_recognition(file_name)
    str_probabilities = '\n'.join(str(key) +': ' + str(value) for key, value in probabilities.items())
    model_time = round(float((datetime.now() - st_time).total_seconds()), 2)

    # Store contex data in variable
    contex_var = {
        'start_time': start_time,
        'user_id': user.id,
        'user_name': user.first_name,
        'photo_path': file_name,
        'model_time': model_time,
        'probabilities': str_probabilities.replace('\n', ','),
        'result': result,
        'user_reply': '',
        'correct_flg': ''
    }
    context.user_data['var'] = contex_var

    await update.message.reply_text(
        f"{str_probabilities}\n"
        f"Класс объекта на картинке: {result}, Верно?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Верно?"
        ),
    )
    return CONV_END


async def conv_end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user

    reply_dict = {"Да": 1, "Нет": 0}
    correct_flg = reply_dict[update.message.text] if not reply_dict.get(update.message.text) == None else 'Null'
    # get contex variable to send it to db
    contex_var = context.user_data.get('var')
    contex_var['user_reply'] = update.message.text
    contex_var['correct_flg'] = correct_flg
    c_sql.write_result(db_path, contex_var)

    await to_log(f"Reply of {user.first_name}: {update.message.text}")
    await update.message.reply_text(
        "Спасибо!", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    await to_log(f"User {user.first_name} canceled the conversation.", )
    await update.message.reply_text(
        "Пока! Буду ждать твоего возвращения.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def stat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    user = update.message.from_user
    stat_result = c_sql.get_stat(db_path)
    await to_log(f'''{user.username}({user.id}) - "{update.message.text}"''')
    # if user.id == DEVELOPER_CHAT_ID:
    await update.message.reply_text(
        "Статистика по работе бота:\n"
        f"Всего записей: {stat_result[0]}\n"
        f"Получено ответов: {stat_result[1]}\n"
        f"Верно определено: {stat_result[2]}%\n"
        f"Среднее время работы модели: {stat_result[3]}с\n"
    )

async def clear_stat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    user = update.message.from_user
    c_sql.clr_stat(db_path)
    await to_log(f'''{user.username}({user.id}) - "{update.message.text}"''')
    # if user.id == DEVELOPER_CHAT_ID:
    await update.message.reply_text(
        "Статистика работы бота очищена:\n"
    )


async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    user = update.message.from_user
    await to_log(f'''{user.username}({user.id}) - "{update.message.text}"''')
    # if user.id == DEVELOPER_CHAT_ID:
    await send_logs(update, context)


async def send_logs(update, context):
    chat_id = update.message.chat_id
    document = open(origin_path + '/com_hist.log', 'rb')
    await context.bot.send_document(chat_id, document)


def main() -> None:
    """init DB"""
    c_sql.init_db(db_path)
    to_log("init DB - done")
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
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
    application.add_handler(CommandHandler("stat", stat_command))
    application.add_handler(CommandHandler("clrstat", clear_stat_command))
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
