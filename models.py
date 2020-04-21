import random
from serializer import PlayerSerializer

gamecode_game_dic = {}


class Player:

    def __init__(self, sid, id, name):
        self.sid = sid
        self.id = id
        self.in_hands_cards = []
        self.is_active_player = False
        self.is_connected = True
        self.current_card = 0
        self.name = name
        self.color = ""
        self.score = 0
        self.is_game_creator = False

    def is_creator(self):
        self.is_game_creator = True

    def add_score(self, added_score):
        self.score += added_score

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


class Game:
    messages = []
    all_steps = {
        'waiting_for_players': 0,
        'waiting_for_story': 1,
        'waiting_for_closest_cards': 2,
        'waiting_for_votes': 3,
        'show_result': 4,
        'end': 5
    }
    step_titles = {
        0: 'منتظر بازیکنان',
        1: 'منتظر قصه',
        2: 'منتظر کارت‌های نزدیک به قصه',
        3: 'منتظر رای‌ها',
    }

    def __init__(self, code, number_of_players):
        self.all_cards = ['{}'.format(i) for i in range(100)]
        self.colors = ['av1', 'av2', 'av3', 'av4', 'av5', 'av6']
        self.closest_cards = {}
        self.votes = {}
        self.players = []
        self.active_player_index = 0
        self.active_player = None
        self.story = ""
        self.players_cards_count = 6
        self.game_code = code
        self.number_of_players = number_of_players
        self.step = self.all_steps['waiting_for_players']
        self.players_dic = {}

    def add_player(self, player):
        if len(self.players) < self.number_of_players:
            self.players.append(player)

    def start_game(self):
        if self.step != self.all_steps['waiting_for_players']:
            return
        for player in self.players:
            self.players_dic[player.id] = player
        for player in self.players:
            random_color = random.choice(self.colors)
            self.colors.remove(random_color)
            player.color = random_color

            player.is_active_player = False
            if self.number_of_players == 3:
                self.players_cards_count = 7
            for i in range(self.players_cards_count):
                random_card = random.choice(self.all_cards)
                self.all_cards.remove(random_card)
                player.add_card(random_card)
        self.colors = ['av1', 'av2', 'av3', 'av4', 'av5', 'av6']
        random_player_index = random.randint(0, self.number_of_players-1)
        print("number of players", self.number_of_players)
        print("random index", random_player_index)
        # random_player_index = self.number_of_players - 1
        self.active_player_index = random_player_index
        self.players[self.active_player_index].is_active_player = True
        self.active_player = self.players[self.active_player_index]
        self.step = self.all_steps['waiting_for_story']

    def tell_story(self, story, story_card):
        self.story = story
        self.closest_cards[self.active_player.id] = [story_card]
        self.step = self.all_steps['waiting_for_closest_cards']

    def send_close_card(self, user_id, close_cards):
        for i in range(len(close_cards)):
            close_cards[i] = close_cards[i]
        self.closest_cards[user_id] = close_cards
        if self.step == 2 and len(self.closest_cards) == self.number_of_players:
                self.waiting_for_votes()

    def waiting_for_votes(self):
        self.step = self.all_steps['waiting_for_votes']

    def send_vote(self, user_id, vote_card):
        if vote_card in self.closest_cards[user_id]:
            return False, "you cant vote to your own card"
        if user_id == self.active_player.id:
            return False, "you are active player you can't vote"
        if user_id in self.votes.keys():
            return False, "you have voted before"
        self.votes[user_id] = vote_card
        print(len(self.votes), "################",self.number_of_players)
        if len(self.votes) == self.number_of_players - 1:
            self.change_result()

            self.step = self.all_steps['show_result']
        return True, "OK"

    def change_result(self):
        active_user_card = self.closest_cards[self.active_player.id][0]
        true_vote_count = 0
        added_score = {}
        for player in self.players:
            added_score[player.id] = 0

        for user_id in self.votes.keys():
            user_card = self.votes[user_id]
            if user_card == active_user_card:
                added_score[user_id] += 3
                true_vote_count += 1
            else:
                for item in self.closest_cards.keys():
                    if user_card in self.closest_cards[item]:
                        added_score[item] += 1
                        break

        if true_vote_count == 0 or true_vote_count == self.number_of_players:
            for player in self.players:
                if player is not self.active_player:
                    added_score[player.id] += 2
        else:
            added_score[self.active_player.id] += 3

        for player in self.players:
            player.add_score(added_score[player.id])

    def next_round(self):
        for player in self.players:
            if player.score >= 30:
                self.end_game()
                return
        for user_id in self.closest_cards.keys():
            player = self.players_dic[user_id]
            for card in self.closest_cards[user_id]:
                player.in_hands_cards.remove(card)
                if len(self.all_cards) == 0:
                    print("all cards used")
                else:
                    random_card = random.choice(self.all_cards)
                    self.all_cards.remove(random_card)
                    player.add_card(random_card)

        self.colors = ['av1', 'av2', 'av3', 'av4', 'av5', 'av6']
        self.closest_cards = {}
        self.votes = {}
        self.active_player_index = (self.active_player_index + 1) % self.number_of_players
        self.active_player = self.players[self.active_player_index]
        self.story = ""
        self.step = self.all_steps['waiting_for_story']

    def end_game(self):
        self.step = self.all_steps['end']

    def send_message(self, user_id, message):
        message_object = {'user_id': int(user_id),
                          'message': message
                          }
        self.messages.append(message_object)

    def get_state(self):
        closest_cards = []
        for user_id in self.closest_cards.keys():
            for card in self.closest_cards[user_id]:
                closest_cards.append({
                    'user_id': user_id,
                    'card': card,
                    'color': self.players_dic[user_id].color

                })
        state = {
            'players': PlayerSerializer(self.players, many=True).data,
            'step': self.step,
            'story': self.story,
            'number_of_players': self.number_of_players,
            'closest_cards': closest_cards,
            'votes': self.votes,
            'messages': self.messages

        }
        if self.active_player is not None:
            state['active_user_id'] = self.active_player.id
        print(state)
        return state

import json

game1 = Game("Game 1", 3)
player1 = Player("sid",1, "fahime")
game1.add_player(player1)
print("players of game1 is: ",game1.players)

player2 = Player("SDds23323df",5,"ali")
game1.add_player(player2)

player3 = Player("SDds23323df",6,"famali")
game1.add_player(player3)

game1.start_game()

game1.get_state()




