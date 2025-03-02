from flask import Flask, request, jsonify, render_template
import yt_dlp
import os
from threading import Thread

app = Flask(__name__)

# Variável global para armazenar o progresso do download
download_progress = 0

def download_video(url):
    global download_progress
    download_progress = 0

    def progress_hook(d):
        global download_progress
        if d['status'] == 'downloading':
            download_progress = d['downloaded_bytes'] / d['total_bytes'] * 100
        elif d['status'] == 'finished':
            download_progress = 100

    # Define o caminho para a pasta Downloads do usuário
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")

    options = {
        'format': 'best',  # Seleciona o melhor formato de vídeo disponível
        'outtmpl': os.path.join(downloads_path, '%(title)s.%(ext)s'),  # Salva na pasta Downloads
        'progress_hooks': [progress_hook],
    }
    
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])

@app.route('/')
def index():
    return render_template('youtube2.html')  # Serve a página HTML

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    thread = Thread(target=download_video, args=(url,))
    thread.start()
    return jsonify({'status': 'success'})

@app.route('/progress', methods=['GET'])
def progress():
    return jsonify({'progress': download_progress})

if __name__ == '__main__':
    # Execute o servidor Flask
    app.run(debug=True)