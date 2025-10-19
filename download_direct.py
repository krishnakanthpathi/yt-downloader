from flask import Flask, request, Response, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/download_direct/', methods=['POST'])
def download_direct():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    # ✅ Stream best video+audio format
    ydl_opts = {
        "format": "best",
        "outtmpl": "-",  # Do not save, stream instead
    }

    def generate_stream():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            yield f"Error: {str(e)}"

    # ✅ Response as a downloadable file stream
    return Response(
        generate_stream(),
        mimetype="application/octet-stream",
        headers={
            "Content-Disposition": "attachment; filename=video.mp4"
        }
    )


if __name__ == '__main__':
    app.run(port=8000, debug=True)
