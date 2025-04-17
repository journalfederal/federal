from flask import Flask, jsonify, send_file
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv
import requests
from content_generator import process_video

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

app = Flask(__name__)

@app.route('/')
def home():
    return send_file('journal-federal.html')

CORS(app)

@app.route('/api/transcript/<video_id>', methods=['GET'])
def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        full_text = ' '.join([line['text'] for line in transcript])
        return jsonify({
            'channel_id': 'UC5HDiPPo2O_y2LLAjh_o6wQ',
            'transcript': full_text
        })
    except Exception as e:
        return jsonify({'error': f'Could not retrieve transcript: {str(e)}'}), 404

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
    import json
    with open('summaries.json', 'r') as f:
        summaries = json.load(f)
        if isinstance(summaries, list):
            summaries = {}
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
            videos.append({
                "id": video_id,
                "title": snippet["title"],
                "thumbnail": snippet["thumbnails"]["high"]["url"],
                "views": "0",
                "date": snippet["publishedAt"][:10],
                "excerpt": snippet["description"][:150] + "...",
            "fullContent": summaries.get(video_id, {}).get("summary", "Your full article text goes here...")
            })

    return jsonify(videos)

@app.route('/api/sync-videos')
def sync_videos():
    process_video()
    return jsonify({"message": "Video content synced successfully."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)