import os
import sqlite3

import openai
import json
from youtube_transcript_api import YouTubeTranscriptApi
from datetime import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")
print("OPENAI KEY:", openai.api_key)
DB_PATH = "summaries.db"

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

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS summaries (
            video_id TEXT PRIMARY KEY,
            title TEXT,
            date TEXT,
            views TEXT,
            summary TEXT
        )
    """)
    conn.commit()
    conn.close()

def load_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT video_id, title, date, views, summary FROM summaries")
    rows = c.fetchall()
    conn.close()
    return {row[0]: {
        "id": row[0],
        "title": row[1],
        "date": row[2],
        "views": row[3],
        "summary": row[4]
    } for row in rows}

def save_entry(video_data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO summaries (video_id, title, date, views, summary)
        VALUES (?, ?, ?, ?, ?)
    """, (video_data["id"], video_data["title"], video_data["date"], video_data["views"], video_data["summary"]))
    conn.commit()
    conn.close()

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
    save_entry(video_data)
    return video_data

def get_all_videos():
    return list(load_db().values())

def sync_and_generate_summaries():
    try:
        with open("videos.json", "r", encoding="utf-8") as f:
            videos = json.load(f)
            init_db()
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
    init_db()
    try:
        sync_and_generate_summaries()
    except Exception as e:
        print("Error processing videos:", e)

def generate_summary_for_video(video):
    video_id = video.get("id")
    title = video.get("title")
    date = video.get("date")
    views = video.get("views")
    return process_video(video_id, title, date, views)