#!/usr/bin/env python3

import json
import socket
import os
from threading import Thread
from time import sleep


def create_fifo(path):
    "Create FIFO file by path."
    if os.path.exists(path):
        os.unlink(path)
    if not os.path.exists(path):
        os.mkfifo(path)


def write(s):
    "Write s into output FIFO."
    with open(cfg["irc"]["out"], "w") as write_fifo:
        write_fifo.write(s + "\n")


def split_text(msg, size):
    for i in range(0, len(l), size):
        yield l[i:i+size]


class Bot():

    def __init__(self, host, port, nick, channel):
        self.host = host
        self.port = port
        self.nick = nick
        self.channel = channel

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))
        self.s.send('USER {0} gate gate {0}\r\n'.format(self.nick).encode())
        self.s.send('NICK {}\r\n'.format(self.nick).encode())
        self.s.send('JOIN {}\r\n'.format(self.channel).encode())

    def run(self):
        while True:
            data = self.s.recv(4096).decode('utf-8')
            if 'PING' in data:
                self.s.send('PONG {}\r\n'.format(data.split(':')[1]).encode())
            if "PRIVMSG {}".format(self.channel) in data:
                body = ":".join(data.split(":")[2:])
                nick = data.split(":")[1].split("!")[0]
                if body.startswith("/me "):
                    write("**{} {}**".format(nick, body[4:]))
                else:
                    write("<{}> {}".format(nick, body))

    def send(self, message):
        self.s.send('PRIVMSG {} :{}\r\n'.format(self.channel, message).encode())


class ListenerThread(Thread):
    "Input FIFO listener."
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name

    def run(self):
        sleep(5)
        while True:
            with open(cfg["irc"]["in"], "r") as fifo_read:
                msg = fifo_read.read().strip()
                if len(msg) > cfg["irc"]["msg_size"]:
                    for msg in split_text(msg, cfg["irc"]["msg_size"]):
                        irc.send(msg)
                else:
                    irc.send(msg)
            sleep(.5)


cfg = json.loads(open("config.json").read())
create_fifo(cfg["irc"]["out"])
create_fifo(cfg["irc"]["in"])
irc = Bot(cfg["irc"]["host"], cfg["irc"]["port"], cfg["irc"]["nickname"],
          cfg["irc"]["channel"])
irc.connect()
listener_thread = ListenerThread("IRC fifo listener")
listener_thread.start()
irc.run()
