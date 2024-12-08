from flask import Flask, jsonify, request
from flask_cors import CORS
import yt_dlp
import os
import re

app = Flask(__name__)

CORS(app)

# Directory where the video will be saved (temporary storage)
DOWNLOAD_DIRECTORY = "./downloads"

# Create a folder to store the downloaded videos
DOWNLOAD_FOLDER = 'C:\\\\Users\\mo5623\\Downloads\\youtube-downloader\\downloads\\'
print(DOWNLOAD_FOLDER)
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def sanitize_title(title):
    return re.sub(r'[\/:*?"<>|]', '_', title)

@app.route('/')
def home():
    return "Hello from Flask!"

@app.route('/download', methods=['POST'])
def download_video():
    try:
        # Get the JSON data from the request
        data = request.get_json()

        # Check if the 'url' field is in the JSON data
        if 'url' not in data or data['url'].strip() == '':
            return jsonify({
                "error": "No URL provided"
            }), 400

        youtube_url = data['url'].strip()
        print(f"Downloading video from: {youtube_url}")

        # Use yt-dlp to download the video
        option ={
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(option) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            file_path = os.path.join(DOWNLOAD_FOLDER, f"{sanitize_title(info['title'])}.mp3")
            print(file_path)

        return jsonify({
            "file_path": file_path
        }), 200
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)