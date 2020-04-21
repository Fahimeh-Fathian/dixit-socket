import socket
from _thread import *

server = "192.168.1.106"
port = 5555
gamecode_game_dic = {}


class game:
    all_cards = ['{}'.format(i) for i in range(20)]
    players = []


    def __init__(self, players, code):
        self.players = players
        self.gamecode = code

    def main(self):
        while True:
            conn, addr = s.accept()
            print("connected to ", addr)
            start_new_thread(self.threaded_client, (conn,))

    def threaded_client(conn):
        print("JAJA")
        conn.send(str.encode("Connected"))
        reply = ""

        while True:
            try:
                data = conn.recv(2048)
                reply = data.decode("utf-8")
                if not data:
                    print("Disconnected")
                    break
                else:
                    print("recieved data: ", data)
                    print("sending data: ", data)
                conn.sendall(str.encode(reply))
            except:
                break
        print("lost connection")
        conn.close()



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print("server error is ", e.strerror)

s.listen(3)
print("waiting for a connection, server started")










