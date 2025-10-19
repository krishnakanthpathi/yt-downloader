from flask import Flask, request, jsonify
import yt_dlp
import re
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ----------------- Helper Functions -----------------

def is_valid_youtube_url(url):
    # Accept both youtube.com and youtu.be links
    pattern = r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+(&\S*)?"
    return re.match(pattern, url) is not None

def download_video(url, resolution):
    try:
        print(f"[INFO] Downloading {url} at resolution <= {resolution}")
        ydl_opts = {
            'format': f'bestvideo[height<={resolution}]+bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True, None
    except Exception as e:
        print(f"[ERROR] Download failed: {str(e)}")
        return False, str(e)

def get_video_info(url):
    try:
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
        video_info = {
            "title": info.get('title'),
            "uploader": info.get('uploader'),
            "duration": info.get('duration'),
            "views": info.get('view_count'),
            "description": info.get('description'),
            "upload_date": info.get('upload_date')
        }
        return video_info, None
    except Exception as e:
        print(f"[ERROR] Fetching video info failed: {str(e)}")
        return None, str(e)

# ----------------- Flask Routes -----------------

@app.route('/download/<int:resolution>', methods=['POST'])
def download_by_resolution(resolution):
    data = request.get_json()
    url = data.get('url')
    if not url or not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid or missing YouTube URL"}), 400
    success, error = download_video(url, resolution)
    if success:
        return jsonify({"message": f"Video downloaded successfully at <= {resolution}p"}), 200
    else:
        return jsonify({"error": error}), 500

@app.route('/video_info', methods=['POST'])
def video_info():
    data = request.get_json()
    url = data.get('url')
    if not url or not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid or missing YouTube URL"}), 400
    info, error = get_video_info(url)
    if info:
        return jsonify(info), 200
    else:
        return jsonify({"error": error}), 500

@app.route('/download_all/', methods=['POST'])
def download_all():
    data = request.get_json()
    urls = data.get('urls')
    if not urls or not isinstance(urls, list):
        return jsonify({"error": "Missing or invalid 'urls' parameter"}), 400

    results = []
    for url in urls:
        if not is_valid_youtube_url(url):
            results.append({"url": url, "error": "Invalid YouTube URL"})
            continue
        success, error = download_video(url, resolution=1080)
        if success:
            results.append({"url": url, "message": "Downloaded successfully"})
        else:
            results.append({"url": url, "error": error})

    return jsonify({"results": results}), 200

# ----------------- Run Flask App -----------------

if __name__ == '__main__':
    print("[INFO] Starting Flask server on port 8000")
    app.run(debug=True, port=8000)
