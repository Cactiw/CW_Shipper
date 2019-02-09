

class Shipper:

    def __init__(self, shipper_id, initiator_telegram_id, initiator_telegram_username, initiator_castle, initiator_game_class,
                 shippered_telegram_id, shippered_telegram_username, shippered_castle, shippered_game_class, time_shippered):
        self.shipper_id = shipper_id
        self.initiator = Player(initiator_telegram_id, initiator_telegram_username, initiator_castle, initiator_game_class)
        self.shippered = Player(shippered_telegram_id, shippered_telegram_username, shippered_castle, shippered_game_class)
        self.time_shippered = time_shippered


class Player:

    def __init__(self, telegram_id, telegram_username, castle, game_class):
        self.telegram_id = telegram_id
        self.telegram_username = telegram_username
        self.castle = castle
        self.game_class = game_class
