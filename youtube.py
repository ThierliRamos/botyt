from flask import Blueprint, request, jsonify, render_template
import yt_dlp
import os
from threading import Thread

# Criação da Blueprint
youtube_app = Blueprint('youtube', __name__)

# Variável global para armazenar o progresso do download
download_progress = 0

def download_audio(url):
    global download_progress
    download_progress = 0

    def progress_hook(d):
        global download_progress
        if d['status'] == 'downloading':
            download_progress = d['downloaded_bytes'] / d['total_bytes'] * 100
        elif d['status'] == 'finished':
            download_progress = 100

    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")

    options = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': os.path.join(downloads_path, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
    }
    
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])

@youtube_app.route('/')
def index():
    return render_template('youtube.html')

@youtube_app.route('/download_audio', methods=['POST'])
def download_audio_route():
    # Seu código para download
    pass
