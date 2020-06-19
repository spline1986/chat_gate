#!/usr/bin/env python3

import json
import os
from datetime import datetime
from mimetypes import guess_extension
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
        if not rtext:
            file_id, filename, caption, doc = get_media(reply)
            if caption:
                rtext = caption
            else:
                rtext = "<media>"
        if not rtext: rtext = "..."
        body = "<{}> > {}: {}\n{}".format(user, to, rtext, text)
    else:
        body = "<{}> {}".format(user, text)
    return body


def out(update, context):
    if not cfg["tg"]["chat"]:
        print(update.effective_chat.id)
    else:
        text = make_text(update.message, update.message.text)
        write(text)


def get_media(message):
    file_id = False
    caption = False
    filename = False
    doc = False
    if message.photo:
        file_id = message.photo[-1].file_id
        caption = message.caption
        filename = "photo"
    elif message.audio:
        file_id = message.audio.file_id
        filename = "audio"
    elif message.document:
        file_id = message.document.file_id
        caption = message.caption
        filename = message.document.file_name
        doc = True
    elif message.voice:
        file_id = message.voice.file_id
        filename = "voice"
    elif message.sticker:
        caption = "{} <sticker>".format(message.sticker.emoji)
    return file_id, filename, caption, doc


def media(update, context):
    file_id, filename, caption, doc = get_media(update.message)
    if file_id:
        f = updater.bot.get_file(file_id)
        ext = f.file_path.split(".")[-1]
        directory = datetime.now().strftime("%Y%m%d%H%M%S")
        os.mkdir("files/{}".format(directory))
        if not doc:
            filename += "." + ext
        savedname = f.download(
            custom_path="files/{}/{}".format(directory, filename)
        )
        text = make_text(update.message,
                         "http://{}/{}".format(cfg["host"],
                                               savedname.replace(" ", "%20")))
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
