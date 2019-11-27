#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import time
from telegram.ext import Updater, MessageHandler, Filters
from db import DB
import threading
from datetime import datetime
from telegram_util import log_on_fail, isMeaningful

START_MESSAGE = ('''
Add this bot to your public channel, it will loop through the old message gradually 
if no activity in a set period of time.
''')

db = DB()

with open('CREDENTIALS') as f:
    CREDENTIALS = yaml.load(f, Loader=yaml.FullLoader)
tele = Updater(CREDENTIALS['bot_token'], use_context=True)
r = tele.bot.send_message(-1001198682178, 'start')
r.delete()
debug_group = r.chat
test_channel = -1001459876114

@log_on_fail(debug_group)
def manage(update, context):
    chat_id = update.effective_chat and update.effective_chat.id
    if not chat_id:
        return
    msg = update.effective_message
    if (not msg) or (not isMeaningful(msg)):
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
        if (not db.ready(chat_id)) or (chat_id in [debug_group.id, test_channel]):
            continue
        for _ in range(10):
            pos = db.iteratePos(chat_id)
            try:
                r = tele.bot.forward_message(
                    chat_id = test_channel, message_id = pos, from_chat_id = chat_id)
                if r.forward_date == None:
                    print(r)
                    continue
                if time.time() - datetime.timestamp(r.forward_date) < 10 * 60 * 60 * 24:
                    db.rewindPos(chat_id)
                    break
                if not isMeaningful(r):
                    continue
                if r.photo:
                    tele.bot.forward_message(
                        chat_id = chat_id, message_id = pos, from_chat_id = chat_id)
                else:
                    tele.bot.send_message(chat_id = chat_id, text = r.text)
                db.setTime(chat_id)
                break
            except Exception as e:
                if str(e) in ['Message to forward not found', "Message can't be forwarded"]:
                    continue
                else:
                    raise e

def loop():
    loopImp()
    threading.Timer(3600, loop).start()

threading.Timer(1, loop).start()

tele.start_polling()
tele.idle()