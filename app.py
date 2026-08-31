import os
from flask import Flask, render_template_string, request, send_file
from yt_dlp import YoutubeDL

app = Flask(__name__)
DOWNLOAD_DIR = "/tmp"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Downloader</title>
    <style>
        body { font-family: sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; text-align: center; background: #f8f9fa; }
        .card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        input[type="text"] { width: 90%; padding: 12px; margin-bottom: 20px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
        button { width: 95%; padding: 12px; cursor: pointer; background: #ff0000; color: white; border: none; border-radius: 4px; font-size: 16px; font-weight: bold; }
        button:hover { background: #cc0000; }
        .loading { display: none; margin-top: 20px; color: #555; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>YouTube 720p 保存</h2>
        <form action="/download" method="POST" onsubmit="showLoading()">
            <input type="text" name="url" placeholder="YouTubeの動画URLを貼り付け" required><br>
            <button type="submit">MP4でダウンロード</button>
        </form>
        <div id="loading" class="loading">⏳ 動画を処理中...<br>（数分かかる場合があります）</div>
    </div>
    <script>
        function showLoading() { document.getElementById('loading').style.display = 'block'; }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form.get('url')
    if not video_url:
        return "URLが空です", 400

    ydl_opts = {
        'format': 'bestvideo[height=720][ext=mp4]+bestaudio[ext=m4a]/best[height=720]',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'prefer_ffmpeg': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            filepath = os.path.splitext(filename)[0] + ".mp4"

        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return f"エラーが発生しました: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
