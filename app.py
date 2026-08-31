import os
import imageio_ffmpeg
from flask import Flask, request, send_file, render_template_string
from yt_dlp import YoutubeDL

# ⚠️ gunicornが最初に見つける Flask の本体定義
app = Flask(__name__)

DOWNLOAD_DIR = "/tmp"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>YouTube Downloader</title>
    <style>
        body { font-family: sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; text-align: center; }
        .card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        input { width: 90%; padding: 12px; margin-bottom: 20px; font-size: 16px; }
        button { width: 95%; padding: 12px; background: #ff0000; color: white; border: none; font-size: 16px; font-weight: bold; cursor: pointer; }
        .loading { display: none; margin-top: 20px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>YouTube 720p 保存</h2>
        <!-- ⚠️ 明示的に同じドメイン内の /download 窓口を指定 -->
        <form action="/download" method="POST" onsubmit="document.getElementById('loading').style.display='block'">
            <input type="text" name="url" placeholder="YouTubeの動画URLを貼り付け" required><br>
            <button type="submit">MP4でダウンロード</button>
        </form>
        <div id="loading" class="loading">⏳ 動画を処理中...<br>（数分かかる場合があります）</div>
    </div>
</body>
</html>
"""

# ① トップ画面の窓口（確実に届くように固定）
@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML)

# ② データを受け取るダウンロード窓口（確実に届くように固定）
@app.route('/download', methods=['POST'])
def download():
    video_url = request.form.get('url')
    if not video_url:
        return "URLが空です", 400

    ydl_opts = {
        'format': 'bestvideo[height=720][ext=mp4]+bestaudio[ext=m4a]/best[height=720]',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            filepath = os.path.splitext(filename) + ".mp4"
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return f"エラーが発生しました: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
