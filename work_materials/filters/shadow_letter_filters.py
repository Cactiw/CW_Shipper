from telegram.ext import BaseFilter
from work_materials.globals import dispatcher

class FilterShadowLetter(BaseFilter):
    def filter(self, message):
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
        return message.text == "/cancel_shadow_letter" and user_data and \
               (user_data.get("status") == "awaiting_letter_confirmation"
                or user_data.get("status") == "awaiting_shadow_letter")

filter_cancel_shadow_letter= FilterShadowLetterCancel()


class FilterReplyToMessage(BaseFilter):
    def filter(self, message):
        return message.text.find("/reply_to_message_") == 0

filter_reply_to_message= FilterReplyToMessage()


class FilterAwaitingReply(BaseFilter):
    def filter(self, message):
        user_data = dispatcher.user_data.get(message.from_user.id)
        return user_data and user_data.get("status") == "awaiting_reply"

filter_awaiting_reply= FilterAwaitingReply()


class FilterReplyConfirm(BaseFilter):
    def filter(self, message):
        user_data = dispatcher.user_data.get(message.from_user.id)
        return message.text == "/confirm_reply" and user_data and user_data.get("status") == "awaiting_reply_confirmation"

filter_confirm_reply= FilterReplyConfirm()


class FilterReplyCancel(BaseFilter):
    def filter(self, message):
        user_data = dispatcher.user_data.get(message.from_user.id)
        return message.text == "/cancel_reply" and user_data and \
               (user_data.get("status") == "awaiting_reply"
                or user_data.get("status") == "awaiting_reply_confirmation")

filter_cancel_reply= FilterReplyCancel()