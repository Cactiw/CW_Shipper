from telegram.error import BadRequest, TelegramError, Unauthorized
import logging, traceback

from work_materials.globals import castles as castles_const, classes_list as classes_const, cursor
from libs.start_pult import rebuild_pult


def pult_callback(bot, update, user_data):
    data = update.callback_query.data
    if data.find("pc") == 0:
        pult_castles_callback(bot, update, user_data)
        return
    if data.find("pk") == 0:
        pult_classes_callback(bot, update, user_data)
        return
    if data.find("pok") == 0:
        pult_ok_callback(bot, update, user_data)
        return


def pult_castles_callback(bot, update, user_data):
    mes = update.callback_query.message
    new_target = int(update.callback_query.data[2:])
    new_markup = rebuild_pult("change_target", new_target, user_data)
    pult_status = user_data.get('start_pult_status')
    pult_status.update({ "castle" : new_target })
    print(user_data.get('start_pult_status'))
    edit_pult(bot = bot, chat_id=mes.chat_id, message_id=mes.message_id, reply_markup=new_markup, callback_query_id=update.callback_query.id)

def pult_classes_callback(bot, update, user_data):
    mes = update.callback_query.message
    new_class = int(update.callback_query.data[2:])
    new_markup = rebuild_pult("change_class", new_class, user_data)
    pult_status = user_data.get('start_pult_status')
    pult_status.update({ "class" : new_class})
    print(user_data.get('start_pult_status'))
    edit_pult(bot = bot, chat_id=mes.chat_id, message_id=mes.message_id, reply_markup=new_markup, callback_query_id=update.callback_query.id)

def pult_ok_callback(bot, update, user_data):
    mes = update.callback_query.message
    pult_status = user_data.get('start_pult_status')
    pult_castle = pult_status.get('castle')
    pult_class = pult_status.get('class')
    castle = castles_const[pult_castle]
    game_class = classes_const[pult_class]
    user_data.pop('start_pult_status')
    user_data.pop('castles')
    user_data.pop('classes')
    user_data.update({'castle' : castle, 'class' : game_class})
    try:
        bot.deleteMessage(chat_id=update.callback_query.from_user.id, message_id=mes.message_id)
    except Unauthorized:
        pass
    except BadRequest:
        pass
    castles_to_string = {'🍆': 'Фермы', '🍁': 'Амбера', '☘': 'Оплота', '🌹': 'Розы', '🐢': 'Тортуги',
                         '🦇': 'Замка ночи', '🖤': 'Скалы'}
    castle_print = castles_to_string.get(castle)
    bot.send_message(chat_id = mes.chat_id,
                     text = 'Регистрация успешна, <b>{0}</b> <b>{1}{2}</b>'.format(game_class, castle, castle_print),
                     parse_mode = 'HTML')
    request = "insert into players(castle, game_class) values (%s, %s)"
    cursor.execute(request, (castle, game_class))
    print(user_data)


def edit_pult(bot, chat_id, message_id, reply_markup, callback_query_id):
    try:
        bot.editMessageReplyMarkup(chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)
    except BadRequest:
        pass
    except TelegramError:
        logging.error(traceback.format_exc())
    finally:
        bot.answerCallbackQuery(callback_query_id=callback_query_id)

