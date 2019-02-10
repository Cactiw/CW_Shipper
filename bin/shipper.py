from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.error import BadRequest, Unauthorized, TelegramError
from work_materials.globals import castles, build_menu, classes_list, cursor, moscow_tz, admin_ids
from libs.shipper_store import Shipper

import datetime

shippers = {}

HOURS_BETWEEN_SHIPPER = 4


def shipper_force(bot, update, user_data):
    shipper(bot, update, user_data, force=True)


def shipper(bot, update, user_data, force = False):
    if isinstance(update, int):
        chat_id = update
    else:
        chat_id = update.message.chat_id
    last_shipper_time = user_data.get("last_shipper_time")
    print(not force, last_shipper_time is not None, last_shipper_time)#, datetime.datetime.now(tz=moscow_tz).replace(tzinfo=None) - last_shipper_time, datetime.datetime.now(tz=moscow_tz).replace(tzinfo=None) - last_shipper_time < datetime.timedelta(hours=HOURS_BETWEEN_SHIPPER))
    if not force and last_shipper_time is not None and \
            datetime.datetime.now(tz=moscow_tz).replace(tzinfo=None) - last_shipper_time < datetime.timedelta(hours=HOURS_BETWEEN_SHIPPER):
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
    print(search_class)
    request = "select telegram_username, times_shippered, player_id, castle, game_class, telegram_id from players where telegram_id != %s "
    request += ("and castle = %s " if search_castle != -1 else "") + ("and game_class = %s " if search_class != -1 else "")
    request += "order by times_shippered"
    args = [update.message.from_user.id]
    if search_castle != -1:
        args.append(search_castle)
    if search_class != -1:
        args.append(search_class)
    print(request, args)
    cursor.execute(request, tuple(args))
    row = cursor.fetchone()
    not_found = False
    if row is None:
        not_found = True
        if search_castle != -1 and search_class != -1:
            request = "select telegram_username, times_shippered, player_id, castle, game_class, telegram_id from players where " \
                      "telegram_id != %s and (castle = %s or game_class = %s) order by times_shippered"
            cursor.execute(request, (update.message.from_user.id, search_castle, search_class))
            row = cursor.fetchone()
        if row is None:
            request = "select telegram_username, times_shippered, player_id, castle, game_class, telegram_id from players where " \
                      "telegram_id != %s order by times_shippered"
            cursor.execute(request, (update.message.from_user.id,))
            row = cursor.fetchone()
        if row is None:
            bot.send_message(chat_id = update.message.chat_id, text = "Любовь найти трудно, мы никого не нашли. Попробуй ещё раз: /shipper")
            return
    first_row = row
    while row:
        suitable = True
        for shipper in list(shippers.values()):
            if (shipper.initiator.telegram_id == update.from_user.id and shipper.shippered.telegram_id == row[5]) or \
                    (shipper.shippered.telegram_id == row[5] and shipper.shippered.telegram_id == update.message.from_user.id):
                row = cursor.fetchone()
                suitable = False
                break
        if suitable:
            break
    if row is None:
        row = first_row
        not_found = True
    times_shippered = row[1] + 1
    now = datetime.datetime.now(tz=moscow_tz).replace(tzinfo=None)
    request = "update players set times_shippered = %s, last_shippered = %s where player_id = %s"
    cursor.execute(request, (times_shippered, now, row[2]))
    request = "insert into shippers(initiator_player_id, shippered_player_id, time_shippered) VALUES (%s, %s, %s) returning shipper_id"
    cursor.execute(request, (player_id, row[2], now))
    row_temp = cursor.fetchone()
    current = Shipper(row_temp[0], update.message.from_user.id, update.message.from_user.username, player_castle, player_game_class, row[5], row[0], row[3], row[4], now)
    shippers.update({row_temp[0] : current})
    if not not_found:
        response = "Смотри, кого мы нашли! @{0}\nПовторить попытку можно будет через {1} часа: /shipper\n"\
            "Написать тайно: /shadow_letter_{2}".format(row[0], HOURS_BETWEEN_SHIPPER, row_temp[0])
    else:
        response = "Любовь найти трудно, наиболее близким к запросу оказался @{0}\nПовторить попытку можно будет через {1} часа: /shipper\n"\
            "Написать тайно: /shadow_letter_{2}".format(row[0], HOURS_BETWEEN_SHIPPER, row_temp[0])
    bot.send_message(chat_id = update.message.chat_id,
                     text = response)
    user_data.update({"last_shipper_time" : now})


def shadow_letter(bot, update, user_data):
    mes = update.message
    try:
        shipper_id = int(mes.text.partition("@")[0].split("_")[2])
    except ValueError:
        bot.send_message(chat_id = mes.chat_id, text = "Проверьте синтаксис и попробуйте ещё раз")
        return
    shipper = shippers.get(shipper_id)
    if shipper is None:
        bot.send_message(chat_id=mes.chat_id, text="Не найдено. Попробуйте ещё раз")
        return
    print(shipper.initiator.telegram_id, mes.from_user.id)
    if shipper.initiator.telegram_id != mes.from_user.id:
        bot.send_message(chat_id=mes.chat_id, text="Не надо хитрить!")
        return
    user_data.update({"status": "awaiting_shadow_letter", "shipper_to_send" : shipper})
    bot.send_message(chat_id = mes.chat_id,
                     text = "Текст, который вы напишете далее будет анонимно отправлен @{0}. "
                            "Используйте /cancel_shadow_letter для отмены.".format(shipper.shippered.telegram_username))


def shadow_letter_confirm(bot, update, user_data):
    mes = update.message
    if len(mes.text) > 1900:
        bot.send_message(chat_id = mes.chat_id, text = "Размер сообщения ограничен 1900 символами!")
        return
    bot.send_message(chat_id = mes.chat_id, text = "Следующий текст будет отправлен:\n{0}"
                                                   "\n\nПодтвердить отправку: /confirm_shadow_letter"
                                                   "\nОтменить отправку: /cancel_shadow_letter".format(mes.text))
    user_data.update({"shadow_letter_text" : mes.text, "status": "awaiting_letter_confirmation"})


def shadow_letter_send(bot, update, user_data):
    mes = update.message
    text = user_data.get("shadow_letter_text")
    shipper = user_data.get("shipper_to_send")
    try:
        bot.send_message(chat_id = shipper.shippered.telegram_id, text = "Кто-то послал вам тайное послание:\n{0}".format(text))
    except (Unauthorized, BadRequest):
        bot.send_message(chat_id = mes.chat_id, text = "Невозможно доставить сообщение, возможно, получатель заблокировал бота. Напишите ему сами, не бегите от своего счастья!")
        return
    except TelegramError:
        bot.send_message(chat_id = mes.chat_id, text = "Ошибка при отправке. Вы можете попробовать ещё раз, или написать сами!")
        return
    bot.send_message(chat_id = mes.chat_id, text = "Сообщение успешно доставлено! Возможно, вам стоит написать самим, уже не таясь?")
    user_data.pop("status")
    user_data.pop("shipper_to_send")
    user_data.pop("shadow_letter_text")
    return

def shadow_letter_cancel(bot, update, user_data):
    pop_list = ["status", "shipper_to_send", "shadow_letter_text"]
    user_data_list = list(user_data)
    for item in pop_list:
        if item in user_data_list:
            user_data.pop(item)
    bot.send_message(chat_id = update.message.chat_id, text = "Успешно отменено!")


