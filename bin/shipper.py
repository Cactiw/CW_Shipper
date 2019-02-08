from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from work_materials.globals import castles, build_menu, classes_list

def shipper(bot, update, user_data):
    if isinstance(update, int):
        chat_id = update
    else:
        chat_id = update.message.chat_id
    __castle_buttons = []
    for castle in castles:
        __castle_buttons.append(KeyboardButton(castle))
    reply_markup = ReplyKeyboardMarkup(build_menu(__castle_buttons, 4, footer_buttons=[KeyboardButton('Случайный замок')]))
    user_data.update({"status" : 'choosing castle'})
    bot.send_message(chat_id = chat_id, text = "Чувствуешь ли ты в каком замке живет твоя любовь?",
                     reply_markup = reply_markup)

def shipper_castle(bot, update, user_data):
    mes = update.message
    castle = mes.text if mes.text in castles else -1
    user_data.update({"search_castle": castle, "status" : "selecting class"})
    __class_buttons = []
    for curr_class in classes_list:
        __class_buttons.append(curr_class)
    reply_markup = ReplyKeyboardMarkup(build_menu(__class_buttons, 3, footer_buttons=[KeyboardButton('Случайный класс')]))
    bot.send_message(chat_id = mes.chat_id, text = "Знаешь ли ты, кем является твоя любовь?",
                     reply_markup = reply_markup)
