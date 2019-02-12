

class Shipper:

    def __init__(self, shipper_id, initiator_telegram_id, initiator_telegram_username, initiator_castle, initiator_game_class,
                 shippered_telegram_id, shippered_telegram_username, shippered_castle, shippered_game_class, time_shippered, muted = False, force = False):
        self.shipper_id = shipper_id
        self.initiator = Player(initiator_telegram_id, initiator_telegram_username, initiator_castle, initiator_game_class)
        self.shippered = Player(shippered_telegram_id, shippered_telegram_username, shippered_castle, shippered_game_class)
        self.time_shippered = time_shippered
        self.muted = muted
        self.force = force


class Player:

    def __init__(self, telegram_id, telegram_username, castle, game_class):
        self.telegram_id = telegram_id
        self.telegram_username = telegram_username
        self.castle = castle
        self.game_class = game_class


class Message:

    def __init__(self, message_id, shipper_id, time_send, answered = False):
        self.message_id = message_id
        self.shipper_id = shipper_id
        self.time_send = time_send
        self.answered = answered
