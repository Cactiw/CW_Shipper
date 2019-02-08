from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler

from work_materials.globals import updater, dispatcher, job, castles as castles_const, classes_list as classes_const,\
    conn, cursor
import work_materials.globals as globals
from libs.start_pult import rebuild_pult

from bin.pult_callback import pult_callback
from bin.save_load_user_data import loadData, saveData

import traceback, logging, datetime, threading

#   Выставляем логгироввание
console = logging.StreamHandler()
console.setLevel(logging.INFO)

log_file = logging.FileHandler(filename='error.log', mode='a')
log_file.setLevel(logging.ERROR)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO, handlers=[log_file, console])


def start(bot, update, user_data):
    mes = update.message
    if user_data.get('class') is not None:
        bot.send_message(chat_id = mes.chat_id, text = "Вы уже зарегистрированы!")
        return
    pult_status = {'castle' : -1, 'class' : -1}
    user_data.update({'castles' : castles_const.copy(), 'classes' : classes_const.copy(), 'start_pult_status' : pult_status})
    reply_markup = rebuild_pult("default", None, user_data)
    bot.send_message(chat_id = mes.chat_id, text = "Выберите замок и класс!", reply_markup = reply_markup)



def inline_callback(bot, update, user_data):
    if update.callback_query.data.find("p") == 0:
        pult_callback(bot, update, user_data)
        return

dispatcher.add_handler(CommandHandler('start', start, pass_user_data=True))

dispatcher.add_handler(CallbackQueryHandler(inline_callback, pass_update_queue=False, pass_user_data=True))

loadData()
updater.start_polling(clean=False)
save_user_data = threading.Thread(target=saveData, name="Save User Data")
save_user_data.start()

# Останавливаем бота, если были нажаты Ctrl + C
updater.idle()
globals.processing = 0
# Разрываем подключение.
conn.close()
