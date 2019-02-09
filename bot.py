from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, Filters

from work_materials.globals import updater, dispatcher, job, castles as castles_const, classes_list as classes_const,\
    conn, cursor
import work_materials.globals as globals
from libs.start_pult import rebuild_pult

from bin.save_load_user_data import loadData, saveData

from bin.pult_callback import pult_callback
from bin.shipper import shipper, shipper_selected_castle, shipper_selected_class, shipper_force

from work_materials.filters.service_filters import filter_is_admin
from work_materials.filters.shipper_filters import filter_shipper_castle, filter_shipper_class

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


def delete_self(bot, update, user_data):
    user_data.clear()
    request = "delete from players where telegram_id = %s"
    cursor.execute(request, (update.message.from_user.id,))
    bot.send_message(chat_id = update.message.chat_id, text = "Удаление завершено")
    start(bot, update, user_data)


def inline_callback(bot, update, user_data):
    if update.callback_query.data.find("p") == 0:
        pult_callback(bot, update, user_data)
        return


dispatcher.add_handler(CommandHandler('start', start, pass_user_data=True))
dispatcher.add_handler(CommandHandler('delete_self', delete_self, filters=filter_is_admin, pass_user_data=True))

dispatcher.add_handler(CommandHandler('shipper', shipper, pass_user_data=True))
dispatcher.add_handler(CommandHandler('shipper_force', shipper_force, filters=filter_is_admin, pass_user_data=True))
dispatcher.add_handler(MessageHandler(Filters.text & filter_shipper_castle, shipper_selected_castle, pass_user_data=True))
dispatcher.add_handler(MessageHandler(Filters.text & filter_shipper_class, shipper_selected_class, pass_user_data=True))

dispatcher.add_handler(CallbackQueryHandler(inline_callback, pass_update_queue=False, pass_user_data=True))

loadData()
save_user_data = threading.Thread(target=saveData, name="Save User Data")
save_user_data.start()
updater.start_polling(clean=False)

# Останавливаем бота, если были нажаты Ctrl + C
updater.idle()
globals.processing = 0
# Разрываем подключение к бд.
conn.close()
