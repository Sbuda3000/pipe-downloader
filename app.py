from decouple import config 
from flask import Flask, jsonify, redirect, request, session
from flask_cors import CORS
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

import base64
import dropbox
import re
import yt_dlp


app = Flask(__name__)

CORS(app)

def sanitize_title(title):
    return re.sub(r'[\/:*?"<>|]', '_', title)

def upload_to_dropbox(file_name, file_content):
    ACCESS_TOKEN = config('DROPBOX_ACCESS_TOKEN')
    dbx = dropbox.Dropbox(ACCESS_TOKEN)
    
    dbx.files_upload(file_content, f'/{file_name}', mute=True)
    shared_link_metadata = dbx.sharing_create_shared_link_with_settings(f'/{file_name}')
    return shared_link_metadata.url

def write_base64_to_file(base64_string, file_name):
    with open(file_name, 'wb') as file:
        file.write(base64.b64decode(base64_string))

@app.route('/')
def home():
    return "Welcome to PIPE DOWNLOADER API"

@app.route('/authorize')
def authorize():
    client_secrets_base64 = config('CLIENT_SECRETS_BASE64')
    write_base64_to_file(client_secrets_base64, 'client_secrets.json')

    flow = Flow.from_client_secrets_file(
        'client_secrets.json',
        scopes=['https://www.googleapis.com/auth/youtube.readonly'],
        redirect_uri='http://localhost:5000/oauth2callback'
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(
        'client_secrets.json',
        scopes=['https://www.googleapis.com/auth/youtube.readonly'],
        state=state,
        redirect_uri='http://localhost:5000/oauth2callback'
    )
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials

    with open('credentials.json', 'w') as credentials_file:
        credentials_file.write(credentials.to_json())

    return redirect('/')

@app.route('/download', methods=['POST'])
def download_video():
    try:
        client_secrets_base64 = config('CLIENT_SECRETS_BASE64')
        write_base64_to_file(client_secrets_base64, 'client_secret.json')

        credentials_base64 = config('CREDENTIALS_BASE64')
        write_base64_to_file(credentials_base64, 'credentials.json')
    
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
            'oauth2': {
                'client_secrets': config('CLIENT_SECRETS_PATH'),
                'credentials': config('CREDENTIALS_PATH'),
            }
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