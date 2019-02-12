from work_materials.globals import cursor, castles_to_string
from bin.shipper import shippers

def profile(bot, update, user_data):
    mes = update.message
    request = "select telegram_username, times_shippered, player_id, castle, game_class, " \
              "telegram_id, last_time_shipper_used from players where telegram_id = %s"
    cursor.execute(request, (mes.from_user.id,))
    row = cursor.fetchone()
    if row is None:
        bot.send_message(chat_id = mes.chat_id, text = "Вы не зарегистрированы! Используйте /start")
        return
    last_time_shipper_used = user_data.get("last_shipper_time")
    response = "<b>{0}</b> --- <b>{1}</b> <b>{2}</b>\nПоследний поиск: {3}\n\n".format(row[0], row[4], row[3] + castles_to_string.get(row[3]), last_time_shipper_used.strftime("%D :: %H:%M"))
    response += "История поиска: /shipper_history"
    bot.send_message(chat_id = mes.chat_id, text = response, parse_mode = 'HTML')


def shipper_history(bot, update, user_data):
    response = "История поиска:\n"
    shippers_list = list(shippers.values())
    for shipper in shippers_list:
        if shipper.initiator.telegram_id == update.message.from_user.id:
            response += "@{0} <b>{1}</b> <b>{2}</b> ---- {3}\nОтправить тайное послание: /shadow_letter_{4}\n\n".format(shipper.shippered.telegram_username,
                                                                    shipper.shippered.game_class, shipper.shippered.castle + castles_to_string.get(shipper.shippered.castle),
                                                                    shipper.time_shippered.strftime("%D :: %H:%M"), shipper.shipper_id)
    bot.send_message(chat_id = update.message.chat_id, text = response, parse_mode = 'HTML')
