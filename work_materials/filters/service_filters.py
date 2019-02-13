from telegram.ext import BaseFilter
from work_materials.globals import admin_ids, moscow_tz, dispatcher
import datetime


class FilterIsAdmin(BaseFilter):
    def filter(self, message):
        return message.from_user.id in admin_ids

filter_is_admin = FilterIsAdmin()


class FilterDeleteYourself(BaseFilter):
    def filter(self, message):
        user_data = dispatcher.user_data.get(message.from_user.id)
        return user_data is None or user_data.get("last_shipper_time") is None

filter_delete_yourself = FilterDeleteYourself()


class FilterOnlyRegistation(BaseFilter):
    def filter(self, message):
        return datetime.datetime.now(tz=moscow_tz).replace(tzinfo=None) < datetime.datetime(year=2019, month=2, day=14)


filter_only_registration = FilterOnlyRegistation()
