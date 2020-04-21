from aiohttp import web
import socketio
import json

from models import Player, Game

sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)
gamecode_game_dic = {}
sid_gamecode = {}

async def index(request):
    """Serve the client-side application."""
    # print("header is:", request)
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

@sio.event
def connect(sid, environ):
    print("gamecode_game_dic is:",gamecode_game_dic)
    print("connect ", sid)
    # print("environ is: ", environ)

@sio.event
async def create_game(sid, data):
    if "game_code" not in data.keys() or "number_of_players" not in data.keys() or\
            "user_id" not in data.keys() or 'username' not in data.keys():
        print("lost connection")
        raise ConnectionRefusedError('incorrect inputs')
    username = data['username']
    game_code = data['game_code']

    sid_gamecode[sid] = game_code
    sio.enter_room(sid, game_code)

    user_id = data['user_id']
    if game_code not in gamecode_game_dic.keys():

        player = Player(sid=sid, id=user_id, name=username)
        player.is_creator()
        number_of_players = int(data["number_of_players"])
        game = Game(code=game_code, number_of_players=number_of_players)
        game.add_player(player)
        gamecode_game_dic[game_code] = game
    else:
        print("there is a game with this code")
        raise ConnectionRefusedError('there is a game with this code')
    state = game.get_state()
    await sio.emit('get_state', state, room=game_code)


@sio.event
async def join_game(sid, data):
    print("data is:", data)
    if "game_code" not in data.keys() or \
            "user_id" not in data.keys() or 'username' not in data.keys():
        print("lost connection")
        raise ConnectionRefusedError('incorrect inputs')

    username = data['username']
    game_code = data['game_code']

    sid_gamecode[sid] = game_code
    sio.enter_room(sid, game_code)

    user_id = data['user_id']

    if game_code not in gamecode_game_dic.keys():
        raise ConnectionRefusedError('game not exist.')

    else:
        game = gamecode_game_dic[game_code]
        user_is_in_game = False
        for player in game.players:
            if player.id == user_id:
                # if player.is_connected == True:
                #     raise ConnectionRefusedError('you are currently in game.')
                # else:
                user_is_in_game = True
                sio.leave_room(player.sid, game_code)
                player.sid = sid
                player.is_connected = True
                break

        if not user_is_in_game:
            player = Player(sid=sid, id=user_id, name=username)
            player.name = username
            game.add_player(player)

    if game.step == 0 and game.number_of_players == len(game.players):
        game.start_game()

    state = game.get_state()
    await sio.emit('get_state', state, room=game_code)


@sio.event
async def tell_story(sid, data):
    print("data is:", data)
    if "game_code" not in data.keys() or "user_id" not in data.keys() \
            or "story" not in data.keys()or "story_card" not in data.keys():
        print("lost connection")
        raise ConnectionRefusedError('incorrect inputs')
    story = data['story']
    story_card = data['story_card']
    game_code = data['game_code']
    user_id = data['user_id']
    game = gamecode_game_dic[game_code]
    if game.step == 1 and game.active_player.id == user_id:
        game.tell_story(story, story_card)
        state = game.get_state()
        await sio.emit('get_state', state, room=game_code)

    else:
        raise ConnectionRefusedError('you can not tell the story')


@sio.event
async def send_close_card(sid, data):

    print("data is:", data)
    if "game_code" not in data.keys() or "user_id" not in data.keys()\
            or "close_card" not in data.keys():
        print("lost connection")
        raise ConnectionRefusedError('incorrect inputs')

    close_card = data['close_card']

    game_code = data['game_code']
    user_id = data['user_id']
    game = gamecode_game_dic[game_code]
    if game.number_of_players == 3 and len(close_card) != 2:
        raise ConnectionRefusedError('incorrect inputs')
    if game.step == 2:
        game.send_close_card(user_id, close_card)
    if game.step == 3 and len(game.closest_cards) == game.number_of_players:
        state = game.get_state()
        await sio.emit('get_state', state, room=game_code)


@sio.event
async def send_vote(sid, data):
    print("data is:", data)
    if "game_code" not in data.keys() or "user_id" not in data.keys() \
            or "vote_card" not in data.keys():
        raise ConnectionRefusedError('incorrect inputs')

    vote_card = data['vote_card']
    game_code = data['game_code']
    user_id = data['user_id']
    game = gamecode_game_dic[game_code]
    if game.step == game.all_steps['waiting_for_votes']:
        no_error, error_message = game.send_vote(user_id, vote_card)
        if not no_error:
            raise ConnectionRefusedError(error_message)
        else:
            state = game.get_state()
            await sio.emit('get_state', state, room=game_code)

@sio.event
async def next_round(sid, data):
    print("data is:", data)
    if "game_code" not in data.keys():
        raise ConnectionRefusedError('incorrect inputs')
    game_code = data['game_code']
    game = gamecode_game_dic[game_code]

    if game.step == game.all_steps['show_result']:
        game.next_round()
        state = game.get_state()
        await sio.emit('get_state', state, room=game_code)


# @sio.event
# async def delete_game(sid, data):
#     if "game_code" not in data.keys():
#         print("lost connection")
#         raise ConnectionRefusedError('incorrect inputs')
#     game_code = data['game_code']
#     game = gamecode_game_dic[game_code]
@sio.event
async def chat(sid, data):
    if "game_code" not in data.keys() or "user_id" not in data.keys() \
            or "message" not in data.keys():
        raise ConnectionRefusedError('incorrect inputs')
    message = data['message']
    game_code = data['game_code']
    user_id = data['user_id']
    game = gamecode_game_dic[game_code]
    if user_id in game.players_dic.keys():
        game.send_message(user_id, message)
        state = game.get_state()
        await sio.emit('get_state', state, room=game_code)


@sio.event
async def lobby(sid):
    lobby = get_lobby()
    await sio.emit('lobby', lobby, room=sid)


def get_lobby():
    lobby = []
    for game_code in gamecode_game_dic.keys():
        game = gamecode_game_dic[game_code]
        if game.step == game.all_steps['waiting_for_players']:
            lobby.append(
                {
                    'game_code': game.game_code,
                    'number_of_players': game.number_of_players,
                    'joined_players': len(game.players)
                }
            )
    return lobby

@sio.event
async def disconnect(sid):
    if sid in sid_gamecode.keys():
        game_code = sid_gamecode[sid]
        game = gamecode_game_dic[game_code]
        for player in game.players:
            if player.sid == sid:
                player.is_connected = False
                sio.leave_room(player.sid, game_code)
        del sid_gamecode[sid]
        state = game.get_state()

        await sio.emit('get_state', state, room=game_code)
    print('disconnect ', sid)

    # state = game.get_state()
    # await sio.emit('get_state', state, room=game_code)

app.router.add_static('/static', 'static')
app.router.add_get('/', index)

if __name__ == '__main__':
    web.run_app(app)