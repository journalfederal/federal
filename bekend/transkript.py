from flask import Flask, request, jsonify, send_file
from google.cloud import speech_v1p1beta1 as speech
import os
import uuid
from srt_olustur import json_to_srt

app = Flask(__name__)

# Google API credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

UPLOAD_FOLDER = "uploads"
SRT_FOLDER = "srt"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SRT_FOLDER, exist_ok=True)

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "file" not in request.files:
        return jsonify({"error": "Dosya bulunamadı"}), 400

    file = request.files["file"]
    filename = f"{uuid.uuid4()}.wav"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    client = speech.SpeechClient()

    with open(filepath, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="tr-TR",
        enable_word_time_offsets=True,
        enable_automatic_punctuation=True,
    )

    response = client.recognize(config=config, audio=audio)

    srt_content = json_to_srt(response)
    srt_filename = f"{uuid.uuid4()}.srt"
    srt_path = os.path.join(SRT_FOLDER, srt_filename)

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    return send_file(srt_path, as_attachment=True, download_name="transkript.srt")


if __name__ == "__main__":
    app.run(debug=True, port=5001)