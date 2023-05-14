import os
import pytube
import moviepy.editor as mp
import telebot
import threading
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'hello'])
def download_video(update):
    bot.reply_to(update, 'Hello there!')

@bot.message_handler(commands=['video'])
def handle_video_command(message):
    try:
        url = message.text.split(' ', 1)[1]
        threading.Thread(target=download_video_thread, args=(message, url)).start()
    except IndexError:
        bot.reply_to(message, 'Invalid command. Please provide a valid YouTube video URL.')

def download_video_thread(message, url):
    try:
        bot.reply_to(message, 'Starting to download: ' + url)
        youtube = pytube.YouTube(url)
        video = youtube.streams.get_highest_resolution()
        video_folder = create_folder('video')
        date_folder = create_date_folder(video_folder)
        video_filename = video.default_filename
        video_path = os.path.join(date_folder, video_filename)
        video.download(output_path=date_folder, filename=video_filename)
        with open(video_path, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file)
        bot.reply_to(message, 'Video downloaded successfully')
    except pytube.exceptions.PytubeError:
        bot.reply_to(message, 'Failed to download the video. Please try again.')

def create_folder(folder_name):
    folder_path = os.path.join(os.getcwd(), folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def create_date_folder(parent_folder):
    date_folder_name = datetime.now().strftime("%d %b %Y")
    date_folder_path = os.path.join(parent_folder, date_folder_name)
    if not os.path.exists(date_folder_path):
        os.makedirs(date_folder_path)
    return date_folder_path

@bot.message_handler(commands=['audio'])
def handle_audio_command(message):
    try:
        url = message.text.split(' ', 1)[1]
        threading.Thread(target=convert_audio_thread, args=(message, url)).start()
    except IndexError:
        bot.reply_to(message, 'Invalid command. Please provide a valid YouTube video URL.')

def convert_audio_thread(message, url):
    try:
        bot.reply_to(message, 'Starting to convert to audio: ' + url)
        youtube = pytube.YouTube(url)
        video = youtube.streams.get_highest_resolution()
        video_folder = create_folder('audio')
        date_folder = create_date_folder(video_folder)
        video_filename = video.default_filename
        video_path = os.path.join(date_folder, video_filename)
        audio_filename = re.sub(r'[^A-Za-z]', '', youtube.title) + '.mp3'
        audio_path = os.path.join(date_folder, audio_filename)
        video.download(output_path=date_folder, filename=video_filename)
        clip = mp.AudioFileClip(video_path)
        clip.write_audiofile(audio_path, bitrate='320k')
        os.remove(video_path)
        with open(audio_path, 'rb') as audio_file:
            bot.send_audio(message.chat.id, audio_file)
        #os.remove(audio_path)
        bot.reply_to(message, 'Audio conversion completed successfully')
    except (pytube.exceptions.PytubeError, OSError, IOError):
        bot.reply_to(message, 'Failed to convert audio. Please try again.')

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, 'Invalid command.')

bot.polling()