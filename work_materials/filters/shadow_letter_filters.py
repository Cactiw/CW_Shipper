from telegram.ext import BaseFilter
from work_materials.globals import dispatcher

class FilterShadowLetter(BaseFilter):
    def filter(self, message):
        print(message.text.find("/shadow_letter_"))
        return message.text.find("/shadow_letter_") == 0

filter_shadow_letter= FilterShadowLetter()


class FilterAwaitingShadowLetter(BaseFilter):
    def filter(self, message):
        user_data = dispatcher.user_data.get(message.from_user.id)
        return user_data and user_data.get("status") == "awaiting_shadow_letter"

filter_awaiting_shadow_letter= FilterAwaitingShadowLetter()


class FilterShadowLetterConfirm(BaseFilter):
    def filter(self, message):
        user_data = dispatcher.user_data.get(message.from_user.id)
        return message.text == "/confirm_shadow_letter" and user_data and user_data.get("status") == "awaiting_letter_confirmation"

filter_confirm_shadow_letter= FilterShadowLetterConfirm()


class FilterShadowLetterCancel(BaseFilter):
    def filter(self, message):
        user_data = dispatcher.user_data.get(message.from_user.id)
        return message.text == "/cancel_shadow_letter" and user_data and user_data.get("status") == "awaiting_letter_confirmation"

filter_cancel_shadow_letter= FilterShadowLetterCancel()