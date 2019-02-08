from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from work_materials.globals import castles, build_menu, classes_list, cursor, moscow_tz

import datetime

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


def shipper_selected_castle(bot, update, user_data):
    mes = update.message
    castle = mes.text if mes.text in castles else -1
    user_data.update({"search_castle": castle, "status" : "choosing class"})
    __class_buttons = []
    for curr_class in classes_list:
        __class_buttons.append(curr_class)
    reply_markup = ReplyKeyboardMarkup(build_menu(__class_buttons, 3, footer_buttons=[KeyboardButton('Случайный класс')]))
    bot.send_message(chat_id = mes.chat_id, text = "Знаешь ли ты, кем является твоя любовь?",
                     reply_markup = reply_markup)


def shipper_selected_class(bot, update, user_data):
    mes = update.message
    game_class = mes.text if mes.text in classes_list else -1
    user_data.update({"search_class": game_class, "status": "selected class"})
    shipper_search(bot, update, user_data)
    return


def shipper_search(bot, update, user_data):
    search_castle = user_data.get("search_castle")
    search_class = user_data.get("search_class")
    player_id = user_data.get("player_id")
    request = "select telegram_username, times_shippered, player_id from players where castle = %s and game_class = %s order by times_shippered limit 1"
    cursor.execute(request, (search_castle, search_class))
    row = cursor.fetchone()
    if row is None:
        bot.send_message(chat_id = update.message.chat_id, text = "Любовь найти трудно, мы никого не нашли")
        return
    bot.send_message(chat_id = update.message.chat_id, text = "Смотри, кого мы нашли! @{0}".format(row[0]))
    times_shippered = row[1] + 1
    request = "update players set times_shippered = %s, last_shippered = %s where player_id = %s"
    now = datetime.datetime.now(tz=moscow_tz).replace(tzinfo=None)
    cursor.execute(request, (times_shippered, now, row[2]))
    request = "insert into shippers(initiator_player_id, shippered_player_id, time_shippered) VALUES (%s, %s, %s)"
    cursor.execute(request, (player_id, row[2], now))
    user_data.update({"last_shipper_time" : now})