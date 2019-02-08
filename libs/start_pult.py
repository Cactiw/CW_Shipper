from work_materials.globals import castles as castles_const, classes_list as classes_const
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def build_pult(castles, classes):
    __pult_buttons = [
        [
            InlineKeyboardButton(castles[0], callback_data="pc0"),
            InlineKeyboardButton(castles[1], callback_data="pc1"),
            InlineKeyboardButton(castles[2], callback_data="pc2"),
            InlineKeyboardButton(castles[3], callback_data="pc3"),
        ],
        [
            InlineKeyboardButton(castles[4], callback_data="pc4"),
            InlineKeyboardButton(castles[5], callback_data="pc5"),
            InlineKeyboardButton(castles[6], callback_data="pc6"),
        ],
        [
            InlineKeyboardButton(classes[0], callback_data="pk0"),
            InlineKeyboardButton(classes[1], callback_data="pk1"),
            InlineKeyboardButton(classes[2], callback_data="pk2"),
        ],
        [
            InlineKeyboardButton(classes[3], callback_data="pk3"),
            InlineKeyboardButton(classes[4], callback_data="pk4"),
            InlineKeyboardButton(classes[5], callback_data="pk5"),
        ],
        [
            InlineKeyboardButton("🆗 Подтвердить", callback_data="pok"),
        ],
    ]
    PultMarkup = InlineKeyboardMarkup(__pult_buttons)
    return PultMarkup

def rebuild_pult(action, context, user_data):
    if action == "default":
        castles = castles_const
        classes = classes_const
        new_markup = build_pult(castles, classes)
        return new_markup
    if action == "change_target":
        castles = user_data.get("castles")
        classes = user_data.get('classes')
        for i in range(0, len(castles)):
            castles[i] = castles_const[i]
        castles[context] = '✅' + castles[context]
        print(user_data.get('castles'))
        new_markup = build_pult(castles, classes)
        return new_markup
    if action == "change_class":
        castles = user_data.get("castles")
        classes = user_data.get('classes')
        for i in range(0, len(classes)):
            classes[i] = classes_const[i]
        classes[context] = '✅' + classes[context]
        print(user_data.get('classes'))
        new_markup = build_pult(castles, classes)
        return new_markup
