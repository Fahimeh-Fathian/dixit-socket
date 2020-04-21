import json
import socket
import random
from _thread import *

from serializer import PlayerSerializer

server = ''
port = 5555
gamecode_game_dic = {}


class Player:
    id = 0
    in_hands_cards = []
    is_active_player = False
    is_connected = True
    description = ""
    current_card = 0
    name = ""
    color = ""
    score = ""
    is_game_creator = False

    def __init__(self, is_active_player, conn):
        self.is_active_player = is_active_player
        self.conn = conn

    def is_creator(self):
        self.is_game_creator = True

    def active_player(self):
        self.is_active_player = True

    def initial_cards(self,cards):
        self.in_hands_cards = cards

    def tell_story(self, description):
        if self.is_active_player:
            self.description = description

    def choose_card(self, card):
        self.current_card = card

    def add_card(self, card):
        self.in_hands_cards.append(card)

    def run_thread(self):
        while True:
            data = conn.recv(2048)
            reply = data.decode("utf-8")


class Game:
    all_cards = ['{}'.format(i) for i in range(20)]
    players = []
    number_of_players = 0
    all_steps = {
        'waiting_for_players': 0,
        'start_game': 1,
    }
    step_titles = {
        0: 'منتظر بازیکنان',
        1: 'شروع بازی'

    }
    colors = ['blue', 'red', 'yellow', 'green', 'black', 'pink']

    def __init__(self, code, number_of_players):
        self.game_code = code
        self.number_of_players = number_of_players
        self.step = self.all_steps['waiting_for_players']


    def add_player(self, player):
        if len(self.players) == 0:
            player.is_creator()
        random_color = random.choice(self.colors)
        self.colors.remove(random_color)
        player.color = random_color
        self.players.append(player)
        self.send_state()

    def start_game(self):
        self.step = self.all_steps['start_game']

    def run_game(conn):
        pass

    def send_state(self):

        state = {
            'players': PlayerSerializer(self.players, many=True).data,
            'step': self.step
        }
        print(state)

        json_state = json.dumps(state, separators=(',', ':'))
        for player in self.players:
            player.conn.sendall(str.encode(json_state))



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print("server error is ", e.strerror)

s.listen(3)
print("waiting for a connection, server started")


def threaded_client(conn):
    conn.send(str.encode("Connected"))
    data = conn.recv(2048)
    reply = data.decode("utf-8")
    print("reply is:", reply)

    print("reply 2 is:", reply)

    reply_list = reply.split(",")

    reply_dict = {}
    for item in reply_list:
        key = item.split(":")[0].strip()
        value = item.split(":")[1].strip()
        reply_dict[key] = value
    if "game_code" in reply_dict.keys():
        game_code = reply_dict["game_code"]
        print("game_code is ", game_code)
        if game_code not in gamecode_game_dic.keys():
            if "number_of_players" in reply_dict.keys():
                number_of_players = reply_dict["number_of_players"]
            else:
                print("you have to specify the number of players")
                print("lost connection")
                conn.close()
                return

            player = Player(is_active_player=True, conn=conn)
            start_new_thread(player.run_thread, (conn,))
            game = Game(code=reply_dict["game_code"], number_of_players=number_of_players)
            game.add_player(player)
            gamecode_game_dic[game_code] = game


        else:
            player = Player(is_active_player=False, conn=conn)
            start_new_thread(player.run_thread, (conn,))
            game = gamecode_game_dic[game_code]
            game.add_player(player)

        if game.number_of_players == len(game.players):
            game.start_game()
    else:
        print("you have to enter gamecode")
        print("lost connection")
        conn.close()
        return


def threaded_client2(conn):
    while True:
        conn.send(str.encode("Connected"))
        data = conn.recv(2048)
        reply = data.decode("utf-8")
        print(reply)
        # conn.sendall(str.encode("your reply is:\n"))


while True:
    print("AAA")
    conn, addr = s.accept()
    print("connected to ", addr)

    start_new_thread(threaded_client2, (conn,))
    # start_new_thread(threaded_client, (conn,))





