#!/usr/bin/env python3

import json
import os
from telegram.ext import Filters, MessageHandler, Updater
from telegram import File
from threading import Thread
from time import sleep


cfg = json.loads(open("config.json").read())
kwargs = {}
if cfg["tg"]["proxy"]:
    kwargs["proxy_url"] = cfg["tg"]["proxy"]
updater = Updater(token=cfg["tg"]["token"], use_context=True,
                  request_kwargs=kwargs)
dispatcher = updater.dispatcher


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
            with open(cfg["tg"]["in"], "r") as fifo_read:
                s = fifo_read.read().strip()
                if cfg["tg"]["chat"]:
                    updater.bot.send_message(cfg["tg"]["chat"], s)
            sleep(1)


def make_username(first, last):
    username = ""
    if first:
        username += first
    if last:
        username += " {}".format(last)
    return username


def make_text(message, text):
    firstname = message.from_user.first_name
    lastname = message.from_user.last_name
    user = make_username(firstname, lastname)
    reply = message.reply_to_message
    if reply:
        firstname = reply.from_user.first_name
        lastname = reply.from_user.last_name
        to = make_username(firstname, lastname)
        rtext = reply.text
        body = "<{}> > {}: {}\n\n{}".format(user, to, rtext, text)
    else:
        body = "<{}> {}".format(user, text)
    return body


def out(update, context):
    if not cfg["tg"]["chat"]:
        print(update.effective_chat.id)
    else:
        text = make_text(update.message, update.message.text)
        write(text)


def media(update, context):
    caption = False
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        caption = update.message.caption
    elif update.message.audio:
        file_id = update.message.audio.file_id
    elif update.message.document:
        file_id = update.message.document.file_id
        caption = update.message.caption
    elif update.message.voice:
        file_id = update.message.voice.file_id
    f = updater.bot.get_file(file_id)
    ext = f.file_path.split(".")[-1]
    filename = f.download(custom_path="files/{}.{}".format(file_id, ext))
    text = make_text(update.message,
                     "http://{}/{}\n".format(cfg["host"], filename))
    write(text)
    if update.message.text:
        text = make_text(update.message, update.message.text)
        write(text)
    if caption:
        text = make_text(update.message, caption)
        write(text)


out_handler = MessageHandler(Filters.text & (~Filters.command), out)
media_handler = MessageHandler(Filters.all, media)
dispatcher.add_handler(out_handler)
dispatcher.add_handler(media_handler)

if not os.path.exists("files"):
    os.mkdir("files")
create_fifo(cfg["tg"]["out"])
create_fifo(cfg["tg"]["in"])
listener_thread = ListenerThread("Telegram fifo listener")
listener_thread.start()
updater.start_polling()
