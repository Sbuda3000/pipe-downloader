from flask import Flask, jsonify, request
from flask_cors import CORS
import yt_dlp
import os
import re
import dropbox
from decouple import config 

app = Flask(__name__)

CORS(app)

# Directory where the video will be saved (temporary storage)
DOWNLOAD_DIRECTORY = "./downloads"

# Create a folder to store the downloaded videos
if not os.path.exists(DOWNLOAD_DIRECTORY):
    os.makedirs(DOWNLOAD_DIRECTORY)

def sanitize_title(title):
    return re.sub(r'[\/:*?"<>|]', '_', title)

def upload_to_dropbox(file_name, file_content):
    ACCESS_TOKEN = config('DROPBOX_ACCESS_TOKEN')
    dbx = dropbox.Dropbox(ACCESS_TOKEN)
    
    dbx.files_upload(file_content, f'/{file_name}', mute=True)
    shared_link_metadata = dbx.sharing_create_shared_link_with_settings(f'/{file_name}')
    return shared_link_metadata.url

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
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(option) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            file_name = f"{sanitize_title(info['title'])}.mp3"
            file_path = f"{sanitize_title(info['title'])}.mp3"

        # Read the downloaded file into memory
        with open(file_path, 'rb') as f:
            file_content = f.read()

        # Upload the downloaded file to Dropbox
        dropbox_url = upload_to_dropbox(file_name, file_content)

        return jsonify({
            "file_path": file_path,
            "dropbox_url": dropbox_url
        }), 200
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)