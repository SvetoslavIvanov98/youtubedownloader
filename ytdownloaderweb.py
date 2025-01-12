from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import yt_dlp
import os
import shutil

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

    # yt-dlp options to fetch the best video or audio (no merging)
    ydl_opts = {
        'format': 'bestvideo',  # Download the best video only
        'outtmpl': f'{download_folder}/%(title)s.%(ext)s',  # Save with video title
        'quiet': True,  # Suppress output except errors
        'cookiefile': 'cookies.txt',  # Path to the cookies.txt file
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.youtube.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8,pl;q=0.7'
        },
        'geo_bypass': True,  # Bypass geographical restrictions
        'progress_hooks': [progress_hook]  # Add progress hook
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info and download it
            info_dict = ydl.extract_info(video_url, download=True)
            video_file = f"{download_folder}/{info_dict['title']}.{info_dict['ext']}"  # Get file path

        # Return the file as a download response
        response = send_file(video_file, as_attachment=True)

        # After sending the file, delete the video file from the folder
        os.remove(video_file)

        return response

    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/progress')
def progress_status():
    global progress
    return jsonify(progress)

def progress_hook(d):
    global progress
    if d['status'] == 'downloading':
        progress['status'] = 'downloading'
        progress['progress'] = float(d['_percent_str'].strip('%'))
        print(f"Downloading: {progress['progress']}%")
    elif d['status'] == 'finished':
        progress['status'] = 'finished'
        progress['progress'] = 100
        print("Download finished")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
