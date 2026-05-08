import json
import os
import sys
import re
import sys
from tqdm import tqdm
from youtube_transcript_api import YouTubeTranscriptApi
from yt_dlp import YoutubeDL
import random
import time

# 1. DEBUGGING: Check Environment Variables
current_script_path = os.path.abspath(__file__)
project_dir = os.path.dirname(current_script_path)
print(f"DEBUG: Automatikusan felismert mappa: {project_dir}")

# 2. Setup Paths
input_file = os.path.join(project_dir, 'video_links', 'video_ids.txt')
output_dir = os.path.join(project_dir, 'news_transcripts')

if not os.path.exists(input_file):
    print(f"HIBA: Nem találom a fájlt itt: {input_file}")
    print("Győződj meg róla, hogy létezik a 'video_links' mappa és benne a 'video_ids.txt'!")
    sys.exit(1)

print(f"DEBUG: Looking for input file at: {input_file}")
if not os.path.exists(input_file):
    print(f"CRITICAL ERROR: Input file not found!")
    sys.exit(1)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"DEBUG: Created output directory: {output_dir}")

# 3. FIX JS RUNTIME: Search for Node.js path automatically
def get_node_path():
    # Common paths for node on macOS (Homebrew or Intel/Apple Silicon)
    paths = ['/usr/local/bin/node', '/opt/homebrew/bin/node', '/usr/bin/node']
    for path in paths:
        if os.path.exists(path):
            return path
    return None

node_path = get_node_path()

# 4. Extraction Logic
def sanitize_filename(name):
    return re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')

with open(input_file, "r") as f:
    video_ids = [line.strip() for line in f if line.strip()]

# YT-DLP Configuration
ydl_opts = {
    "quiet": True,
    "skip_download": True,
    # This force-points yt-dlp to use Node.js if found
    "javascript_runtimes": [node_path] if node_path else None,
}

if node_path:
    print(f"DEBUG: Found JavaScript runtime at: {node_path}")
else:
    print("WARNING: Node.js not found! The extraction might fail.")

for v_id in tqdm(video_ids[44::], desc="Processing Videos", unit="video"):
    video_url = f"https://www.youtube.com/watch?v={v_id}"

    try:
        # Metadata Extraction
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
        
        channel_name = info.get("channel", "Unknown")
        upload_date = info.get("upload_date", "00000000")
        title = info.get("title", "")

        # Transcript Extraction
        try:
            api = YouTubeTranscriptApi()
            transcript_list = api.list(v_id)
            
            try:
                transcript = transcript_list.find_generated_transcript(['hu'])
            except:
                transcript = transcript_list.find_transcript(['hu'])
            
            data = transcript.fetch()
            full_text = " ".join(entry.text for entry in data)
            
        except Exception as te:
            tqdm.write(f"  - No transcript for {v_id}: {te}")
            full_text = None

        # Saving File
        if full_text:
            safe_channel = sanitize_filename(channel_name)
            filename = f"{safe_channel}_{upload_date}.json"
            filepath = os.path.join(output_dir, filename)

            output_data = {
                "video_id": v_id,
                "title": title,
                "channel": channel_name,
                "upload_date": upload_date,
                "transcript": full_text
            }

            with open(filepath, "w", encoding="utf-8") as json_file:
                print('JSON was writtin succesfully!')
                json.dump(output_data, json_file, ensure_ascii=False, indent=4)

        time.sleep(random.uniform(20, 30))

    except Exception as e:
        tqdm.write(f"  !!! Metadata Error for {v_id}: {str(e)[:80]}")

print("\n--- Done! ---")