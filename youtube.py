from flask import Blueprint, request, jsonify, render_template, send_file
import yt_dlp
import os
from threading import Thread
import time
from urllib.parse import urlparse, parse_qs

# Criação da Blueprint
youtube_app = Blueprint('youtube', __name__)

download_progress = 0

def download_audio(url, output_file):
    global download_progress
    download_progress = 0

    def progress_hook(d):
        global download_progress
        if d['status'] == 'downloading':
            download_progress = d['downloaded_bytes'] / d['total_bytes'] * 100
        elif d['status'] == 'finished':
            download_progress = 100

    options = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': output_file,
        'cookiefile': '/opt/render/project/src/cookies/cookies.txt',  # Verifique se este caminho está correto
        'progress_hooks': [progress_hook],
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
    except Exception as e:
        return str(e)  # Retorne a mensagem de erro se necessário

@youtube_app.route('/')
def index():
    return render_template('youtube.html')

@youtube_app.route('/download_audio', methods=['POST'])
def download_audio_route():
    url = request.form['url']
    
    # Validação da URL
    if "youtube.com" not in url and "youtu.be" not in url:
        return jsonify({'status': 'error', 'message': 'URL inválida!'}), 400
    
    # Extraindo o ID do vídeo
    parsed_url = urlparse(url)
    video_id = parse_qs(parsed_url.query).get('v', [None])[0]
    if not video_id:
        return jsonify({'status': 'error', 'message': 'ID do vídeo não encontrado!'}), 400

    output_file_path = os.path.join(os.path.expanduser("~"), "Downloads", f"{video_id}.mp3")
    
    # Inicie o download em uma thread
    thread = Thread(target=download_audio, args=(url, output_file_path))
    thread.start()

    # Aguarde o download concluir antes de enviar o arquivo
    while not os.path.exists(output_file_path):
        time.sleep(1)  # Espera que o arquivo seja criado

    # Retornar o arquivo para download
    return send_file(output_file_path, as_attachment=True)

@youtube_app.route('/progress', methods=['GET'])
def progress():
    return jsonify({'progress': download_progress})
