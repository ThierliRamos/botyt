from flask import Flask, request, jsonify, render_template
import yt_dlp
import os
from threading import Thread

app = Flask(__name__)

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

    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")

    options = {
        'format': 'best',
        'outtmpl': os.path.join(downloads_path, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])

@app.route('/')
def index():
    return render_template('youtube2.html')

@app.route('/download_video', methods=['POST'])
def download_video_route():
    url = request.form['url']
    # Validação da URL
    if "youtube.com" not in url and "youtu.be" not in url:
        return jsonify({'status': 'error', 'message': 'URL inválida!'}), 400
    thread = Thread(target=download_video, args=(url,))
    thread.start()
    return jsonify({'status': 'success'})

@app.route('/progress', methods=['GET'])
def progress():
    return jsonify({'progress': download_progress})

if __name__ == '__main__':
    app.run(debug=True)
