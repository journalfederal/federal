from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import subprocess
import os

app = Flask(__name__)
CORS(app)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route("/kes-ve-indir", methods=["POST"])
def kes_ve_indir():
    print("✅ /kes-ve-indir endpoint'e istek geldi")
    data = request.get_json()
    output_name = data.get("outputName", "").strip()
    if not output_name:
        return jsonify({"error": "Dosya adı verilmedi!"}), 400
    url = data.get("url")
    start = int(data.get("start", 0))
    end = int(data.get("end", 0))

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
        print("✂️  yt-dlp doğrudan kesmeye başlıyor...")
        duration_section = f"*{start}-{end}"
        clipped_path = os.path.join(DOWNLOAD_DIR, f"{output_name}.mp4")

        cmd = [
            "yt-dlp",
            "--download-sections", duration_section,
            "-f", "mp4",
            "-o", clipped_path,
            url
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("yt-dlp çıktı:", result.stderr)
    except Exception as e:
        return jsonify({"error": f"yt-dlp kesme hatası: {str(e)}"}), 500

    print("✅ yt-dlp kesimi tamamlandı:", clipped_path)
    print("📦 Dosya gönderiliyor...")
    return send_file(clipped_path, as_attachment=True, download_name=f"{output_name}.mp4")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
