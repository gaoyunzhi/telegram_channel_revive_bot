#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import yaml
import time
from telegram.ext import Updater, MessageHandler, Filters
from db import DB
import threading
import traceback as tb
from datetime import datetime

START_MESSAGE = ('''
Add this bot to your public channel, it will loop through the old message gradually 
if no activity in a set period of time.
''')

db = DB()

with open('CREDENTIALS') as f:
    CREDENTIALS = yaml.load(f, Loader=yaml.FullLoader)

test_channel = -1001459876114
debug_group = CREDENTIALS.get('debug_group') or -1001198682178

def valid(r):
    if r.media_group_id:
        return False
    if r.photo:
        return True
    if not r.text:
        return False
    if r.text.startswith('/'):
        return False
    if len(r.text) < 10:
        return False
    return True

def manage(update, context):
    try:
        chat_id = update.effective_chat and update.effective_chat.id
        if not chat_id:
            return
        msg = update.effective_message
        if (not msg) or (not valid(msg)):
            return
        if not db.hasChatId(chat_id):
            db.addChatId(chat_id)
        db.setTime(chat_id)
    except Exception as e:
        updater.bot.send_message(chat_id=debug_group, text=str(e))    


def start(update, context):
    if update.message:
        update.message.reply_text(START_MESSAGE, quote=False)

updater = Updater(CREDENTIALS['bot_token'], use_context=True)
dp = updater.dispatcher

dp.add_handler(MessageHandler(~Filters.private, manage))
dp.add_handler(MessageHandler(Filters.private, start))

def loopImp():
    for chat_id in db.chatIds():
        if (not db.ready(chat_id)) or (chat_id in [debug_group, test_channel]):
            continue
        for _ in range(10):
            pos = db.iteratePos(chat_id)
            try:
                r = updater.bot.forward_message(
                    chat_id = test_channel, message_id = pos, from_chat_id = chat_id)
                if time.time() - datetime.timestamp(r.forward_date) < 10 * 60 * 60 * 24:
                    db.rewindPos(chat_id)
                    break
                if not valid(r):
                    continue
                if r.photo:
                    updater.bot.send_photo(
                        chat_id = chat_id, caption = r.text, photo = r.photo)
                else:
                    updater.bot.send_message(
                        chat_id = chat_id, text = r.text, photo = r.photo)
                db.setTime(chat_id)
                break
            except Exception as e:
                if str(e) in ['Message to forward not found', "Message can't be forwarded"]:
                    pos = db.iteratePos(chat_id)
                else:
                    raise e

def loop():
    try:
        loopImp()
    except Exception as e:
        print(e)
        tb.print_exc()
        try:
            updater.bot.send_message(chat_id=debug_group, text=str(e))
        except:
            pass
    threading.Timer(3600, loop).start()

threading.Timer(1, loop).start()

updater.start_polling()
updater.idle()