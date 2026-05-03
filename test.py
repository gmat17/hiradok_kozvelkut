import os
import json
import time
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

def run_api_safe():
    source_file = 'eredmeny_video_1.json'
    with open(source_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        text_to_fix = data.get('raw_text', '')

    print("--- Küldés a Gemininek... (Ha hibát dob, várok és újrapróbálom) ---")

    prompt = f"""
        Feladat: Te egy professzionális szerkesztő vagy. Itt egy nyers híradó leirat, amit a 
        Whisper készített. Javítsd ki a központozást és a helyesírást, különösen figyelj a 
        nevekre (pl. Vitézy Dávid, Lázár János, Magyar Péter), amik a magyar politikában gyakran
        előfordulnak. Ne hagyd ki a politikai  kifejezéseket, és maradj teljesen 
        tárgyilagos. Csak a javított szöveget add vissza!
        
        Szöveg: {text_to_fix}
        """
    
    # ÚJRA PRÓBÁLKOZÓ LOGIKA
    for attempt in range(3): # Maximum 3 próbálkozás
        try:
            response = model.generate_content(prompt)
            print("\n=== SIKERÜLT! ===\n")
            print(response.text)
            return # Ha sikerült, kilépünk a függvényből
        except Exception as e:
            if "429" in str(e):
                print(f"Várnom kell... A limit betelt. Újrapróbálkozás 15 mp múlva... (Próbálkozás: {attempt+1}/3)")
                time.sleep(15) # Várunk 15 másodpercet a következő kérés előtt
            else:
                print(f"Váratlan hiba: {e}")
                break

if __name__ == "__main__":
    run_api_safe()