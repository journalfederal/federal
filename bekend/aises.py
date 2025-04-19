import requests

ELEVEN_API_KEY = "sk_6b7fe69757c063d70ba55e99dbf336cea0eb9ad2e6da4a5e"

def generate_speech(text, voice="VR6AewLTigWG4xSOukaG"):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/stream"
    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.5,
            "use_speaker_boost": True
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.content
    else:
        print("ElevenLabs API Hatası:", response.status_code, response.text)
        raise Exception(f"Seslendirme başarısız oldu: {response.status_code}\n{response.text}")