from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from pytube import YouTube
import os
import threading

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['STATIC_PATH'] = 'YT_scrape/static'

downloads = {}

def download_video(url, thread_id):
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        filename = os.path.join(app.config['STATIC_PATH'], 'downloaded_video.mp4')
        os.makedirs(app.config['STATIC_PATH'], exist_ok=True)
        stream.download(output_path=app.config['STATIC_PATH'], filename='downloaded_video.mp4')
        downloads[thread_id] = yt.title
    except Exception as e:
        print(f"Error downloading video: {e}")
        downloads[thread_id] = None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        if url:
            thread_id = threading.get_ident()
            threading.Thread(target=download_video, args=(url, thread_id)).start()
            return jsonify({'status': 'loading', 'thread_id': thread_id})
    return render_template('index.html')

@app.route('/check_status/<int:thread_id>')
def check_status(thread_id):
    if thread_id in downloads:
        title = downloads.pop(thread_id)
        if title:
            return jsonify({'status': 'complete', 'title': title})
        else:
            return jsonify({'status': 'error'})
    return jsonify({'status': 'loading'})

@app.route('/download_complete')
def download_complete():
    title = request.args.get('title')
    return render_template('download_complete.html', title=title)

if __name__ == '__main__':
    app.run(debug=True)
