import telebot
import os
import socket
import time
from time import gmtime, strftime
import datetime
import igosint
import json
import random
import instaloader

# Telegram Bot token and admin ID
token = "6473755221:AAF1zNUsOcsAnnHKDEYxpkEud3XWhIw0Qf4"
admin = "5941392968"

# Report bot token
report_token = "7140748891:AAER8n1iFArAAMlK1dUdPeAs6sRi8vK6QgU"
report = telebot.TeleBot(report_token)
bot = telebot.TeleBot(token)

# Dictionary to store the last search time for each user
last_search_time = {}
p = instaloader.Instaloader()
registered_users_file = 'registered_users.json'

# Load existing registered user data from the JSON file
try:
    with open(registered_users_file, 'r') as file:
        registered_users = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    registered_users = {}

file_path = "/storage/emulated/0/gproxy.txt"
try:
    with open(file_path, 'r') as file:
        proxies = file.readlines()
        proxies = [proxy.strip() for proxy in proxies]  # Remove trailing newline characters
        
except FileNotFoundError:
    print("Proxy file not found.")
    
def random_proxy():
    if proxies:
        return random.choice(proxies)
    else:
        print("Proxy list is empty.")
        return None
        
def save_registered_users():
    with open(registered_users_file, 'w') as file:
        json.dump(registered_users, file, indent=4)
        
def register(user):
    try:
            if hasattr(user, 'contact') and user.contact is not None and hasattr(user.contact, 'phone_number'):
                ph = user.contact.phone_number
            else:
                ph = None
            current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            registered_users[user.id] = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'register_time': current_time,
            'language_code': user.language_code,
            'chat_id': user.id,
            'phone_number': ph,
            'role': 'user',
            'status': 'active'
            }
            save_registered_users()
    except Exception as e:
        report_error(user.username, e)
        pass
            
# Function to get IP address
def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))
        ip_address = s.getsockname()[0]
    except Exception as e:
        print(f"An error occurred: {e}")
        ip_address = None
    finally:
        s.close()
    
    return ip_address

# Function to report errors
def report_error(username=None, err=None, search=None):
    ip_address = get_ip_address()
    current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    message = f"""Time : `{current_time}`\nUsername : `{username}` \nSearch : {search}```Error\n{err}```"""
    report.send_message(admin, message, parse_mode="Markdown")


def send_media(message, url):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        proxy = random_proxy()
    #    p.context._session.proxies = {'http':  proxy, 'https': proxy}
        post = instaloader.Post.from_shortcode(p.context, url.split('/')[-2])
        caption = post.caption if post.caption else ""

        if post.typename == 'GraphVideo':
            format = "video"
            durl = post.video_url
            bot.send_video(message.chat.id, durl, caption=caption)
        elif post.typename == 'GraphImage':
            format = "photo"
            durl = post.url
            bot.send_photo(message.chat.id, durl, caption=caption)
        elif post.typename == 'GraphSidecar':
            for node in post.get_sidecar_nodes():
                if node.is_video:
                    durl = node.video_url
                    bot.send_video(message.chat.id, durl, caption=caption)
                else:
                    durl = node.display_url
                    bot.send_photo(message.chat.id, durl, caption=caption)
    except Exception as e:
        bot.reply_to(message, f"Please try again after few minutes")
        report_error(message.from_user.username, e)
                                

# Command handler for /start
@bot.message_handler(commands=['start'])
def start(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing') 
        user_id = str(message.from_user.id)
        user = message.from_user
        if user_id not in registered_users:
            register(user)
        mes = "Hello! Welcome to the OSINT Bot. Use /search <username> to search for a user."
        bot.reply_to(message, mes, parse_mode="Markdown")
    except Exception as e:
        report_error(message.from_user.username, e)
        pass


@bot.message_handler(commands=['ping'])
def ping(message):
    try:
        user_id = str(message.from_user.id)
        user = message.from_user
        if user_id not in registered_users:
            register(user)
        bot.send_chat_action(message.chat.id, 'typing') 
        start_time = datetime.datetime.now()
        speed = (datetime.datetime.now() - start_time).microseconds
        result = f"Pong! Response speed: {speed}ms"
        bot.reply_to(message, result, parse_mode="Markdown")
    except Exception as e:
        report_error(message.from_user.username, e)
        pass

@bot.message_handler(commands=['hello'])
def hello(message):
    try:
        user_id = str(message.from_user.id)
        user = message.from_user
        if user_id not in registered_users:
            register(user)
        bot.send_chat_action(message.chat.id, 'typing') 
        bot.reply_to(message, "Hello! How can I assist you?")
    except Exception as e:
        report_error(message.from_user.username, e)
        pass


@bot.message_handler(commands=['menu', 'help'])
def menu(message):
    try:
        user_id = str(message.from_user.id)
        user = message.from_user
        if user_id not in registered_users:
            register(user)
        bot.send_chat_action(message.chat.id, 'typing') 
        mes = "You can use this bot to perform Instagram OSINT (Open-Source Intelligence) searches. Usage \n/search ‘username’ to get Instagram profile details\n/ping to check the ping of the bot\n/download to download Instagram post and reels"
        bot.reply_to(message, mes, parse_mode="Markdown")
    except Exception as e:
        report_error(message.from_user.username, e)
        pass


@bot.message_handler(commands=['search'])
def search(message):
    try:
        user_id = message.from_user.id
        current_time = time.time()
        user = message.from_user
        if user_id not in registered_users:
            register(user)
        # Check if user has exceeded rate limit (10 seconds)
        if user_id in last_search_time and current_time - last_search_time[user_id] < 10:
            bot.reply_to(message, "Please wait for a while before searching again.")
            return
        
        bot.send_chat_action(message.chat.id, 'typing')
        last_search_time[user_id] = current_time
        if message.text[:26].strip() == "/search@nk_insta_osint_bot":
            uname = message.text[27:].strip()
        else:
            uname = message.text[8:].strip()
        if uname:
            result = igosint.get(uname)
            
            if result[1] == "InstaloaderException":
                bot.reply_to(message, f"Please try again after few minutes also check if there is mistake in the username `{uname}` ", parse_mode="Markdown")
                report_error(message.from_user.username, result[1], uname)
                status = "falied"
            elif result[1] == "success":
                bot.send_photo(message.chat.id, result[2], caption=uname)
                bot.send_message(message.chat.id, result[3], parse_mode="Markdown")
                status = "success"
            else:
                bot.reply_to(message, "Please try again later.")
                report_error(message.from_user.username, result[1], uname)
                status = "failed"
            if user_id != int(admin):
                current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                info =  f"Time : `{current_time}`\nName : `{user.first_name} {user.last_name}`\nUsername : `{user.username}`\nUser Id : `{user.id}`\nLanguage: `{user.language_code}`\n```Osint\nUsername: {uname}\nStatus: {status}\n```"
                report.send_message(admin, info, parse_mode="Markdown")
        else:
            bot.reply_to(message, 'Please enter a valid username and try again.')
    except Exception as e:
        report_error(message.from_user.username, e, message.text[8:].strip())

@bot.message_handler(commands=['data'])
def send_file(message):
    if str(message.from_user.id) != admin:
        pass
    try:
        
        file_path = "registered_users.json"

        # Send the file
        with open(file_path, 'rb') as file:
            bot.send_document(admin, file)
        
    except Exception as e:
        bot.reply_to(message, f"Failed to send file: {str(e)}")

@bot.message_handler(commands=['download'])
def download(message):
    url = message.text
    if 'instagram.com/p/' in url or 'instagram.com/reel/' in url:
        try:
            send_media(message, url)
        except Exception as e:
            bot.reply_to(message, f"Please check the url and try again {e}")
        

# Handler for all other messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_id = str(message.from_user.id)
        user = message.from_user
        if user_id not in registered_users:
            register(user)
        # send
        url = message.text
        if 'instagram.com/p/' in url or 'instagram.com/reel/' in url:
            try:
                send_media(message, url)
            except Exception as e:
                bot.reply_to(message, f"Please check the url and try again {e}")
                
    except Exception as e:
        report_error(message.from_user.username, e)

while True:
    try:
        bot.polling(timeout=30) 
    except Exception as e:
        print(e)
        continue 
     