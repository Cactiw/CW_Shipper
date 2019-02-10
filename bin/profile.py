from work_materials.globals import cursor, castles_to_string

def profile(bot, update, user_data):
    mes = update.message
    request = "select telegram_username, times_shippered, player_id, castle, game_class, " \
              "telegram_id, last_time_shipper_used from players where telegram_id = %s"
    cursor.execute(request, (mes.from_user.id,))
    row = cursor.fetchone()
    if row is None:
        bot.send_message(chat_id = mes.chat_id, text = "Вы не зарегистрированы! Используйте /start")
        return
    response = "<b>{0}</b> --- <b>{1}</b> <b>{2}</b>\nПоследний поиск: {3}\n\n".format(row[0], row[4], row[3] + castles_to_string.get(row[3]), row[6])
    response += "История поиска: /shipper_history"
    bot.send_message(chat_id = mes.chat_id, text = response, parse_mode = 'HTML')
