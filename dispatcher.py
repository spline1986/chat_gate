#!/usr/bin/env python3

import json
import os
from datetime import datetime
from threading import Thread
from time import sleep


def read(f):
    "Read from f."
    with open(f, "r") as read_fifo:
        return read_fifo.read().strip()


def write(s, f):
    "Write s into f."
    with open(f, "w") as write_fifo:
        write_fifo.write(s + "\n")

def to_log(s):
    today = datetime.now().strftime("%Y.%m.%d")
    now = datetime.now().strftime("%H:%M")
    with open("logs/log_{}.txt".format(today), "a") as log:
        log.write("[{}] {}\n".format(now, s))


class ListenerThread(Thread):
    "Out FIFO listener."
    def __init__(self, name, src):
        Thread.__init__(self)
        self.name = name
        self.src = src
        self.dsts = []
        for key in cfg.keys():
            if key != "host" and cfg[key] != src:
                self.dsts.append(cfg[key])

    def run(self):
        if self.src["enabled"]:
            sleep(5)
            while True:
                sleep(0.1)
                s = read(self.src["out"])
                to_log(s)
                for dst in self.dsts:
                    if dst["enabled"]:
                        write(s, dst["in"])


def load_config():
    "Loads config.json into cfg variable."
    return json.loads(open("config.json").read())

if not os.path.exists("logs"):
    os.mkdir("logs")
cfg = load_config()
tg_dispatcher = ListenerThread("tg_dispatch", cfg["tg"])
tg_dispatcher.start()
xmpp_dispatcher = ListenerThread("xmpp_dispatch", cfg["xmpp"])
xmpp_dispatcher.start()
irc_dispatcher = ListenerThread("irc_dispatch", cfg["irc"])
irc_dispatcher.start()
