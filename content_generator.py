import os

import openai
import json
from youtube_transcript_api import YouTubeTranscriptApi
from datetime import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")
print("OPENAI KEY:", openai.api_key)
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
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                else:
                    print("DB is not a dict, resetting.")
                    return {}
        except Exception as e:
            print("Failed to load DB:", e)
            return {}
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

def sync_and_generate_summaries():
    try:
        with open("videos.json", "r", encoding="utf-8") as f:
            videos = json.load(f)
            for video in videos:
                video_id = video.get("id")
                title = video.get("title")
                date = video.get("date")
                views = video.get("views")
                result = process_video(video_id, title, date, views)
                if result:
                    print(f"✓ Summary for {video_id}: {result['summary'][:80]}")
    except Exception as e:
        print("Error in sync_and_generate_summaries:", e)

if __name__ == "__main__":
    try:
        sync_and_generate_summaries()
    except Exception as e:
        print("Error processing videos:", e)