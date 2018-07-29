#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import os
import time
import sys
from copy import copy
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Handler
from telegram import Chat
from datetime import datetime

_port = int(os.environ['PORT'])
_webhook = "%s%s" % (os.environ["WEB_HOOK"], os.environ["BOT_TOKEN"])
_token = os.environ["BOT_TOKEN"]
_location = os.environ["URL_LOCATION"]
_certificate = os.environ["CERTIFICATE"]
_listen = "127.0.0.1"

# Enable logging
logging.basicConfig(stream=sys.stderr, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)

# Group title : Group id
# Bot forwards messages from group identified by title to group identified by id
source = -277686843
test = -254343904
target = set()

try:
    db = open("data/groups.txt", "r")
    line = db.readline()
    while line:
        try:
            target.add(int(line));
        except Exception as e:
            logger.warn("Exception: %s" % e)
        
        line = db.readline()
    
    db.close()
except Exception as e:
    logger.warn("Exception: %s" % e)

logger.info(target)
def sendid(chat):
    chat.send_message(chat.id)

def showid(bot, update):
    logger.info("Showid")
    sendid(update.message.chat)

def publish(bot, update):
    logger.info("Publish")
    if (update.message.chat.id == source):
        sent = []

        for tid in target:
            logger.info("Publish in %d" % tid)
            smsg = bot.send_message(tid, update.message.text)
            sent.append((smsg.chat.id, smsg.message_id))            

        f = open("data/messages.txt", "a")
        f.write(json.dumps({update.message.message_id: sent}))
        f.write("\n")
        f.close()

        bot.send_message(update.message.chat.id, update.message.message_id)

def forward(bot, update):
    logger.info("Forward")
    if (update.message.chat.id == source):
        sent = []

        for tid in target:
            logger.info("Publish in %d" % tid)
            smsg = bot.forward_message(tid, update.message.chat.id, update.message.message_id)
            sent.append((smsg.chat.id, smsg.message_id))            

        f = open("data/messages.txt", "a")
        f.write(json.dumps({update.message.message_id: sent}))
        f.write("\n")
        f.close()

        bot.send_message(update.message.chat.id, update.message.message_id)

def dump_target():
    try:
        db = open("data/groups.txt", "w")

        for cid in target:
            db.write("%d\n" % cid)

        db.close()
    except Exception as e:
        logger.warn("Exception: %s" % e)

def new_chat_members(bot, update):
    logger.info("Added to chat")

    if ((update.message.chat.id not in target) and (update.message.chat.id != source)):
        target.add(update.message.chat.id)
        dump_target()

def left_chat_member(bot, update):
    logger.info("Left chat")

    if (update.message.left_chat_member.id == bot.id):
        if (update.message.chat.id in target):
            target.remove(update.message.chat.id)
            dump_target()

def edit(bot, update):
    logger.info("Edit message")

    if (update.edited_message.chat.id != source): return

    strid = "%d" % update.edited_message.message_id
    f = open("data/messages.txt", "r")
    line = f.readline()
    while line:
        msg = json.loads(line.strip())
        if strid in msg:
            logger.info("Edit %d" % update.edited_message.message_id)

            for chat in msg[strid]:
                bot.edit_message_text(update.edited_message.text, chat[0], chat[1])

            break

        line = f.readline()

    f.close()

def delete(bot, update):
    logger.info("Delete message")
    
    if (update.message.chat.id != source): return

    tid = 0
    chat = None
    if (update.channel_post):
        tid = update.channel_post.text.split("/delete")[1].strip()
        chat = update.channel_post.chat
    elif (update.message):
        tid = update.message.text.split("/delete")[1].strip()
        chat = update.message.chat
    else:
        return

    if (chat.id != source):
        return

    f = open("data/messages.txt", "r")
    line = f.readline()
    while line:
        msg = json.loads(line.strip())
        if tid in msg:
            logger.info("Delete %s" % tid)

            for chat in msg[tid]:
                bot.delete_message(chat[0], chat[1])

            break

        line = f.readline()

    f.close()

def test(bot, update):
    logger.info("Test")
    
    if (update.message.chat.id != source): return

    cmd = update.message.text.split("/delete")

    if (len(cmd) == 1):
        if (status == 0):
            bot.send_message(source, "Testing mode: Bot is forwarding to  group only")
        else:
            bot.send_message(source, "Production mode: Bot is forwarding to all chats")
        

def fallback(bot, update, user_data, job_queue, chat_data, update_queue):
    logger.info("Fallback")

    if (update.channel_post):
        logger.info("Channel post %d" % update.channel_post.message_id)
        if (len(update.channel_post.entities) and update.channel_post.entities[0].type == "bot_command"):
            if (update.channel_post.text[0:7] == "/showid"):
                sendid(update.channel_post.chat)

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.error('Update "%s" caused error "%s"', update, error)

def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    logger.info("Creating updater object with token: '%s'" % (_token))

    updater = Updater(_token)

    i = 0
    while i < 3:
        try:
            logger.info("Starting webhook '%s' %d '%s'" % (_listen, _port, _location))
            updater.start_webhook(listen=_listen, port=_port, url_path=_location)
            logger.info("Setting webhook with certificate '%s'" % (_certificate))
            updater.bot.set_webhook(url=_webhook, certificate=open(_certificate, 'rb'), timeout=5000)
            break
        except Exception as e:
            logger.error("Exception: %s" % e)
            updater.stop()

        i += 1
        time.sleep(2)
    #endwhile
 
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("showid", showid))
    dp.add_handler(CommandHandler("delete", delete))
    dp.add_handler(CommandHandler("test", delete))
    dp.add_handler(MessageHandler(Filters.text, publish))
    dp.add_handler(MessageHandler(Filters.photo | Filters.document | Filters.voice | Filters.video | Filters.sticker | Filters.video_note | Filters.contact | Filters.venue | Filters.location, forward))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_chat_members))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, left_chat_member))
    dp.add_handler(MessageHandler(Filters.text, edit, message_updates = False, channel_post_updates = False, edited_updates = True))
    #dp.add_handler(MessageHandler(Filters.all, fallback))

    # log all errors
    dp.add_error_handler(error)

    logger.info("Running")

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
