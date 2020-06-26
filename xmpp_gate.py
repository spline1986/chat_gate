#!/usr/bin/env python3

import json
import os
import sleekxmpp
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
    with open(cfg["xmpp"]["out"], "w") as write_fifo:
        write_fifo.write(s + "\n")


class Bot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password, room, nick):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.room = room
        self.nick = nick
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("groupchat_message", self.muc_message)

    def start(self, event):
        self.get_roster()
        self.send_presence()
        self.plugin["xep_0045"].joinMUC(self.room, self.nick, wait=True)

    def muc_message(self, msg):
        if msg["mucnick"] != self.nick:
            body = msg["body"]
            if body.startswith("/me "):
                write("**{} {}**".format(msg["mucnick"], body[4:]))
            else:
                write("<{}> {}".format(msg["mucnick"], body))

    def resend(self, message):
        self.send_message(self.room, message, mtype="groupchat")


class ListenerThread(Thread):
    "Input FIFO listener."
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name

    def run(self):
        sleep(5)
        while True:
            with open(cfg["xmpp"]["in"], "r") as fifo_read:
                s = fifo_read.read().strip()
                xmpp.resend(s)
            sleep(.5)


cfg = json.loads(open("config.json").read())

create_fifo(cfg["xmpp"]["out"])
create_fifo(cfg["xmpp"]["in"])
listener_thread = ListenerThread("XMPP fifo listener")
listener_thread.start()

xmpp = Bot(cfg["xmpp"]["jid"], cfg["xmpp"]["password"],
           cfg["xmpp"]["room"], cfg["xmpp"]["nick"])
xmpp.register_plugin("xep_0030") # Service Discovery
xmpp.register_plugin("xep_0045") # MUC
xmpp.register_plugin("xep_0199") # Ping
if xmpp.connect():
    xmpp.process(block=True)
    print("Connected")
else:
    print("Unable to connect")
