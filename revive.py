#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import time
from telegram.ext import Updater, MessageHandler, Filters
from db import DB
import threading
from datetime import datetime
from telegram_util import log_on_fail, splitCommand, autoDestroy

START_MESSAGE = ('''
Add this bot to your public channel, it will loop through the old message gradually 
if no activity in a set period of time.
''')

db = DB()

with open('CREDENTIALS') as f:
    CREDENTIALS = yaml.load(f, Loader=yaml.FullLoader)
tele = Updater(CREDENTIALS['bot_token'], use_context=True)
debug_group = tele.bot.get_chat(-1001198682178)

@log_on_fail(debug_group)
def manage(update, context):
    chat_id = update.effective_chat and update.effective_chat.id
    if not chat_id:
        return
    msg = update.effective_message
    if not msg:
        return
    command, text = splitCommand(msg.text)
    if 'interval' in command:
        db.setInterval(chat_id, int(text))
        autoDestroy(msg.reply_text('success'))
        msg.delete()
        return
    db.setTime(chat_id)

def start(update, context):
    if update.message:
        update.message.reply_text(START_MESSAGE, quote=False)

dp = tele.dispatcher
dp.add_handler(MessageHandler(~Filters.private, manage))
dp.add_handler(MessageHandler(Filters.private, start))

@log_on_fail(debug_group)
def loopImp():
    for chat_id in db.chatIds():
        if (not db.ready(chat_id)) or (chat_id in [debug_group.id]):
            continue
        for _ in range(10):
            pos = db.iteratePos(chat_id)
            try:
                r = tele.bot.forward_message(
                    chat_id = chat_id, message_id = pos, from_chat_id = chat_id)
            except:
                continue
            if time.time() - datetime.timestamp(r.forward_date) < 10 * 60 * 60 * 24:
                db.rewindPos(chat_id)
                r.delete()
            else:
                db.setTime(chat_id)
            break

def loop():
    loopImp()
    threading.Timer(3600, loop).start()

threading.Timer(1, loop).start()

tele.start_polling()
tele.idle()