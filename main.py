import whisper
import json
import os
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"
import subprocess
import sys
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

class MediaTranscriber:
    def __init__(self, whisper_size="medium"):
        """Initializes the local Whisper model."""
        print(f"--- Loading Whisper {whisper_size} model... ---")
        self.stt_model = whisper.load_model(whisper_size) 

    def download_audio(self, url):
        output_template = "%(uploader)s_%(upload_date)s.%(ext)s"
        python_path = sys.executable

        cmd = [
            python_path,
            "-m",
            "yt_dlp",
            "-x",
            "--audio-format", "mp3",
            "--restrict-filenames",
            "-o", output_template,
            url
        ]

        print("--- Downloading audio ---")

        result = subprocess.run(
            cmd,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True
        )

        if result.returncode != 0:
            print("❌ yt-dlp failed:")
            print(result.stderr)
            return None

        # 🔥 IMPORTANT FIX:
        # reconstruct expected filename (best effort)
        expected = output_template.replace("%(ext)s", "mp3")

        # try to find actual file
        folder = os.getcwd()
        for file in os.listdir(folder):
            if file.endswith(".mp3"):
                return file

        return None

    def transcribe_local(self, audio_path):
        """Performs speech-to-text using the local Whisper model."""
        print(f"--- Transcribing: {audio_path} ---")
        result = self.stt_model.transcribe(audio_path, verbose=True)
        return result['text']

    def process_from_file(self, file_path, output_folder):
        """
        Reads URLs from a text file and saves each transcription to the output_folder.
        """
        # Ensure the output directory exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print(f"--- Created directory: {output_folder} ---")

        if not os.path.exists(file_path):
            print(f"Error: {file_path} not found.")
            return

        with open(file_path, "r") as f:
            urls = [line.strip() for line in f if line.strip()]

        print(f"Found {len(urls)} links. Starting process...")

        for i, url in enumerate(urls):
            print(f"\n=== Processing {i+1}/{len(urls)}: {url} ===")
            
            try:
                # 1. Letöltés
                audio_file = self.download_audio(url)
                if not audio_file or not os.path.exists(audio_file):
                    print(f"Skipping {url} due to download error.")
                    continue
                
                # 2. Transzkripció (Whisper vagy Azure hívás)
                raw_text = self.transcribe_local(audio_file)
                
                # --- Módosított rész kezdete ---
                # Levágjuk a kiterjesztést az audio fájl nevéből (pl. 'atv.mp3' -> 'atv')
                base_name = os.path.splitext(audio_file)[0]
                
                # A JSON fájl neve pontosan ugyanaz lesz, mint az audio fájlé volt
                file_name = f"{base_name}.json"
                output_path = os.path.join(output_folder, file_name)
                # --- Módosított rész vége ---

                # 3. Adatok összeállítása és mentése
                data = {
                    "url": url,
                    "original_filename": audio_file,
                    "raw_text": raw_text
                }
                
                with open(output_path, "w", encoding="utf-8") as f_out:
                    json.dump(data, f_out, ensure_ascii=False, indent=4)
                
                print(f"✅ Saved: {output_path}")

                # 4. Takarítás
                if os.path.exists(audio_file):
                    os.remove(audio_file)
                    print(f"--- Temporary file ({audio_file}) deleted. ---")

            except Exception as e:
                print(f"❌ Error processing {url}: {e}")

        print(f"\n--- Done! Results saved in: {output_folder} ---")

# --- EXECUTION ---
if __name__ == "__main__":
    # Get the base path from the environment
    BASE_PATH = os.getenv('PROJECT_DIR')
    
    if not BASE_PATH:
        print("Error: 'PROJECT_DIR' variable not found in .env file.")
        sys.exit(1)

    # Construct absolute paths
    INPUT_FILE = os.path.join(BASE_PATH, "video_links/m1_pot.txt")
    OUTPUT_DIR = os.path.join(BASE_PATH, "transcripts")
    
    # Initialize and run with the "large" model for accuracy
    transcriber = MediaTranscriber(whisper_size="medium")
    transcriber.process_from_file(INPUT_FILE, output_folder=OUTPUT_DIR)