from work_materials.globals import dispatcher, psql_creditals
import logging, traceback, time, threading, psycopg2

def mass_send(text):
    conn = psycopg2.connect("dbname={0} user={1} password={2}".format(psql_creditals['dbname'], psql_creditals['user'],
                                                                      psql_creditals['pass']))
    conn.set_session(autocommit=True)
    cursor = conn.cursor()
    text = "Время искать свои половинки!\n/shipper"
    request = "select telegram_id from players limit 2"
    cursor.execute(request)
    row = cursor.fetchone()
    i = 0
    while row:
        try:
            dispatcher.bot.send_message(chat_id=row[0], text = text)
        except Exception:
            logging.warning("Error in sending message, telegram_id ={}\n{}".format(row[0], traceback.format_exc().splitlines()[-1]))
        else:
            i += 1
            print("sent {} message, chat_id = {}".format(i, row[0]))
        time.sleep(0.1)
        row = cursor.fetchone()
    cursor.close()

def mass_send_start(bot, update):
    threading.Thread(target=mass_send, args = ("",)).start()
    bot.send_message(chat_id = update.message_chat_id, text = "Начата рассылка...")
