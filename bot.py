#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import os
import time
import sys
from copy import copy
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
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
source = {-277686843}
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

def showid(bot, update):
    update.message.chat.send_message(update.message.chat.id)

def publish(bot, update):
    if (update.message.chat.id in source):
        for tid in target:
            logger.info("Publish in %d" % tid)
            bot.send_message(tid, update.message.text)

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

    if ((update.message.chat.id not in target) and (update.message.chat.id not in source)):
        target.add(update.message.chat.id)
        dump_target()

def left_chat_member(bot, update):
    logger.info("Left chat")

    if (update.message.left_chat_member.id == bot.id):
        if (update.message.chat.id in target):
            target.remove(update.message.chat.id)
            dump_target()

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
    dp.add_handler(MessageHandler(Filters.text, publish))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_chat_members))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, left_chat_member))

    # log all errors
    dp.add_error_handler(error)

    logger.info("Running")

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
