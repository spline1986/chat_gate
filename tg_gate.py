#!/usr/bin/env python3

import json
import os
import telebot
from threading import Thread
from time import sleep


cfg = json.loads(open("tg_gate.json").read())
bot = telebot.TeleBot(cfg["token"])


def create_fifo(path):
    if os.path.exists(path):
        os.unlink(path)
    if not os.path.exists(path):
        os.mkfifo(path)

def write(s):
    with open(cfg["out"], "w") as write_fifo:
        write_fifo.write(s + "\n")


class MyThread(Thread):
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name

    def run(self):
        sleep(5)
        while True:
            with open(cfg["in"], "r") as fifo_read:
                s = fifo_read.read().strip()
                bot.send_message(233587284, s)
            sleep(.5)


@bot.message_handler(content_types=['text'])
def get_text(message):
    user = "{} {}".format(message.from_user.first_name,
                          message.from_user.last_name)
    write("<{}>: {}".format(user.strip(), message.text))


@bot.message_handler(content_types=["audio", "document", "photo"])
def get_photo(message):
    if message.photo:
        file_id = message.photo[0].file_id
    elif message.document:
        file_id = message.document.file_id
    elif message.audio:
        file_id = message.audio.file_id
    file_info = bot.get_file(file_id)
    ext = file_info.file_path.split(".")[-1]
    f = bot.download_file(file_info.file_path)
    open(file_id + "." + ext, "wb").write(f)


create_fifo(cfg["out"])
create_fifo(cfg["in"])
my_thread = MyThread("Telegram fifo listener")
my_thread.start()
bot.polling()
