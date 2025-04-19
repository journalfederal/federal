from flask import Flask, render_template, request, redirect, url_for, render_template_string

cmd = [
    "yt-dlp",
    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
    "-o", downloaded_path,
    youtube_url
]

result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print("FFmpeg çıktı:", result.stderr)