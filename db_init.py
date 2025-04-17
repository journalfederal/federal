import sqlite3

def process_video(video_id, title, date, views):
    print(f"Processing: {title} ({video_id})")
    transcript = get_transcript(video_id)
    print("Transcript fetched:", transcript[:100])

    if not transcript:
        print("Transcript is empty.")
        return None

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes YouTube transcripts into articles."},
                {"role": "user", "content": f"Summarize this transcript:\n{transcript}"}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        summary = response.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI Error:", e)
        return None

    print("Generated summary:", summary[:100])

    conn = sqlite3.connect("summaries.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO summaries (video_id, summary) VALUES (?, ?)", (video_id, summary))
    conn.commit()
    conn.close()

    return {
        "id": video_id,
        "title": title,
        "date": date,
        "views": views,
        "summary": summary
    }