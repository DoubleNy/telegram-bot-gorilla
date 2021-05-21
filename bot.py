import logging
import time
import os
import cloudscraper
import json
import datetime
import requests
import telegram
import json

from telegram.ext import Updater, CommandHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

limit_time = 0

def get_change(current, previous):
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return float('inf')


def get_reply_time():
    global limit_time

    return time.time() - limit_time


def allow_reply():
    global limit_time

    current = time.time() - limit_time

    return current >= 5


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hey this is your bot, Uncle Space Bot!\n'
                              'I am glad to serve you with most updated info.')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(text='<b>/p</b> or <b>/price</b> shows the price for SPACEGORILLA.\n'
                                   '<b>/t</b> or <b>/time</b> Time until the bot will be released (anti-spam).\n'
                                   '<b>/help</b> helps you in finding the commands supported by the bot.\n\n',
                              parse_mode=telegram.ParseMode.HTML
                              )


def tm_time(update, context):
    """Send a message when the command /help is issued."""

    if not allow_reply():
        time = get_reply_time()
        update.message.reply_text(text=f'Bot will be released in <b>{round(5 - time, 1)}</b> <i>sec.</i>',
                                  parse_mode=telegram.ParseMode.HTML)

        return

    update.message.reply_text(text='Bot is waiting for your command...', parse_mode=telegram.ParseMode.HTML)


def price(update, context):
    today = datetime.date.today()
    first_day = datetime.date(2021, 5, 11)

    global limit_time

    if not allow_reply():
        return

    scraper = cloudscraper.create_scraper()

    api_response = {}

    coin_name = ''
    coin_price_usd = 0
    coin_price_change = 0
    coin_mcapp = 0
    coin_mcapp_formatted = 0

    transactions_count = 0
    transactions_change = 0

    liquidity_usd = 0

    volume_usd = 0
    volume_change = 0

    coin_supply = 717.2
    url_pancake = 'https://exchange.pancakeswap.finance/#/swap?outputCurrency=0xd948a2c11626a0efc25f4e0cea4986056ac41fed&inputCurrency=BNB'
    url_bogged = 'https://bogged.finance/swap?token=0xd948A2c11626a0EFC25f4e0ceA4986056AC41feD'
    url_dexguru = 'https://dex.guru/token/0xd948a2c11626a0efc25f4e0cea4986056ac41fed-bsc'
    url_poocoin = 'https://poocoin.app/tokens/0xd948a2c11626a0efc25f4e0cea4986056ac41fed'

    error_fetching = False

    try:
        api_response = json.loads(
            scraper.get("https://api.dex.guru/v1/tokens/0x9e4A6BE811a4c6b02dE37186B32711E186eacb41").text)

        coin_name = api_response['symbol']
        coin_price = float(api_response['priceUSD'] * 1e6)
        coin_price_change = api_response['priceChange24h']

        coin_mcapp = round(coin_supply * 1e6 * coin_price)
        coin_mcapp_formatted = "{:,}".format(coin_mcapp)

        transactions_count = api_response['txns24h']
        transactions_change = api_response['txns24hChange']

        liquidity_usd = api_response['liquidityUSD']

        volume_usd = api_response['volume24hUSD']
        volume_change = api_response['volumeChange24h']

    except:
        error_fetching = True
        coin_name = api_response['data']['coin_name']
        coin_price = float(api_response['data']['coin_price']) * 1e6
        coin_mcapp = round(coin_supply * 1e6 * coin_price)
        coin_mcapp_formatted = "{:,}".format(coin_mcapp)

    limit_time = time.time()

    num_days = today - first_day

    if not error_fetching:
        update.message.reply_text(text=f"         🚀   {coin_name}   🚀\n\n"
                                       # f"💰  1M tokens: <b>${round(coin_price, 8)}</b><i>({round(coin_price / coin_price_change * 100)}% last 24h)</i> \n"
                                       f"💰  1M tokens: <b>${round(coin_price, 8)}</b>\n"
                                       f"💴  Market cap: <b>${coin_mcapp_formatted}</b> \n"
                                       # f"💬  Transactions count (24h): <b>{round(transactions_count)}</b><i>({round(transactions_change * 100)}% last 24h)</i>\n"
                                       f"💬  Transactions count (24h): <b>{round(transactions_count)}</b>\n"
                                       # f"📊  Volume (24h): <b>${round(volume_usd)}</b><i>({round(volume_change * 100)}% last 24h)</i>\n"
                                       f"📊  Volume (24h): <b>${round(volume_usd)}</b>\n"
                                       f"💸  Liquidity (24h): <b>${round(liquidity_usd)}</b>\n"
                                       f"🎚  Supply: <b>{coin_supply}t</b> \n",
                                       # f"⏰  Time Since Launch {num_days.days} days\n\n"
                                  parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    # 1773001800:AAHtAX5DUReFenUYgwpteZCfn4S66z-KFiY

    # updater = Updater(os.environ['TELEGRAM_TOKEN'], use_context=True)
    updater = Updater('1638812538:AAGgOpb-sjPDvRToFU2j4GiPiSerPUlFJ7o', use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("price", price))
    dp.add_handler(CommandHandler("p", price))
    dp.add_handler(CommandHandler("time", tm_time))
    dp.add_handler(CommandHandler("t", tm_time))

    # dp.add_handler(CommandHandler("price_bogged", priceB))
    # dp.add_handler(CommandHandler("p_bogged", priceB))
    #
    # dp.add_handler(CommandHandler("price_pancake", priceP))
    # dp.add_handler(CommandHandler("p_pancake", priceP))
    # log all errors
    dp.add_error_handler(error)

    global ticks_update_time
    global limit_time

    ticks_update_time = time.time()

    limit_time = time.time()
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
