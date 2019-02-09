from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from work_materials.globals import castles, build_menu, classes_list, cursor, moscow_tz, admin_ids
from libs.shipper_store import Shipper

import datetime

shippers = []

HOURS_BETWEEN_SHIPPER = 4


def shipper_force(bot, update, user_data):
    shipper(bot, update, user_data, force=True)


def shipper(bot, update, user_data, force = False):
    if isinstance(update, int):
        chat_id = update
    else:
        chat_id = update.message.chat_id
    last_shipper_time = user_data.get("last_shipper_time")
    if not force and last_shipper_time is not None and \
            last_shipper_time - datetime.datetime.now(tz=moscow_tz).replace(tzinfo=None) < datetime.timedelta(hours=HOURS_BETWEEN_SHIPPER):
        response = "Время ещё не пришло. Должно пройти {0} часа после предыдущей попытки.".format(HOURS_BETWEEN_SHIPPER)
        if chat_id in admin_ids:
            response += "\nВы можете пропустить ожидание: /shipper_force"
        bot.send_message(chat_id=chat_id, text=response)
        return
    __castle_buttons = []
    for castle in castles:
        __castle_buttons.append(KeyboardButton(castle))
    reply_markup = ReplyKeyboardMarkup(build_menu(__castle_buttons, 4, footer_buttons=[KeyboardButton('Случайный замок')]), resize_keyboard=True)
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
    reply_markup = ReplyKeyboardMarkup(build_menu(__class_buttons, 3, footer_buttons=[KeyboardButton('Случайный класс')]), resize_keyboard=True, one_time_keyboard=True)
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
    player_castle = user_data.get("castle")
    player_game_class = user_data.get("game_class")
    player_id = user_data.get("player_id")
    request = "select telegram_username, times_shippered, player_id, castle, game_class from players "
    request += "where " if search_castle != -1 or search_class != -1 else ""
    request += "castle = %s " if search_castle != -1 else "" + "and " if search_class != -1 and search_castle != -1 else "" + "game_class = %s " if search_class != -1 else ""
    request += "order by times_shippered limit 1"
    args = []
    if search_castle != -1:
        args.append(search_castle)
    if search_class != -1:
        args.append(search_class)
    cursor.execute(request, args)
    row = cursor.fetchone()
    if row is None:
        bot.send_message(chat_id = update.message.chat_id, text = "Любовь найти трудно, мы никого не нашли. Попробуй ещё раз: /shipper")
        return
    times_shippered = row[1] + 1
    now = datetime.datetime.now(tz=moscow_tz).replace(tzinfo=None)
    request = "update players set times_shippered = %s, last_shippered = %s where player_id = %s"
    cursor.execute(request, (times_shippered, now, row[2]))
    request = "insert into shippers(initiator_player_id, shippered_player_id, time_shippered) VALUES (%s, %s, %s) returning shipper_id"
    cursor.execute(request, (player_id, row[2], now))
    row_temp = cursor.fetchone()
    current = Shipper(row_temp[0], player_id, update.message.from_user.username, player_castle, player_game_class, row[2], row[0], row[3], row[4], now)
    shippers.append(current)
    bot.send_message(chat_id = update.message.chat_id,
                     text = "Смотри, кого мы нашли! @{0}\nПовторить попытку можно будет через {1} часа: /shipper\n"
                            "Написать тайно: /shadow_letter_{2}".format(row[0], HOURS_BETWEEN_SHIPPER, row_temp[0]))
    user_data.update({"last_shipper_time" : now})