#!/usr/bin/env python3

import json
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


class ListenerThread(Thread):
    "Out FIFO listener."
    def __init__(self, name, flag1, flag2, fout, fin):
        Thread.__init__(self)
        self.name = name
        self.flag1 = flag1
        self.flag2 = flag2
        self.fout = fout
        self.fin = fin

    def run(self):
        sleep(5)
        while True:
            sleep(0.1)
            if self.flag1:
                s = read(self.fout)
                if self.flag2:
                    write(s, self.fin)


def load_config():
    "Loads config.json into cfg variable."
    return json.loads(open("config.json").read())


cfg = load_config()
tg_dispatcher = ListenerThread("tg_disatch", cfg["tg"]["enabled"], cfg["xmpp"]["enabled"], cfg["tg"]["out"], cfg["xmpp"]["in"])
tg_dispatcher.start()
xmpp_dispatcher = ListenerThread("tg_disatch", cfg["xmpp"]["enabled"], cfg["tg"]["enabled"], cfg["xmpp"]["out"], cfg["tg"]["in"])
xmpp_dispatcher.start()
