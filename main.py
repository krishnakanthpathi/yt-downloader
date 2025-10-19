from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app) 

# ✅ Route to get direct video link
@app.route('/get_direct_link', methods=['POST'])
def get_direct_link():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        ydl_opts = {"quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # ✅ Get the best quality download URL
            formats = info.get("formats", [])
            direct_url = None

            for f in formats[::-1]:  # Try best quality first
                if f.get("url"):
                    direct_url = f["url"]
                    break

            if not direct_url:
                return jsonify({"error": "Could not fetch direct URL"}), 500

            return jsonify({"direct_download_url": direct_url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8000))  
    app.run(host="0.0.0.0", port=port, debug=True)