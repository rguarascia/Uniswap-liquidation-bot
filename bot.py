#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

import logging
import requests
import json
from api_endpoints import getTokenAPI, getPoolAPI


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def getTokens(update, context):
    """Sends API requires for tokens"""
    user_text = update.message.text[4:].strip()

    if (' ' in user_text) or (not '/' in user_text):
        update.message.reply_text(
            "Use a slash `/` to declare pairs. Ex. `/liq CEL/ETH`")
        return

    requestedToken = user_text.split("/")[0]
    requestedPool = user_text.split("/")[1]

    tokenAPI_reply = getTokenAPI(requestedToken)
    if(not tokenAPI_reply):
        update.message.reply_text("Token not found")
        return

    tokenAPI_reply = tokenAPI_reply[0]

    poolAPI_reply = getPoolAPI(
        tokenAPI_reply['id'], tokenAPI_reply['symbol'], requestedPool)

    if (not poolAPI_reply):
        update.message.reply_text("Pool not found")

    poolAPI_reply = poolAPI_reply[0]

    logger.info(poolAPI_reply)

    short_id = "{}...{}".format(
        poolAPI_reply['id'][0:4], poolAPI_reply['id'][-4:])

    update.message.reply_text("Uniswap Liquidation for {} \n$ {:,}\nFee Tier: {}%\n[{}]({})".format(
        user_text, round(float(
            poolAPI_reply['totalValueLockedUSD']), 2), round(int(poolAPI_reply['feeTier'])/100000, 2), short_id,
        "https://info.uniswap.org/#/pools/{}".format(poolAPI_reply["id"])))


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(
        "", use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("liq", getTokens))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()