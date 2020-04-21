import asyncio
import time
import socketio

loop = asyncio.get_event_loop()
sio = socketio.AsyncClient()
start_timer = None


async def create_game():

    await sio.emit('create_game', {
        "game_code":"game_code1",
        "number_of_players":3,
        "username":"fahime",
        "user_id":1,
        "list":[5,6]
    })


async def join_game():

    await sio.emit('join_game', {
        "game_code":"aasdfasf",
        "number_of_players":3,
        "username":"ali",
        "user_id":12
    })


@sio.event
async def connect():
    print('connected to server')
    await create_game()


@sio.event
async def get_state(data):
    print("from server",data)


async def start_server():
    await sio.connect('http://213.233.180.121:8080')
    # await sio.connect('http://localhost:8080')
    await sio.wait()


if __name__ == '__main__':
    loop.run_until_complete(start_server())

