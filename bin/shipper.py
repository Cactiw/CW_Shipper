from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.error import BadRequest, Unauthorized, TelegramError
from work_materials.globals import castles, build_menu, classes_list, cursor, moscow_tz, admin_ids, castles_to_string
from libs.shipper_store import Shipper, Message

import datetime, logging, traceback, random

shippers = {}
shipper_messages_sent = {}

HOURS_BETWEEN_SHIPPER = 1


def fill_shippers():
    logging.info("Filling shippers...")
    shippers.clear()
    request = "select shipper_id, time_shippered, player.telegram_id, " \
        "player.telegram_username username, player.castle castle, player.game_class game_class, " \
        "shippered.telegram_id as shippered_telegram_id, shippered.telegram_username as shippered_telegram_username, " \
        "shippered.castle as shippered_castle, shippered.game_class as shippered_game_class, muted, force from shippers " \
        "inner join players player ON initiator_player_id = player.player_id " \
        "inner join players shippered on shippered_player_id = shippered.player_id"
    cursor.execute(request)
    row = cursor.fetchone()
    while row:
        current = Shipper(row[0], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[1], muted = row[10], force = row[11])
        print(row[0], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[1])
        shippers.update({row[0]: current})
        row = cursor.fetchone()
    logging.info("Shippers filled")


def fill_sent_messages():
    logging.info("Filling messages...")
    request = "select message_id, shipper_id, time_sent, answered from messages"
    cursor.execute(request)
    row = cursor.fetchone()
    while row:
        print(row[0], row[1], row[2], row[3])
        current = Message(row[0], row[1], row[2], answered=row[3])
        shipper_messages_sent.update({row[0] : current})
        row = cursor.fetchone()
    logging.info("Messages filled")


def shipper_force(bot, update, user_data):
    shipper(bot, update, user_data, force=True)


def shipper(bot, update, user_data, force=False):
    user_data.update({"shipper_force": force})
    if isinstance(update, int):
        chat_id = update
    else:
        chat_id = update.message.chat_id
    last_shipper_time = user_data.get("last_shipper_time")
    if not force and last_shipper_time is not None and \
            datetime.datetime.now(tz=moscow_tz).replace(tzinfo=None) - last_shipper_time < datetime.timedelta(hours=HOURS_BETWEEN_SHIPPER):
        response = "Время ещё не пришло. Должен пройти {0} час после предыдущей попытки.\n" \
                   "Осталось: {1}".format(HOURS_BETWEEN_SHIPPER, ":".join(str(datetime.timedelta(hours=HOURS_BETWEEN_SHIPPER) -(datetime.datetime.now(tz=moscow_tz).replace(tzinfo=None) - last_shipper_time)).partition(".")[0].split(":")[1:3]))
        if chat_id in admin_ids:
            response += "\nВы можете пропустить ожидание: /shipper_force"
        bot.send_message(chat_id=chat_id, text=response)
        return
    __castle_buttons = []
    for castle in castles:
        __castle_buttons.append(KeyboardButton(castle))
    reply_markup = ReplyKeyboardMarkup(build_menu(__castle_buttons, 4, footer_buttons=[KeyboardButton('Случайный замок')]), resize_keyboard=True)
    user_data.update({"status" : 'choosing castle'})
    bot.send_message(chat_id = chat_id, text = "Чувствуете ли вы в каком замке живет ваша любовь?",
                     reply_markup = reply_markup)


def shipper_selected_castle(bot, update, user_data):
    mes = update.message
    castle = mes.text if mes.text in castles else -1
    user_data.update({"search_castle": castle, "status" : "choosing class"})
    __class_buttons = []
    for curr_class in classes_list:
        __class_buttons.append(curr_class)
    reply_markup = ReplyKeyboardMarkup(build_menu(__class_buttons, 3, footer_buttons=[KeyboardButton('Случайный класс')]), resize_keyboard=True, one_time_keyboard=True)
    bot.send_message(chat_id = mes.chat_id, text = "Знаете ли вы, кем является ваша любовь?",
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
    request = "select telegram_username, times_shippered, player_id, castle, game_class, telegram_id from players where telegram_id != %s and shipper_enabled = TRUE "
    request += ("and castle = %s " if search_castle != -1 else "") + ("and game_class = %s " if search_class != -1 else "")
    if random.randint(0, 1):
        request += "order by times_shippered, last_shippered"
    else:
        request += "order by last_shippered, times_shippered"
    args = [update.message.from_user.id]
    if search_castle != -1:
        args.append(search_castle)
    if search_class != -1:
        args.append(search_class)
    cursor.execute(request, tuple(args))
    row = cursor.fetchone()
    not_found = False
    if row is None:
        not_found = True
        if search_castle != -1 and search_class != -1:
            request = "select telegram_username, times_shippered, player_id, castle, game_class, telegram_id from players where " \
                      "telegram_id != %s and (castle = %s or game_class = %s) and shipper_enabled = TRUE "
            if random.randint(0, 1):
                request += "order by times_shippered, last_shippered"
            else:
                request += "order by last_shippered, times_shippered"
            cursor.execute(request, (update.message.from_user.id, search_castle, search_class))
            row = cursor.fetchone()
        if row is None:
            request = "select telegram_username, times_shippered, player_id, castle, game_class, telegram_id from players where " \
                      "telegram_id != %s and shipper_enabled = TRUE "
            if random.randint(0, 1):
                request += "order by times_shippered, last_shippered"
            else:
                request += "order by last_shippered, times_shippered"
            cursor.execute(request, (update.message.from_user.id,))
            row = cursor.fetchone()
        if row is None:
            bot.send_message(chat_id = update.message.chat_id, text = "Любовь найти трудно, мы никого не нашли. Попробуй ещё раз: /shipper")
            return
    first_row = row
    while row:
        suitable = True
        for shipper in list(shippers.values()):
            if shipper.initiator.telegram_id == update.message.from_user.id and shipper.shippered.telegram_id == row[5]:
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
    force = user_data.get("shipper_force")
    if force is None:
        force = False
    if not force:
        request = "update players set times_shippered = %s, last_shippered = %s where player_id = %s"
        cursor.execute(request, (times_shippered, now, row[2]))
    request = "insert into shippers(initiator_player_id, shippered_player_id, time_shippered, force) VALUES (%s, %s, %s, %s) returning shipper_id"
    cursor.execute(request, (player_id, row[2], now, force))
    row_temp = cursor.fetchone()
    current = Shipper(row_temp[0], update.message.from_user.id, update.message.from_user.username, player_castle, player_game_class, row[5], row[0], row[3], row[4], now, force=force)
    shippers.update({row_temp[0] : current})
    if not not_found:
        response = "Смотри, кого мы нашли! <b>{2}</b> <b>{3}</b>\n@{0}\nПовторить попытку можно будет через {1} час: /shipper\n".format(row[0], HOURS_BETWEEN_SHIPPER, row[4], row[3] + castles_to_string.get(row[3]))
    else:
        response = "Любовь найти трудно, наиболее близким к запросу оказался <b>{2}</b> <b>{3}</b> \n@{0}\nПовторить попытку можно будет через {1} час: /shipper\n".format(row[0], HOURS_BETWEEN_SHIPPER, row[4], row[3] + castles_to_string.get(row[3]))
    bot.send_message(chat_id = update.message.chat_id, text = response, parse_mode = 'HTML', reply_markup = ReplyKeyboardRemove())
    user_data.update({"last_shipper_time" : now})
    shadow_letter(bot, update, user_data, shipper_id=row_temp[0])


def shadow_letter(bot, update, user_data, shipper_id = None):
    mes = update.message
    if shipper_id is None:
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
                     text = "Текст, который вы напишете далее будет анонимно отправлен @{0}.\n"
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
    if shipper.muted:
        bot.send_message(chat_id=mes.chat_id, text="Этот человек отключил сообщения от вас. Возможно, когда-нибудь, он включит их обратно.")
        user_data.pop("status")
        user_data.pop("shipper_to_send")
        user_data.pop("shadow_letter_text")
        return
    try:
        bot.send_message(chat_id = shipper.shippered.telegram_id,
                         text = "Кто-то послал вам тайное сообщение:\n{0}\n\n"
                                "Ответить (1 сообщение на каждое входящее): /reply_to_message_{1}\n"
                                "Вы можете отключить сообщения от этого человека: /mute_shipper_{1}".format(text, shipper.shipper_id))
    except (Unauthorized, BadRequest):
        bot.send_message(chat_id = mes.chat_id, text = "Невозможно доставить сообщение, возможно, получатель заблокировал бота. Напишите ему сами, не бегите от своего счастья!")
        return
    except TelegramError:
        bot.send_message(chat_id = mes.chat_id, text = "Ошибка при отправке. Вы можете попробовать ещё раз, или написать сами!")
        return
    now = datetime.datetime.now(tz = moscow_tz).replace(tzinfo=None)
    request = "insert into messages(shipper_id, time_sent) values (%s, %s) returning message_id"
    cursor.execute(request, (shipper.shipper_id, now))
    row_temp = cursor.fetchone()
    current_message = Message(row_temp[0], shipper.shipper_id, now)
    shipper_messages_sent.update({row_temp[0] : current_message})
    bot.send_message(chat_id = mes.chat_id, text = "Сообщение успешно доставлено! Возможно, вам стоит написать самим, уже не таясь?\n"
                                                   "Так же можно написать повторно: /shadow_letter_{0}".format(shipper.shipper_id))
    user_data.pop("status")
    user_data.pop("shipper_to_send")
    user_data.pop("shadow_letter_text")
    return


def shadow_letter_cancel(bot, update, user_data):
    shipper = user_data.get("shipper_to_send")
    pop_list = ["status", "shipper_to_send", "shadow_letter_text"]
    user_data_list = list(user_data)
    for item in pop_list:
        if item in user_data_list:
            user_data.pop(item)
    bot.send_message(chat_id = update.message.chat_id,
                     text = "Успешно отменено!\nВы можете написать ещё раз: /shadow_letter_{0}".format(shipper.shipper_id))


def reply_to_message(bot, update, user_data):
    mes = update.message
    try:
        shipper_id = int(mes.text.partition("@")[0].split("_")[3])
    except ValueError:
        bot.send_message(chat_id=mes.chat_id, text="Проверьте синтаксис и попробуйте ещё раз")
        return
    shipper = shippers.get(shipper_id)
    if shipper is None:
        bot.send_message(chat_id=mes.chat_id, text="Не найдено. Попробуйте ещё раз")
        return
    if shipper.shippered.telegram_id != mes.from_user.id:
        bot.send_message(chat_id=mes.chat_id, text="Не надо хитрить!")
        return
    message_exist = False
    messages_list = list(shipper_messages_sent.values())
    message_to_reply = None
    for message in messages_list:
        if message.shipper_id == shipper_id and message.answered == False:
            message_to_reply = message
            message_exist = True
            break
    if not message_exist:
        bot.send_message(chat_id=mes.chat_id, text="Не найдено, или вы уже ответили.")
        return
    user_data.update({"status": "awaiting_reply", "reply_to_send": shipper, "message_to_reply": message_to_reply})
    bot.send_message(chat_id=mes.chat_id,
                     text="Текст, который вы напишете далее будет отправлен обратно (уже не анонимно)."
                          "\nИспользуйте /cancel_reply для отмены.")


def reply_confirm(bot, update, user_data):
    mes = update.message
    if len(mes.text) > 1900:
        bot.send_message(chat_id=mes.chat_id, text="Размер сообщения ограничен 1900 символами!")
        return
    bot.send_message(chat_id=mes.chat_id, text="Следующий текст будет отправлен в ответ:\n{0}"
                                               "\n\nПодтвердить отправку: /confirm_reply"
                                               "\nОтменить отправку: /cancel_reply".format(mes.text))
    user_data.update({"reply_text": mes.text, "status": "awaiting_reply_confirmation"})


def reply_cancel(bot, update, user_data):
    pop_list = ["status", "reply_to_send", "reply_text"]
    user_data_list = list(user_data)
    for item in pop_list:
        if item in user_data_list:
            user_data.pop(item)
    bot.send_message(chat_id=update.message.chat_id, text="Успешно отменено!")


def reply_send(bot, update, user_data):
    mes = update.message
    text = user_data.get("reply_text")
    shipper = user_data.get("reply_to_send")
    message = user_data.get("message_to_reply")
    if message.answered:
        bot.send_message(chat_id=mes.chat_id,
                         text="Вы уже ответили на это сообщение. Подождите, пока вам напишут ещё!")
        user_data.pop("status")
        user_data.pop("reply_to_send")
        user_data.pop("reply_text")
        user_data.pop("message_to_reply")
        return
    try:
        bot.send_message(chat_id=shipper.initiator.telegram_id,
                         text="@{1} ответил вам на ваше сообщение:\n{0}\n\nВы всегда можете снова написать ему!: /shadow_letter_{2}".format(text, shipper.shippered.telegram_username, shipper.shipper_id))
    except (Unauthorized, BadRequest):
        bot.send_message(chat_id=mes.chat_id,
                         text="Невозможно доставить сообщение, возможно, получатель заблокировал бота. Грустно, если вы так и не узнали, кто это был(")
        return
    except TelegramError:
        bot.send_message(chat_id=mes.chat_id,
                         text="Ошибка при отправке. Вы можете попробовать ещё раз, или написать сами!")
        return
    now = datetime.datetime.now(tz=moscow_tz).replace(tzinfo=None)
    request = "update messages set answered = TRUE, time_answered = %s where shipper_id = %s"
    cursor.execute(request, (now, shipper.shipper_id,))
    message.answered = True
    bot.send_message(chat_id=mes.chat_id, text="Сообщение успешно доставлено!")
    user_data.pop("status")
    user_data.pop("reply_to_send")
    user_data.pop("reply_text")
    user_data.pop("message_to_reply")
    return


def shipper_mute(bot, update, user_data):
    mes = update.message
    try:
        shipper_id = int(mes.text.split('_')[2].partition("@")[0])
    except Exception:
        logging.error(traceback.format_exc())
        bot.send_message(chat_id = mes.chat_id, text = "Произошла ошибка. Проверьте синтаксис.")
        return
    shipper = shippers.get(shipper_id)
    if shipper is None or shipper.shippered.telegram_id != mes.from_user.id:
        bot.send_message(chat_id=mes.chat_id, text="Не найдено. Правильный номер поиска?")
        return
    if shipper.muted:
        bot.send_message(chat_id=mes.chat_id, text="Уже и так отключено.")
        return
    shipper.muted = True
    request = "update shippers set muted = TRUE where shipper_id = %s"
    cursor.execute(request, (shipper.shipper_id,))
    bot.send_message(chat_id = mes.chat_id, text = "Готово! Этот человек вас больше не побеспокоит\nВы можете отменить своё решение: /unmute_shipper_{0}".format(shipper_id))


def shipper_unmute(bot, update, user_data):
    mes = update.message
    try:
        shipper_id = int(mes.text.split('_')[2].partition("@")[0])
    except Exception:
        logging.error(traceback.format_exc())
        bot.send_message(chat_id=mes.chat_id, text="Произошла ошибка. Проверьте синтаксис.")
        return
    shipper = shippers.get(shipper_id)
    if shipper is None or shipper.shippered.telegram_id != mes.from_user.id:
        bot.send_message(chat_id=mes.chat_id, text="Не найдено. Правильный номер поиска?")
        return
    if not shipper.muted:
        bot.send_message(chat_id=mes.chat_id, text="Сообщения пока ещё включены!")
        return
    shipper.muted = False
    request = "update shippers set muted = FALSE where shipper_id = %s"
    cursor.execute(request, (shipper.shipper_id,))
    bot.send_message(chat_id=mes.chat_id, text="Готово! Вы снова можете получать сообщения от этого человека")


