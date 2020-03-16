#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import time
from telegram.ext import Updater, MessageHandler, Filters
from db import DB, HOUR
import threading
from telegram_util import log_on_fail, splitCommand, autoDestroy
from telegram import InputMediaPhoto
from bs4 import BeautifulSoup
import cached_url

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
        autoDestroy(msg.reply_text('success'), 0.1)
        msg.delete()
        return
    db.setTime(chat_id)

def start(update, context):
    if update.message:
        update.message.reply_text(START_MESSAGE, quote=False)

tele.dispatcher.add_handler(MessageHandler(~Filters.private, manage))
tele.dispatcher.add_handler(MessageHandler(Filters.private, start))

def getAllPos(link):
    s = BeautifulSoup(cached_url.get(link), 'html.parser')
    result = []
    for a in s.find_all('a', class_='grouped_media_wrap'):
        result.append(int(a.get('href', '').strip().split('/')[-1]))
    return sorted(result)

def forwardMsg(reciever, sender, pos, bot, debug_group):
    link = 'https://t.me/%s/%d' % \
        (tele.bot.get_chat(sender).username, pos)
    all_pos = getAllPos(link)
    print(all_pos)
    if not all_pos:
        try:
            return [bot.forward_message(chat_id = reciever, 
                message_id = pos, from_chat_id = sender)]
        except:
            return []
            
    group = []
    for np in all_pos:
        r = bot.forward_message(chat_id = debug_group.id, 
            from_chat_id = sender, message_id = np)
        r.delete()
        m = InputMediaPhoto(r.photo[-1].file_id, 
            caption=r.caption_markdown, parse_mode='Markdown')
        if r.caption_markdown:
            group = [m] + group
        else:
            group.append(m)
    return bot.send_media_group(reciever, group)

@log_on_fail(debug_group)
def loopImp():
    for chat_id in db.chatIds():
        if (not db.ready(chat_id)) or (chat_id in [debug_group.id]):
            continue
        if chat_id != -1001341438972: # testing
            continue
        for _ in range(10):
            pos = db.iteratePos(chat_id)
            r = forwardMsg(chat_id, chat_id, pos, tele.bot, debug_group)
            if not r:
                continue
            for _ in range(len(r) - 1):
                db.iteratePos(chat_id)
            db.setTime(chat_id)
            break

def loop():
    loopImp()
    threading.Timer(HOUR, loop).start()

threading.Timer(1, loop).start()

tele.start_polling()
tele.idle()