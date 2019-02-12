from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, Filters

from work_materials.globals import updater, dispatcher, job, castles as castles_const, classes_list as classes_const,\
    conn, cursor, admin_ids
import work_materials.globals as globals
from libs.start_pult import rebuild_pult

from bin.save_load_user_data import loadData, saveData

from bin.pult_callback import pult_callback
from bin.shipper import shipper, shipper_selected_castle, shipper_selected_class, shipper_force, shadow_letter, \
    shadow_letter_confirm, shadow_letter_send, shadow_letter_cancel, fill_shippers, shipper_mute, shipper_unmute
from bin.profile import profile, shipper_history

from work_materials.filters.service_filters import filter_is_admin, filter_only_registration, filter_delete_yourself
from work_materials.filters.shipper_filters import filter_shipper_castle, filter_shipper_class, filter_mute_shipper, filter_unmute_shipper
from work_materials.filters.shadow_letter_filters import filter_shadow_letter, filter_awaiting_shadow_letter, filter_confirm_shadow_letter, filter_cancel_shadow_letter

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


def help(bot, update):
    response = "Данный бот предназначен для помощи игрокам чв в нахождении вторых половинок и приурочен к 14 февраля.\nСписок доступных команд:\n"
    response += "/start - Регистрация в боте, всё очевидно.\n/shipper - Начать процесс поиска, можно использовать 1 раз в 4 часа\n"
    response += "/delete_self - Удаление регистрации, можно использовать до первого успешного /shipper\n"
    response += "/profile - Отображение основной информации.\n/shipper_history - Отображение истории поиска\n"
    response += "Так же доступны некоторые другие команды, подсказки будут возникать по ходу использования.\n\n"
    if update.message.from_user.id in admin_ids:
        response += "<b>Admin features:</b>\n"
        response += "/delete_self - аналогично, но работает в любое время (использовать с огромной осторожностью, " \
                    "возможна значительная потеря данных\n/shipper_force - Тот же шиппер, но с игнорированием временных " \
                    "ограничений, не будет учитываться в статистике и при самом шиппере."
    bot.send_message(chat_id = update.message.chat_id, text = response, parse_mode = 'HTML')


def inline_callback(bot, update, user_data):
    if update.callback_query.data.find("p") == 0:
        pult_callback(bot, update, user_data)
        return


def only_registration(bot, update):
    bot.send_message(chat_id = update.message.chat_id,
                     text = "До 14 февраля доступна только регистрация! Наберитесь терпения!\n"
                            "Вы можете использовать /profile для проверки регистрации")


def unknown_message(bot, update):
    bot.send_message(chat_id = update.message.chat_id, text = "Некорректный ввод, попробуйте повторить /shipper")


dispatcher.add_handler(CommandHandler('start', start, pass_user_data=True))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('profile', profile, pass_user_data=True))
dispatcher.add_handler(CommandHandler('shipper_history', shipper_history, pass_user_data=True))
dispatcher.add_handler(CommandHandler('delete_self', delete_self, filters=filter_is_admin, pass_user_data=True))
dispatcher.add_handler(CommandHandler('delete_self', delete_self, filters=filter_delete_yourself, pass_user_data=True))

dispatcher.add_handler(CommandHandler('shipper_force', shipper_force, filters=filter_is_admin, pass_user_data=True))

dispatcher.add_handler(MessageHandler(filter_only_registration, only_registration))
dispatcher.add_handler(CommandHandler('shipper', shipper, pass_user_data=True))
dispatcher.add_handler(MessageHandler(Filters.text & filter_shipper_castle, shipper_selected_castle, pass_user_data=True))
dispatcher.add_handler(MessageHandler(Filters.text & filter_shipper_class, shipper_selected_class, pass_user_data=True))

dispatcher.add_handler(MessageHandler(Filters.command & filter_shadow_letter, shadow_letter, pass_user_data=True))
dispatcher.add_handler(MessageHandler(Filters.text & filter_awaiting_shadow_letter, shadow_letter_confirm, pass_user_data=True))
dispatcher.add_handler(MessageHandler(Filters.command & filter_confirm_shadow_letter, shadow_letter_send, pass_user_data=True))
dispatcher.add_handler(MessageHandler(Filters.command & filter_cancel_shadow_letter, shadow_letter_cancel, pass_user_data=True))
dispatcher.add_handler(MessageHandler(Filters.command & filter_mute_shipper, shipper_mute, pass_user_data=True))
dispatcher.add_handler(MessageHandler(Filters.command & filter_unmute_shipper, shipper_unmute, pass_user_data=True))

dispatcher.add_handler(MessageHandler(Filters.all, unknown_message))

dispatcher.add_handler(CallbackQueryHandler(inline_callback, pass_update_queue=False, pass_user_data=True))

loadData()
fill_shippers()
save_user_data = threading.Thread(target=saveData, name="Save User Data")
save_user_data.start()
updater.start_polling(clean=False)

# Останавливаем бота, если были нажаты Ctrl + C
updater.idle()
globals.processing = 0
# Разрываем подключение к бд.
conn.close()
