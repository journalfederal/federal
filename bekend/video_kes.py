from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import shutil
print("🧪 yt-dlp PATH kontrolü:", shutil.which("yt-dlp"))
import subprocess
import os
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)
CORS(app)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def extract_youtube_id(url):
    query = urlparse(url)
    if "youtube" in query.netloc:
        return parse_qs(query.query).get("v", [None])[0]
    if "youtu.be" in query.netloc:
        return query.path.lstrip("/")
    return None

def parse_time(t):
    if isinstance(t, str) and ":" in t:
        parts = list(map(int, t.split(":")))
        return sum(x * 60**i for i, x in enumerate(reversed(parts)))
    return int(t)

@app.route("/kes-ve-indir", methods=["POST"])
def kes_ve_indir():
    print("✅ /kes-ve-indir endpoint'e istek geldi")
    print("🍪 Cookies dosyası mevcut mu?", os.path.exists("cookies.txt"))
    data = request.get_json()
    output_name = data.get("outputName", "").strip()
    if not output_name:
        return jsonify({"error": "Dosya adı verilmedi!"}), 400
    url = data.get("url")
    
    start = parse_time(data.get("start", 0))
    end = parse_time(data.get("end", 0))

    print(f"🎯 URL: {url}")
    print(f"⏱️  Başlangıç: {start}, Bitiş: {end}")

    if not url or end <= start:
        return jsonify({"error": "Geçersiz veri"}), 400

    # Unique filenames
    download_template = os.path.join(DOWNLOAD_DIR, f"{output_name}.%(ext)s")
    clipped_path = os.path.join(DOWNLOAD_DIR, f"{output_name}.mp4")

    # Download full video
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
        "outtmpl": download_template,
        "quiet": True,
    }

    try:
        print("🔽 Video indiriliyor...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_path = ydl.prepare_filename(info)
    except Exception as e:
        return jsonify({"error": f"Video indirilemedi: {str(e)}"}), 500

    if not os.path.exists(downloaded_path):
        return jsonify({"error": "Video indirildi ama dosya bulunamadı!"}), 500

    print("✅ Video indirildi:", downloaded_path)

    # yt-dlp kesme
    try:
        print("✂️  yt-dlp Python API ile kesmeye başlıyor...")
        duration_section = f"*{start}-{end}"
        clip_opts = {
            "format": "bestvideo+bestaudio",
            "download_sections": [duration_section],
            "merge_output_format": "mp4",
            "outtmpl": clipped_path,
            "cookies": "cookies.txt",
            "quiet": True
        }
        with yt_dlp.YoutubeDL(clip_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        return jsonify({"error": f"yt-dlp kesme hatası: {str(e)}"}), 500

    if not os.path.exists(clipped_path) or os.path.getsize(clipped_path) < 1024:
        return jsonify({"error": "Video kesilemedi ya da boş çıktı!"}), 500

    print("✅ yt-dlp kesimi tamamlandı:", clipped_path)
    video_id = extract_youtube_id(url)
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    return jsonify({
        "success": True,
        "video_path": clipped_path,
        "download_name": f"{output_name}.mp4",
        "thumbnail": thumbnail_url
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
