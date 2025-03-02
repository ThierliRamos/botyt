from flask import Blueprint, request, jsonify, render_template
import yt_dlp
import os
from threading import Thread
from urllib.parse import urlparse, parse_qs

# Criação da Blueprint
youtube2_app = Blueprint('youtube2', __name__)

download_progress = 0

def download_video(url, output_file, format):
    global download_progress
    download_progress = 0

    def progress_hook(d):
        global download_progress
        if d['status'] == 'downloading':
            download_progress = d['downloaded_bytes'] / d['total_bytes'] * 100
        elif d['status'] == 'finished':
            download_progress = 100

    # Caminho fixo para o arquivo de cookies
    cookies_file = 'cookies/cookies'

    options = {
        'format': format,
        'outtmpl': output_file,
        'progress_hooks': [progress_hook],
        'cookiefile': 'cookies/cookies.txt',  # Verifique se este caminho está correto
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"Erro: {e}")

@youtube2_app.route('/')
def index():
    return render_template('youtube2.html')

@youtube2_app.route('/download_video', methods=['POST'])
def download_video_route():
    url = request.form['url']
    format = request.form['format']  # Obtém o formato enviado pelo formulário

    # Validação da URL
    if "youtube.com" not in url and "youtu.be" not in url:
        return jsonify({'status': 'error', 'message': 'URL inválida!'}), 400
    
    # Configuração do caminho de download
    parsed_url = urlparse(url)
    video_id = parse_qs(parsed_url.query).get('v', [None])[0]
    if not video_id:
        return jsonify({'status': 'error', 'message': 'ID do vídeo não encontrado!'}), 400

    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    output_file_path = os.path.join(downloads_path, f"{video_id}.mp4")  # Altere a extensão conforme necessário

    thread = Thread(target=download_video, args=(url, output_file_path, format))
    thread.start()

    return jsonify({'status': 'success'})

@youtube2_app.route('/progress', methods=['GET'])
def progress():
    return jsonify({'progress': download_progress})
