from flask import Flask, render_template, request
import os
import requests
import re

app = Flask(__name__)

@app.route('/')
def youtube():
    return render_template('youtube.html', message=None)

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    try:
        id_video = extrair_id_video(url)
        if not id_video:
            message = "Link inválido!"
            return render_template('youtube.html', message=message)

        # Baixar o áudio usando a API do RapidAPI
        audio_url = f"https://youtube-mp3-audio-video-downloader.p.rapidapi.com/download-mp3/{id_video}"
        headers = {
            "x-rapidapi-key": "99bb57d209mshb6ca809dc147a3ep1a51e7jsnf829ae92aef6",  # Chave da API hardcoded
            "x-rapidapi-host": "youtube-mp3-audio-video-downloader.p.rapidapi.com"
        }
        resposta = requests.get(audio_url, headers=headers)

        if resposta.status_code == 200:
            file_path = f'downloads/{id_video}.mp3'
            with open(file_path, 'wb') as f:
                f.write(resposta.content)

            message = "Música baixada com sucesso!"
            return render_template('youtube.html', message=message)
        else:
            message = f"Erro ao baixar a música! Código de resposta: {resposta.status_code}"
            return render_template('youtube.html', message=message)

    except Exception as e:
        message = str(e)
        return render_template('youtube.html', message=message)

def extrair_id_video(url):
    regex = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^&\n]{11})'
    match = re.search(regex, url)
    return match.group(1) if match else None

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True)
