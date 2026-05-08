import azure.cognitiveservices.speech as speechsdk
import json
import os
import subprocess
import sys
import time
from dotenv import load_dotenv

# Környezeti változók betöltése
load_dotenv()

class AzureMediaTranscriber:
    def __init__(self):
        """Inicializálja az Azure Speech szolgáltatást."""
        self.base_path = os.getenv('PROJECT_DIR')
        if not self.base_path:
            raise ValueError("Hiba: 'PROJECT_DIR' nem található a .env fájlban.")

        print("--- Azure Speech Service inicializálása... ---")
        self.speech_key = os.getenv('AZURE_SPEECH_KEY')
        self.service_region = os.getenv('AZURE_SPEECH_REGION')
        
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key, 
            region=self.service_region
        )
        self.speech_config.speech_recognition_language = "hu-HU"

    def download_audio(self, url):
        """
        Letölti az audiót WAV formátumban a projekt mappájába.
        """
        output_template = "%(uploader)s_%(upload_date)s.%(ext)s"
        python_path = sys.executable 
        
        # Fájlnév lekérése
        try:
            get_name_cmd = [python_path, '-m', 'yt_dlp', '--get-filename', '-o', output_template, url]
            generated_name = subprocess.check_output(get_name_cmd).decode().strip()
            # Kicseréljük a kiterjesztést wav-ra
            final_audio_name = os.path.splitext(generated_name)[0] + ".wav"
        except Exception as e:
            print(f"Hiba a fájlnév lekérésekor: {e}")
            return None
        
        # Teljes útvonal a projekt mappáján belül
        full_audio_path = os.path.join(self.base_path, final_audio_name)
        
        if os.path.exists(full_audio_path):
            print(f"--- A fájl már létezik: {final_audio_name} ---")
            return full_audio_path

        print(f"--- Letöltés indítása: {final_audio_name} ---")
        # Idézőjelek használata a biztonság kedvéért
        download_cmd = f'{python_path} -m yt_dlp -x --audio-format wav -o "{full_audio_path}" "{url}"'
        os.system(download_cmd)
        
        return full_audio_path

    def transcribe_azure(self, audio_path):
        """Folyamatos Azure transzkripció időtúllépés elleni védelemmel."""
        audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config, 
            audio_config=audio_config
        )

        transcript_segments = []
        done = False
        last_speech_time = time.time()

        def recognized_handler(evt):
            nonlocal last_speech_time
            if evt.result.text:
                print(f"Felismerve: {evt.result.text[:60]}...")
                transcript_segments.append(evt.result.text)
                last_speech_time = time.time()

        def stop_handler(evt):
            nonlocal done
            done = True

        recognizer.recognized.connect(recognized_handler)
        recognizer.session_stopped.connect(stop_handler)
        recognizer.canceled.connect(stop_handler)

        print(f"--- Azure Cloud Transzkripció: {os.path.basename(audio_path)} ---")
        recognizer.start_continuous_recognition()
        
        # Várunk, amíg kész nem lesz, vagy amíg 20 mp csend nem lesz a végén
        while not done:
            time.sleep(1)
            if time.time() - last_speech_time > 20:
                print("--- Időtúllépés: nincs több beszéd, leállítás... ---")
                break
            
        recognizer.stop_continuous_recognition()
        return " ".join(transcript_segments)

    def process_from_file(self, file_path, output_folder_name="transcripts"):
        """
        Végigmegy a linkeken és menti a JSON fájlokat.
        """
        output_folder = os.path.join(self.base_path, output_folder_name)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        if not os.path.exists(file_path):
            print(f"Hiba: A megadott link-fájl nem található: {file_path}")
            return

        with open(file_path, "r") as f:
            urls = [line.strip() for line in f if line.strip()]

        for i, url in enumerate(urls):
            print(f"\n=== Videó {i+1}/{len(urls)} feldolgozása ===")
            
            try:
                # 1. Letöltés
                audio_file = self.download_audio(url)
                if not audio_file or not os.path.exists(audio_file):
                    continue
                
                # 2. Transzkripció Azure-ral
                raw_text = self.transcribe_azure(audio_file)
                
                # 3. Mentés (ugyanazzal a névvel, mint az audio fájl)
                base_name = os.path.splitext(os.path.basename(audio_file))[0]
                output_path = os.path.join(output_folder, f"{base_name}.json")
                
                data = {
                    "url": url,
                    "filename": os.path.basename(audio_file),
                    "raw_text": raw_text
                }
                
                with open(output_path, "w", encoding="utf-8") as f_out:
                    json.dump(data, f_out, ensure_ascii=False, indent=4)
                
                print(f"✅ Mentve: {output_path}")

                # 4. Takarítás (WAV törlése)
                if os.path.exists(audio_file):
                    os.remove(audio_file)
                    print(f"--- Ideiglenes WAV törölve. ---")

            except Exception as e:
                print(f"❌ Hiba a videó feldolgozásakor ({url}): {e}")

# --- INDÍTÁS ---
if __name__ == "__main__":
    transcriber = AzureMediaTranscriber()
    # A linkeket tartalmazó fájl abszolút útvonala
    LINKS_FILE = os.path.join(transcriber.base_path, "video_links", "m1_pot2_forditott.txt")
        
    transcriber.process_from_file(LINKS_FILE)