from flask import Flask, request, send_file
from flask_cors import CORS
import tempfile
import os
import traceback
from aises import generate_speech

app = Flask(__name__)
CORS(app)

@app.route('/seslendir', methods=['POST'])
def seslendir():
    try:
        data = request.get_json()
        print("Gelen JSON:", data)
        text = data.get('text')
        voice = data.get('voice', 'arnold')
        filename = data.get('filename', 'seslendirme')

        if not text or not filename:
            return {"error": "Metin ve dosya adı gereklidir."}, 400

        audio_content = generate_speech(text, voice)

        temp_path = os.path.join(tempfile.gettempdir(), f"{filename}.mp3")
        with open(temp_path, "wb") as f:
            f.write(audio_content)

        return send_file(temp_path, mimetype="audio/mpeg", as_attachment=True)

    except Exception as e:
        print("Sunucu hatası:", str(e))
        traceback.print_exc()
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(port=5001)