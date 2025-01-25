from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import yt_dlp
import os
import re

app = Flask(__name__)
progress = {'status': 'idle', 'progress': 0}

# Render the home page with the form to input the video URL and folder
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    global progress
    progress = {'status': 'idle', 'progress': 0}  # Reset progress
    video_url = request.form['video_url']
    download_folder = "downloads"

    # Ensure the download folder exists
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # yt-dlp options to fetch the best video and audio
    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',  # Download the best video and audio with height <= 1080
        'outtmpl': f'{download_folder}/%(title)s.%(ext)s',  # Save with video title
        'quiet': True,  # Suppress output except errors
        'geo_bypass': True,  # Bypass geographical restrictions
        'merge_output_format': 'mp4',  # Ensure the output format is mp4
        'progress_hooks': [progress_hook],  # Add progress hook
        'cookiefile': 'cookies.txt',  # Use cookies from cookies.txt
        'http_headers': {  # Add common headers to mimic a real browser
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.youtube.com/',  # Add Referer header
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info and download it
            info_dict = ydl.extract_info(video_url, download=True)
            print(f"Info dict: {info_dict}")  # Debug print
            video_file = f"{download_folder}/{info_dict['title']}.mp4"  # Get file path
            print(f"Video file path: {video_file}")  # Debug print

        # Return the file as a download response
        response = send_file(video_file, as_attachment=True)
        response.headers["Content-Disposition"] = f"attachment; filename={os.path.basename(video_file)}"

        # After sending the file, delete the video file from the folder
        os.remove(video_file)

        return response

    except Exception as e:
        print(f"Error: {str(e)}")  # Debug print
        # Clean up any .part files
        for file in os.listdir(download_folder):
            if file.endswith('.part'):
                os.remove(os.path.join(download_folder, file))
        return f"Error: {str(e)}"

@app.route('/progress')
def progress_status():
    global progress
    return jsonify(progress)

def progress_hook(d):
    global progress
    if d['status'] == 'downloading':
        # Remove ANSI escape codes
        percent_str = re.sub(r'\x1b\[[0-9;]*m', '', d['_percent_str']).strip('%')
        progress['status'] = 'downloading'
        progress['progress'] = float(percent_str)
        print(f"Downloading: {progress['progress']}%")
    elif d['status'] == 'finished':
        progress['status'] = 'finished'
        progress['progress'] = 100
        print("Download finished")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
