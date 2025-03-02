from flask import Flask, request, jsonify, render_template
import yt_dlp
import os
from threading import Thread

app = Flask(__name__)

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

    # Define o caminho para a pasta Downloads do usuário
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")

    options = {
        'format': 'bestaudio/best',  # Seleciona o melhor formato de áudio disponível
        'extractaudio': True,         # Extrai somente o áudio do vídeo
        'audioformat': 'mp3',         # Formato do áudio
        'outtmpl': os.path.join(downloads_path, '%(title)s.%(ext)s'),  # Salva na pasta Downloads
        'progress_hooks': [progress_hook],
    }
    
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])

@app.route('/')
def index():
    return render_template('youtube.html')  # Serve a página HTML

@app.route('/download_audio', methods=['POST'])
def download_audio_route():
    print("Rota /download_audio chamada")  # Adicionada para debugging
    url = request.form['url']
    # Validação da URL
    if "youtube.com" not in url and "youtu.be" not in url:
        return jsonify({'status': 'error', 'message': 'URL inválida!'}), 400
    
    try:
        thread = Thread(target=download_audio, args=(url,))
        thread.start()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Erro ao iniciar o download: {e}")  # Log do erro no console do servidor
        return jsonify({'status': 'error', 'message': 'Erro ao iniciar o download.'}), 500

@app.route('/progress', methods=['GET'])
def progress():
    return jsonify({'progress': download_progress})

if __name__ == '__main__':
    # Execute o servidor Flask
    app.run(debug=True)
