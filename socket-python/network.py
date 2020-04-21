import socket

import client_joingame


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
class Network:
    def __init__(self):
        print("Here")
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "213.233.180.121"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.pos = self.connect()


    def getPos(self):
        return self.pos

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode("utf-8")
        except:
            pass
    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return self.client.recv(2048).decode("utf-8")
        except socket.error as e:
            print("error is: ", e)

n = Network()
n.send("game_code:1021,number_of_players:3")

