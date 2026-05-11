import json
import os
import sys
import re
import time
import random

from tqdm import tqdm
from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi


# 1. DEBUG: script location
current_script_path = os.path.abspath(__file__)
project_dir = os.path.dirname(current_script_path)

print(f"DEBUG: Automatikusan felismert mappa: {project_dir}")


# 2. Paths
input_file = os.path.join(project_dir, "video_links", "video_ids.txt")
output_dir = os.path.join(project_dir, "news_transcripts")

if not os.path.exists(input_file):
    print(f"HIBA: Nem találom a fájlt itt: {input_file}")
    print("Ellenőrizd a 'video_links/video_ids.txt' fájlt!")
    sys.exit(1)

os.makedirs(output_dir, exist_ok=True)

print(f"DEBUG: Input file: {input_file}")
print(f"DEBUG: Output dir: {output_dir}")


# 3. Utils
def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\s-]", "", name)
    return name.strip().replace(" ", "_")


# 4. Load video IDs
with open(input_file, "r", encoding="utf-8") as f:
    video_ids = [line.strip() for line in f if line.strip()]


# 5. yt-dlp options (modern)
ydl_opts = {
    "quiet": True,
    "skip_download": True,
    "noplaylist": True,
}


# 6. Processing loop
for v_id in tqdm(video_ids[44:], desc="Processing Videos", unit="video"):
    video_url = f"https://www.youtube.com/watch?v={v_id}"

    try:
        # ---- Metadata ----
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

        channel_name = info.get("channel", "Unknown")
        upload_date = info.get("upload_date", "00000000")
        title = info.get("title", "")

        # ---- Transcript ----
        full_text = None

        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(v_id)

            try:
                transcript = transcript_list.find_generated_transcript(["hu"])
            except Exception:
                transcript = transcript_list.find_transcript(["hu"])

            data = transcript.fetch()
            full_text = " ".join(entry.text for entry in data)

        except Exception as te:
            tqdm.write(f"  - No transcript for {v_id}: {te}")

        # ---- Save ----
        if full_text:
            safe_channel = sanitize_filename(channel_name)
            filename = f"{safe_channel}_{upload_date}.json"
            filepath = os.path.join(output_dir, filename)

            output_data = {
                "video_id": v_id,
                "title": title,
                "channel": channel_name,
                "upload_date": upload_date,
                "transcript": full_text,
            }

            with open(filepath, "w", encoding="utf-8") as json_file:
                json.dump(output_data, json_file, ensure_ascii=False, indent=4)

            tqdm.write(f"Saved: {filename}")

        # polite delay
        time.sleep(random.uniform(20, 30))

    except Exception as e:
        tqdm.write(f"  !!! Metadata Error for {v_id}: {str(e)[:120]}")

print("\n--- Done! ---")