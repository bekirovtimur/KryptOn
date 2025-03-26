import os
import telebot
import mysql.connector
import qrcode
import time
import random
import string
import schedule
from threading import Thread
from io import BytesIO
from telebot import types
from datetime import datetime, timedelta

subscribe_server_url = os.getenv("SUBSCRIPTION_SERVER_URL")
subscriptions_max_count = int(os.getenv("SUBSCRIPTIONS_MAX_COUNT", 5)) # Maximum number of subscriptions per user
bot_token = os.getenv("BOT_TOKEN") # Telegram bot API key
db_config = {
    'host': os.getenv("MYSQL_HOST", "mysql"),
    'user': os.getenv("MYSQL_USER", "root"),
    'password': os.getenv("MYSQL_PASSWORD", "rootpassword"),
    'database': os.getenv("MYSQL_DATABASE", "krypton"),
    'port': 3306
}
bot = telebot.TeleBot(bot_token)
db = mysql.connector.connect(**db_config)

@bot.message_handler(commands=['start'])
# Reaction on /start command
def user_check(message):
    # Check is user exists in database
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    sql = "SELECT * FROM users WHERE chat_id = %s"
    cursor = db.cursor()
    cursor.execute(sql, (chat_id,))
    user = cursor.fetchone()

    if user:
        # If user exists, update information about user in database
        sql = "UPDATE users SET chat_id = %s, username = %s, first_name = %s, last_name = %s WHERE tg_user_id = %s"
        val = (chat_id, username, first_name, last_name, user_id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()

    else:
        # If user not exists, add information about user to database
        sql = "INSERT INTO users (chat_id, tg_user_id, username, first_name, last_name) VALUES (%s, %s, %s, %s, %s)"
        val = (chat_id, user_id, username, first_name, last_name)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()

    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(message.chat.id,f'🔹<b>KryptOn</b>🔹', parse_mode='html')
    menu(message)

def menu(message):
    # Main menu page
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🔹 Balance', callback_data='balance'))
    markup.add(types.InlineKeyboardButton('🔹 Subscriptions', callback_data='subscriptions'))
    markup.add(types.InlineKeyboardButton('🔹 Get Help', url='https://telegra.ph/KryptOn-03-26-3'))
    bot.send_message(message.chat.id,f'<b>Main Menu</b>', parse_mode='html', reply_markup=markup)

def balance(message):
    # Balance menu page
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🔹 Add Koins', url='https://t.me/CryptoBot'))
    markup.add(types.InlineKeyboardButton('🔹 Payment History', callback_data='pay_history'))
    markup.add(types.InlineKeyboardButton('🔹 Main Menu', callback_data='menu'))
    bot.send_message(message.chat.id,f'<b>Balance: </b>0 Koins\n<b>Subscriptions limit: </b>{subscriptions_max_count}\n', parse_mode='html', reply_markup=markup)

def pay_history(message):
    # Payments history menu page
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🔹 Back', callback_data='balance'))
    markup.add(types.InlineKeyboardButton('🔹 Main Menu', callback_data='menu'))
    bot.send_message(message.chat.id,f'<b>Payment History</b>\n<i>Payment history is empty</i>', parse_mode='html', reply_markup=markup)

def subscriptions(message):
    # List all active user subscriptions
    bill_user_id = get_user_id(message)
    subscription = get_user_subscriptions(bill_user_id)
    active_subscriptions_count = int(len(subscription))
    markup = types.InlineKeyboardMarkup()
    for subscription in subscription:
        flag = get_flag_emoji(subscription[3])
        markup.add(types.InlineKeyboardButton(f"{flag} {subscription[2]} - ID {subscription[0]}", callback_data=f"subscription_{subscription[0]}"))
    if active_subscriptions_count < subscriptions_max_count:
        markup.add(types.InlineKeyboardButton('➕ Add new subscription', callback_data='add_new_subscription'))
    markup.add(types.InlineKeyboardButton('🔹 Back', callback_data='menu'))
    markup.add(types.InlineKeyboardButton('🔹 Main Menu', callback_data='menu'))
    bot.send_message(message.chat.id, f"<b>Active subscriptions: </b>{active_subscriptions_count}", parse_mode='html', reply_markup=markup)

def subscription_info(message, subscription_id):
    # Menu page about selected active subscription
    markup = types.InlineKeyboardMarkup()
    subscription = get_subscription(subscription_id)
    name = subscription[0][2]
    flag = get_flag_emoji(subscription[0][3])
    region = subscription[0][3]
    active_until = datetime.fromtimestamp(subscription[0][4])
    token = subscription[0][1]
    cost = subscription[0][6]
    markup.add(types.InlineKeyboardButton('🔹 Copy Subscription Link', callback_data=f"subscriptionlink_{region}_{token}_{subscription_id}"))
    markup.add(types.InlineKeyboardButton('🔹 Show QR code', callback_data=f"subscriptionqr_{region}_{token}_{subscription_id}"))
    markup.add(types.InlineKeyboardButton('🔻 Remove Subscription', callback_data=f"unsubscribe_{subscription_id}"))
    markup.add(types.InlineKeyboardButton('🔹 Back', callback_data='subscriptions'))
    markup.add(types.InlineKeyboardButton('🔹 Main Menu', callback_data='menu'))
    bot.send_message(message.chat.id, f"<b>Subscription ID: </b>{subscription_id}\n<b>Name: </b>{name}\n<b>Region: </b>{flag} {region}\n<b>Cost: </b>{cost} Koins\n<b>Active Until: </b>{active_until}\n<b>Token: </b>{token}\n", parse_mode='html', reply_markup=markup)

def subscriptionlink_copy(message, region, token, subscription_id):
    # Copy Code menu page
    markup = types.InlineKeyboardMarkup()
    subscription_url = f"{subscribe_server_url}?token={token}"
    markup.add(types.InlineKeyboardButton('🔹 Back', callback_data=f"subscription_{subscription_id}"))
    markup.add(types.InlineKeyboardButton('🔹 Main Menu', callback_data='menu'))
    bot.send_message(message.chat.id, f"Click on the subscription link below to copy it to your clipboard:\n\n`{subscription_url}`", parse_mode="Markdown", reply_markup=markup)

def subscriptionqr_image(message, region, token, subscription_id):
    # QR Code menu page
    markup = types.InlineKeyboardMarkup()
    subscription_url = f"{subscribe_server_url}?token={token}"
    qr_img = generate_qr_code(subscription_url)  # Generate QR code
    byte_io = BytesIO()  # Save QR code to BytesIO
    qr_img.save(byte_io, 'PNG')
    byte_io.seek(0)  # Move cursor to zero point
    markup.add(types.InlineKeyboardButton('🔹 Back', callback_data=f"subscription_{subscription_id}"))
    markup.add(types.InlineKeyboardButton('🔹 Main Menu', callback_data='menu'))
    bot.send_photo(message.chat.id, byte_io, reply_markup=markup)

def new_subscription_list(message):
    # List all available subscriptions to purchase menu page
    all_subscriptions = get_all_subscriptions()
    markup = types.InlineKeyboardMarkup()
    for subscription in all_subscriptions:
        subscription_id = subscription[0]
        subscription_name = subscription[1]
        flag = get_flag_emoji(subscription[3])
        markup.add(types.InlineKeyboardButton(f"{flag} {subscription_name}", callback_data=f"new_subscription_info_{subscription_id}"))
    markup.add(types.InlineKeyboardButton('🔹 Back', callback_data='menu'))
    markup.add(types.InlineKeyboardButton('🔹 Main Menu', callback_data='menu'))
    bot.send_message(message.chat.id, '<b>Available subscriptions</b>', parse_mode='html', reply_markup=markup)

def new_subscription_info(message, subscription_id):
    # Purchase subscription (info about new subscription) menu page
    subscription = get_new_subscription_info(subscription_id)
    name = subscription[0][1]
    period_seconds = int(subscription[0][2])
    flag = get_flag_emoji(subscription[0][3])
    cost = subscription[0][4]
    current_time = int(time.time())
    active_until = datetime.fromtimestamp(current_time + period_seconds)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('➕ Purchase Subscription', callback_data=f"purchase_subscription_{subscription_id}_{period_seconds}"))
    markup.add(types.InlineKeyboardButton('🔹 Back', callback_data='add_new_subscription'))
    markup.add(types.InlineKeyboardButton('🔹 Main Menu', callback_data='menu'))
    bot.send_message(message.chat.id, f"<b>Subscription: </b>{flag} {name}\n<b>Active until: </b>{active_until}\n<b>Cost: </b>{cost} Koins\n<i>Please note that you must have no more than {subscriptions_max_count} active subscriptions!</i>\n<i>Once the specified limit is reached, you will not be able to connect additional subscriptions.</i>\n", parse_mode='html', reply_markup=markup)

def unsubscribe(message, subscription_id):
    # Unsubscribe menu page
    markup = types.InlineKeyboardMarkup()
    subscription = get_subscription(subscription_id)
    name = subscription[0][2]
    flag = get_flag_emoji(subscription[0][3])
    region = subscription[0][3]
    active_until = datetime.fromtimestamp(subscription[0][4])
    token = subscription[0][1]
    cost = subscription[0][6]
    markup.add(types.InlineKeyboardButton('🔻 Yes Remove Subscription', callback_data=f"remove_subscription_{subscription_id}"))
    markup.add(types.InlineKeyboardButton('🔹 Back', callback_data=f"subscription_{subscription_id}"))
    markup.add(types.InlineKeyboardButton('🔹 Main Menu', callback_data='menu'))
    bot.send_message(message.chat.id, f"<b>Are you sure you want to delete subscription?</b>\n<b>Subscription ID: </b>{subscription_id}\n<b>Name: </b>{name}\n<b>Region: </b>{flag} {region}\n<b>Cost: </b>{cost} Koins\n<b>Active Until: </b>{active_until}\n<b>Token: </b>{token}\n<b>Please note, this action cannot be undone!</b>", parse_mode='html', reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'balance':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        balance(callback.message)
    elif callback.data == 'menu':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        menu(callback.message)
    elif callback.data == 'pay_history':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        pay_history(callback.message)
    elif callback.data == 'subscriptions':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        subscriptions(callback.message)
    elif callback.data.startswith("subscription_"):
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        subscription_data = callback.data.split("_")
        subscription_id = subscription_data[1]
        subscription_info(callback.message, subscription_id)
    elif callback.data.startswith("subscriptionlink_"):
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        subscription_data = callback.data.split("_")
        region = subscription_data[1]
        token = subscription_data[2]
        subscription_id = subscription_data[3]
        subscriptionlink_copy(callback.message, region, token, subscription_id)
    elif callback.data.startswith("subscriptionqr_"):
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        subscription_data = callback.data.split("_")
        region = subscription_data[1]
        token = subscription_data[2]
        subscription_id = subscription_data[3]
        subscriptionqr_image(callback.message, region, token, subscription_id)
    elif callback.data == 'add_new_subscription':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        new_subscription_list(callback.message)
    elif callback.data.startswith("new_subscription_info_"):
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        subscription_data = callback.data.split("_")
        subscription_id = subscription_data[3]
        new_subscription_info(callback.message, subscription_id)
    elif callback.data.startswith("purchase_subscription_"):
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        subscription_data = callback.data.split("_")
        subscription_id = subscription_data[2]
        period = subscription_data[3]
        purchase_subscription(callback.message, subscription_id, period)
    elif callback.data.startswith("unsubscribe_"):
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        subscription_data = callback.data.split("_")
        subscription_id = subscription_data[1]
        unsubscribe(callback.message, subscription_id)
    elif callback.data.startswith("remove_subscription_"):
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        subscription_data = callback.data.split("_")
        subscription_id = subscription_data[2]
        remove_subscription(callback.message, subscription_id)

def get_user_id(message):
    # Get billing user ID from database
    chat_id = message.chat.id
    sql = 'SELECT id FROM users WHERE chat_id = %s'
    val = (chat_id,)
    cursor = db.cursor()
    cursor.execute(sql, val)
    result = cursor.fetchall()
    cursor.close()
    billing_user_id = result[0][0]
    return billing_user_id

def get_user_subscriptions(bill_user_id):
    # Get all user subscriptions from billing
    sql = 'SELECT tok.id, tok.token, tar.name, tar.region, tok.end_date, tok.is_active FROM tokens tok JOIN tariffs tar ON tok.tariff_id = tar.id WHERE user_id = %s'
    val = (bill_user_id,)
    cursor = db.cursor()
    cursor.execute(sql, val)
    result = cursor.fetchall()
    cursor.close()
    subscription = result
    return subscription

def get_subscription(subscription_id):
    # Get information about subscription from billing
    sql = 'SELECT tok.id, tok.token, tar.name, tar.region, tok.end_date, tok.is_active, tar.cost FROM tokens tok JOIN tariffs tar ON tok.tariff_id = tar.id WHERE tok.id = %s'
    val = (subscription_id,)
    cursor = db.cursor()
    cursor.execute(sql, val)
    result = cursor.fetchall()
    cursor.close()
    return result

def get_all_subscriptions():
    # Get all available subscriptions from billing (all tariffs)
    sql = 'SELECT id, name, period, region, cost FROM tariffs'
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    return result

def get_new_subscription_info(subscription_id):
    # Get new subscription info from billing (tariff info)
    sql = 'SELECT id, name, period, region, cost FROM tariffs WHERE id = %s'
    val = (subscription_id,)
    cursor = db.cursor()
    cursor.execute(sql, val)
    result = cursor.fetchall()
    cursor.close()
    return result

def purchase_subscription(message, subscription_id, period):
    # Add subscription to user
    user_id = get_user_id(message)
    tariff_id = subscription_id
    token = generate_token()
    start_date = int(time.time())
    period_seconds = int(period)
    end_date = start_date + period_seconds
    sql = 'INSERT INTO tokens(user_id, tariff_id, token, start_date, end_date) VALUES(%s, %s, %s, %s, %s)'
    val = (user_id, tariff_id, token, start_date, end_date)
    cursor = db.cursor()
    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    subscriptions(message)

def remove_subscription(message, subscription_id):
    # Remove user subscription
    sql = 'DELETE FROM tokens WHERE id = %s'
    val = (subscription_id,)
    cursor = db.cursor()
    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    subscriptions(message)

def get_flag_emoji(country_code):
    # Get flag emoji from region code
    country_code = country_code.upper()
    if len(country_code) != 2 or not country_code.isalpha():
        raise ValueError("Country code must be two letters (e.g., 'ru', 'us', 'fi')")
    flag_emoji = "".join(chr(ord(char) + 127397) for char in country_code)
    return flag_emoji

def generate_token(length=24):
    # Generate token
    characters = string.ascii_letters + string.digits
    token = ''.join(random.choice(characters) for _ in range(length))
    return token

def generate_qr_code(subscription_url):
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(subscription_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

################################################################
def expired_subscription_del():
    current_time = int(time.time())
    sql = "DELETE FROM tokens WHERE end_date < %s"
    cursor = db.cursor()
    cursor.execute(sql, (current_time,))
    db.commit()
    cursor.close()

def run_scheduler():
    schedule.every(5).minutes.do(expired_subscription_del)
    while True:
        schedule.run_pending()
        time.sleep(1)

scheduler_thread = Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()
################################################################

bot.polling(none_stop=True)
