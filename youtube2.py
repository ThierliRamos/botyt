from flask import Blueprint, request, jsonify, render_template, send_file
import yt_dlp
import os
from threading import Thread
from urllib.parse import urlparse, parse_qs

# Criação da Blueprint
youtube2_app = Blueprint('youtube2', __name__)

download_progress = 0

def download_video(url, output_file):
    global download_progress
    download_progress = 0

    def progress_hook(d):
        global download_progress
        if d['status'] == 'downloading':
            download_progress = d['downloaded_bytes'] / d['total_bytes'] * 100
        elif d['status'] == 'finished':
            download_progress = 100

    options = {
        'format': 'bestaudio/best',  # Seleciona o melhor áudio disponível
        'outtmpl': output_file,       # Especifica o caminho do arquivo de saída
        'cookiefile': 'cookies/cookies.txt',  # Caminho para o arquivo de cookies
        'progress_hooks': [progress_hook],    # Função de callback para acompanhar o progresso do download
    }

    try:
        print(f"Iniciando download: {url}")  # Log de início do download
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
            print(f"Download concluído: {output_file}")  # Log após conclusão do download
    except Exception as e:
        print(f"Erro ao baixar o vídeo: {e}")  # Log de erro
        return False
    return True

@youtube2_app.route('/')
def index():
    return render_template('youtube2.html')

@youtube2_app.route('/download_video', methods=['POST'])
def download_video_route():
    url = request.form['url']

    # Validação da URL
    if "youtube.com" not in url and "youtu.be" not in url:
        return jsonify({'status': 'error', 'message': 'URL inválida!'}), 400

    # Extrair o ID do vídeo
    parsed_url = urlparse(url)
    if "youtube.com" in url:
        video_id = parse_qs(parsed_url.query).get('v', [None])[0]
    else:
        video_id = parsed_url.path.split('/')[-1]  # Para youtu.be

    if not video_id:
        return jsonify({'status': 'error', 'message': 'ID do vídeo não encontrado!'}), 400

    # Definindo o caminho para um arquivo temporário
    output_file_path = f"/tmp/{video_id}.mp3"  # Usar um diretório temporário para áudio

    print(f"Iniciando download do áudio: {url} para {output_file_path}")  # Log de depuração

    # Iniciar o download em um thread
    thread = Thread(target=download_video, args=(url, output_file_path))
    thread.start()

    # Esperar o download terminar
    thread.join()  # Aguarda o término do download

    # Verificar se o arquivo foi criado antes de tentar enviá-lo
    if not os.path.exists(output_file_path):
        print(f"Arquivo não encontrado: {output_file_path}")  # Log de erro
        return jsonify({'status': 'error', 'message': 'O arquivo não foi criado.'}), 500

    # Retornar o arquivo para download
    return send_file(output_file_path, as_attachment=True, download_name=f"{video_id}.mp3", mimetype='audio/mpeg')

@youtube2_app.route('/progress', methods=['GET'])
def progress():
    return jsonify({'progress': download_progress})
