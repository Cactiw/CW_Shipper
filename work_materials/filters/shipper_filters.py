from telegram.ext import BaseFilter
from work_materials.globals import castles, classes_list, dispatcher

class FilterShipperCastle(BaseFilter):
    def filter(self, message):
        try:
            return (message.text in castles or message.text == 'Случайный замок') and dispatcher.user_data.get(message.from_user.id).get('status') == 'choosing castle'
        except TypeError:
            return False

filter_shipper_castle= FilterShipperCastle()