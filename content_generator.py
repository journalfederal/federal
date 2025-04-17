import os
from dotenv import load_dotenv
load_dotenv()

import openai
import json
from youtube_transcript_api import YouTubeTranscriptApi
from datetime import datetime

print("OPENAI KEY:", openai.api_key)

openai.api_key = os.getenv("OPENAI_API_KEY")
DB_PATH = "summaries.json"

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t["text"] for t in transcript])
    except Exception as e:
        print(f"Transcript error: {e}")
        return None

def generate_summary(transcript):
    prompt = f"""
    Below is a YouTube transcript. Convert it into a professional, neutral-tone news article (around 3 concise paragraphs).

    Transcript:
    {transcript}

    News article:
    """
    try:
        res = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI Error:", e)
        return "Failed to summarize."

def load_db():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def process_video(video_id, title, date, views):
    db = load_db()
    if video_id in db:
        return db[video_id]
    transcript = get_transcript(video_id)
    print("Transcript fetched:", transcript[:100])
    if not transcript:
        return None
    summary = generate_summary(transcript)
    print("Generated summary:", summary[:100])
    video_data = {
        "id": video_id,
        "title": title,
        "date": date,
        "views": views,
        "summary": summary
    }
    db[video_id] = video_data
    save_db(db)
    return video_data

def get_all_videos():
    return list(load_db().values())

if __name__ == "__main__":
    test = process_video("dQw4w9WgXcQ", "Fed Faiz Artırım Kararı", "2025-04-17", "125456")
    print("✓ Test summary written:", test["summary"][:100])