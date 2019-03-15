from telegram import Bot
from config import ProductionToken
from work_materials.globals import admin_ids

bot = Bot(token=ProductionToken)
text = "У вас не установлено имя пользователя, поэтому часть функций бота будет для вас недоступна. Например, вас не смогут находить другие пользователи бота.\n" \
       "Вы можете использовать /delete_self до первого поиска, установить имя пользователя Telegram (откройте настройки Telegram -> username) и зарегистрироваться в боте заново (/start) для снятия ограничений."
message = bot.send_message(chat_id=admin_ids[0], text=text)
#message = bot.send_message(chat_id=78566615, text=text)
print("success, message =", message)