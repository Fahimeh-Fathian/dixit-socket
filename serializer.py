class PlayerSerializer:

    def __init__(self, players, many):
        self.players = players
        self.many = many
        self.data = self.get_data()

    def get_data(self):
        if self.many:
            data = []
            for player in self.players:
                data.append(self.serialize(player))
        else:
            data = self.serialize(self.players)
        return data

    def serialize(self, player):
        data = {
            'id': player.id,
            'name': player.name,
            'color': player.color,
            'score': player.score,
            'is_connected': player.is_connected,
            'game_creator': player.is_game_creator,
            'in_hand_cards': player.in_hands_cards
        }
        return data