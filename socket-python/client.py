from network import Network

class Player:
    in_hands_cards = []
    is_active_player = False
    description = ""
    current_card = 0

    def __init__(self, cards, is_active_player):
        self.in_hands_cards = cards
        self.is_active_player = is_active_player

    def active_player(self):
        self.is_active_player = True

    def tell_story(self, description):
        if self.is_active_player:
            self.description = description

    def choose_card(self, card):
        self.current_card = card

    def add_card(self, card):
        self.in_hands_cards.append(card)


def main():
    win = True

    while win:
        input_string = input().split(",")
        if input_string[0] == "end":
            win = False
        elif input_string[0] == "player_turn":

            print("player is active")
        elif input_string[0] == "add_desc":
            print("asfdasdf")
        elif input_string[0] == "choose_card":
            print("player chooses a card")

main()