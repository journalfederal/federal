from flask import Flask, jsonify, send_file
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
import sqlite3

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

app = Flask(__name__)

@app.route('/')
def home():
    return send_file('journal-federal.html')

CORS(app)

@app.route('/api/channel-stats')
def get_channel_stats():
    api_key = os.getenv("YOUTUBE_API_KEY")
    channel_id = "UC5HDiPPo2O_y2LLAjh_o6wQ"
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if 'items' in data and data['items']:
        stats = data['items'][0]['statistics']
        return jsonify({
            "subscribers": stats.get("subscriberCount", "0"),
            "views": stats.get("viewCount", "0"),
            "videos": stats.get("videoCount", "0")
        })
    else:
        return jsonify({"error": "Data not found"}), 404

@app.route('/logo.png')
def logo():
    return send_file('logo.png', mimetype='image/png')

@app.route('/journal.png')
def journal_image():
    return send_file('journal.png', mimetype='image/png')

@app.route('/api/videos')
def get_videos():
    conn = sqlite3.connect("summaries.db")
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS summaries (video_id TEXT PRIMARY KEY, title TEXT, date TEXT, views TEXT, summary TEXT)")
    summaries = {row[0]: {"summary": row[4]} for row in c.execute("SELECT * FROM summaries")}

    api_key = os.getenv("YOUTUBE_API_KEY")
    channel_id = "UC5HDiPPo2O_y2LLAjh_o6wQ"
    url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=6&type=video"

    response = requests.get(url)
    data = response.json()

    videos = []
    for item in data.get("items", []):
        if "videoId" in item["id"]:
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            description = snippet["description"]
            excerpt = description[:300] + ("..." if len(description) > 300 else "")
            videos.append({
                "title": snippet["title"],
                "excerpt": excerpt
            })

    conn.close()
    return jsonify(videos)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)