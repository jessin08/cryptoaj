#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

# For REST Call
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

# For coinmarketcap API
from coinmarketcap import Market
from telegram.ext.defaults import Defaults
coinmarketcap = Market()

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TELEGRAM_TOKEN = "1785720465:AAEkVuQy89a20UJTqD2LgcFXgQoip902ZTI"

# CoinMarketCap
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
lunarurl = 'https://api.lunarcrush.com/v2?'
parameters = {
  'start':'1',
  'limit':'5000',
  'convert':'USD'
}
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': '391881a0-fbdb-4045-a225-b8f11fa52e61',
}

session = Session()
session.headers.update(headers)


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


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    
def getCoinOfDay(update, context):
    params = {
        'data': 'coinoftheday',
        'key': '4mu863tc1wqgojnbiovi7w'
    }
    try:
        response = session.get(lunarurl, params=params)
        data = json.loads(response.text)
        update.message.reply_text("Coin of the day is " + json.dumps(data.data.symbol))
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    
def getPrice(update, context):
    update.message.reply_text("Just a moment, please...")
    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        update.message.reply_text("Price is " + json.dumps(data))
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

def getListings(update, context):
    update.message.reply_text("Just a moment, please...")
    if len(context.args) > 2:
        crypto = context.args[0].upper()
        sign = context.args[1]
        price = context.args[2]
        response = f"⏳ I will send you a message when the price of {crypto} reaches £{price}, \n"
        
        # response += f"the current price of {crypto} is £{coinbase_client.get_spot_price(currency_pair=crypto + '-GBP')['amount']}"
    else:
        response = '⚠️ Please provide a crypto code and a price value: \n<i>/price_alert {crypto code} {> / &lt;} {price}</i>'
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    # data = coinmarketcap.listings()
    # print(data)
        


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token=TELEGRAM_TOKEN, defaults=Defaults(parse_mode=ParseMode.HTML), use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("cprice", getPrice))
    dp.add_handler(CommandHandler("listings", getListings))
    dp.add_handler(CommandHandler("coinofday", getCoinOfDay))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

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