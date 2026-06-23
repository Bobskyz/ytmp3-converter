import os
import shutil
import tempfile
import subprocess
import threading
import queue
import uuid
from flask import Flask, request, render_template, jsonify, Response, send_file, after_this_request

app = Flask(__name__)

TEMP_DIR = tempfile.mkdtemp(prefix="ytmp3_")
print(f"Temporary directory created: {TEMP_DIR}")

tasks = {}

def check_js_runtime():
    try:
        subprocess.run(['node', '--version'], capture_output=True, check=True)
        return 'node'
    except:
        try:
            subprocess.run(['deno', '--version'], capture_output=True, check=True)
            return 'deno'
        except:
            return None

def cleanup_temp_dir():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        print(f"Cleaned up temp directory: {TEMP_DIR}")

@app.route('/')
def index():
    js_runtime = check_js_runtime()
    return render_template('index.html', js_runtime=js_runtime)

@app.route('/panduan')
def panduan():
    """Mengirim file PDF panduan."""
    return send_file('Visitor Data.pdf', as_attachment=False)

@app.route('/download', methods=['POST'])
def start_download():
    url = request.form.get('url', '').strip()
    if not url:
        return jsonify({'error': 'URL tidak boleh kosong'}), 400

    quality = request.form.get('quality', '192')
    if quality not in ['128', '192', '256', '320']:
        quality = '192'

    visitor_data = request.form.get('visitor_data', '').strip()

    task_id = str(uuid.uuid4())
    log_queue = queue.Queue()
    tasks[task_id] = {
        'queue': log_queue,
        'status': 'processing',
        'file_path': None,
        'info': None,
        'error': None,
        'url': url,
        'quality': quality,
        'visitor_data': visitor_data,
    }

    thread = threading.Thread(target=run_download, args=(task_id,))
    thread.daemon = True
    thread.start()

    return jsonify({'task_id': task_id})

def run_download(task_id):
    task = tasks.get(task_id)
    if not task:
        return

    url = task['url']
    quality = task['quality']
    visitor_data = task['visitor_data']
    log_queue = task['queue']

    request_temp_dir = tempfile.mkdtemp(dir=TEMP_DIR)
    output_template = os.path.join(request_temp_dir, '%(title)s.%(ext)s')
    
    ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg')
    if os.path.exists(ffmpeg_path):
        ydl_opts['ffmpeg_location'] = ffmpeg_path

    # Bangun opsi yt-dlp
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': output_template,
        'quiet': False,
        'no_warnings': False,
        'verbose': True,
        'extract_flat': False,
        'retries': 15,
        'fragment_retries': 15,
        'throttledratelimit': 102400,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        }],
        'postprocessor_args': [
            '-ar', '44100',
            '-ac', '2',
            '-codec:a', 'libmp3lame',
            '-b:a', f'{quality}k',
        ],
    }

    # Extractor args untuk YouTube
    extractor_args = {
        'youtube': {
            'player_client': ['android', 'ios', 'web'],
            'player_js_variant': 'tv',
            'skip': ['hls', 'dash'],
            'include_empty_format': True,
        }
    }
    if visitor_data:
        extractor_args['youtube']['visitor_data'] = visitor_data

    ydl_opts['extractor_args'] = extractor_args

    # Gunakan subprocess agar bisa streaming log
    import sys
    cmd = [sys.executable, '-m', 'yt_dlp'] + [
        '--no-warnings', '--verbose',
        '--extract-audio', '--audio-format', 'mp3',
        '--audio-quality', quality,
        '--add-metadata',
        '--embed-thumbnail',
        '--output', output_template,
        '--js-runtimes', 'node',
        url
    ]
    if visitor_data:
        cmd.extend(['--extractor-args', f'youtube:visitor_data={visitor_data}'])
    cmd.extend(['--extractor-args', 'youtube:player_client=android,ios,web'])
    cmd.extend(['--extractor-args', 'youtube:player_js_variant=tv'])
    cmd.extend(['--extractor-args', 'youtube:skip=hls,dash'])
    cmd.extend(['--extractor-args', 'youtube:include_empty_format=True'])

    log_queue.put(f"Running: {' '.join(cmd)}")

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        for line in iter(process.stdout.readline, ''):
            if not line:
                break
            line = line.strip()
            if line:
                log_queue.put(line)

        process.stdout.close()
        return_code = process.wait()

        if return_code != 0:
            log_queue.put(f"ERROR: Proses gagal dengan kode {return_code}")
            task['status'] = 'error'
            task['error'] = f"Gagal dengan kode {return_code}"
            log_queue.put("DONE_ERROR")
            return

        # Cari file MP3
        mp3_files = [f for f in os.listdir(request_temp_dir) if f.endswith('.mp3')]
        if not mp3_files:
            log_queue.put("ERROR: Tidak ditemukan file MP3 setelah konversi")
            task['status'] = 'error'
            task['error'] = "File MP3 tidak ditemukan"
            log_queue.put("DONE_ERROR")
            return

        mp3_path = os.path.join(request_temp_dir, mp3_files[0])
        task['file_path'] = mp3_path
        task['info'] = {'title': os.path.splitext(mp3_files[0])[0]}
        task['status'] = 'completed'
        log_queue.put("DONE_SUCCESS")

    except Exception as e:
        log_queue.put(f"ERROR: {str(e)}")
        task['status'] = 'error'
        task['error'] = str(e)
        log_queue.put("DONE_ERROR")

@app.route('/progress/<task_id>')
def progress_stream(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': 'Task tidak ditemukan'}), 404

    def event_stream():
        q = task['queue']
        while True:
            try:
                msg = q.get(timeout=1)
            except queue.Empty:
                if task['status'] in ('completed', 'error'):
                    break
                continue
            yield f"data: {msg}\n\n"
            if msg in ('DONE_SUCCESS', 'DONE_ERROR'):
                break

    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/download_file/<task_id>')
def download_file(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': 'Task tidak ditemukan'}), 404
    if task['status'] != 'completed':
        return jsonify({'error': 'Proses belum selesai'}), 400

    mp3_path = task['file_path']
    if not mp3_path or not os.path.exists(mp3_path):
        return jsonify({'error': 'File tidak ditemukan'}), 404

    info = task['info'] or {}
    safe_title = "".join(c for c in info.get('title', 'audio') if c.isalnum() or c in (' ', '-', '_')).rstrip()
    download_name = f"{safe_title}.mp3"

    @after_this_request
    def cleanup(response):
        temp_dir = os.path.dirname(mp3_path)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        tasks.pop(task_id, None)
        return response

    return send_file(
        mp3_path,
        as_attachment=True,
        download_name=download_name,
        mimetype='audio/mpeg'
    )

import atexit
atexit.register(cleanup_temp_dir)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)