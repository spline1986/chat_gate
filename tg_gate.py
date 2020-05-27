#!/usr/bin/env python3

import json
import os
import telebot
from threading import Thread
from time import sleep


cfg = json.loads(open("config.json").read())
bot = telebot.TeleBot(cfg["tg"]["token"])


def create_fifo(path):
    "Create FIFO file by path."
    if os.path.exists(path):
        os.unlink(path)
    if not os.path.exists(path):
        os.mkfifo(path)

def write(s):
    "Write s into output FIFO."
    with open(cfg["tg"]["out"], "w") as write_fifo:
        write_fifo.write(s + "\n")


class ListenerThread(Thread):
    "Input FIFO listener."
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name

    def run(self):
        sleep(5)
        while True:
            sleep(0.1)
            with open(cfg["tg"]["in"], "r") as fifo_read:
                s = fifo_read.read().strip()
                if cfg["tg"]["chat"]:
                    bot.send_message(cfg["tg"]["chat"], s)
            sleep(.5)


def make_username(first, last):
    username = ""
    if first:
        username += first
    if last:
        username += " {}".format(last)
    return username


@bot.message_handler(content_types=['text'])
def get_text(message):
    "Write incoming message into out FIFO."
    if not cfg["tg"]["chat"]:
        print("Message from chat {}".format(message.chat.id))
    user = make_username(message.from_user.first_name,
                         message.from_user.last_name)
    write("<{}> {}".format(user.strip(), message.text))


@bot.message_handler(content_types=["audio", "document", "photo"])
def get_photo(message):
    "Write incoming file into files/ directory."
    if message.photo:
        file_id = message.photo[0].file_id
    elif message.document:
        file_id = message.document.file_id
    elif message.audio:
        file_id = message.audio.file_id
    file_info = bot.get_file(file_id)
    ext = file_info.file_path.split(".")[-1]
    f = bot.download_file(file_info.file_path)
    open("files/{}.{}".format(file_id, ext), "wb").write(f)
    user = make_username(message.from_user.first_name,
                         message.from_user.last_name)
    write("<{}> {}".format(user.strip(),
                           "http://{}/files/{}.{}".format(cfg["host"],
                                                          file_id,
                                                          ext)))


if not os.path.exists("files"):
    os.mkdir("files")
create_fifo(cfg["tg"]["out"])
create_fifo(cfg["tg"]["in"])
listener_thread = ListenerThread("Telegram fifo listener")
listener_thread.start()
bot.polling()
