# core/tts_module.py
import pyttsx3
import threading
import os

# --- pyttsx3 Engine (Reliable Fallback) ---
try:
    if os.name == 'posix':
        _engine = pyttsx3.init('nsss')
    else:
        _engine = pyttsx3.init()
        
    _engine.setProperty("rate", 180) # You can adjust the speed
    _pyttsx3_available = True
    print("[tts_module] Using pyttsx3 engine (reliable fallback).")

except Exception as e:
    print(f"Failed to load pyttsx3: {e}. Using print() as fallback.")
    _engine = None
    _pyttsx3_available = False


def _speak_pyttsx3(text: str):
    """Internal function to synthesize and play audio."""
    try:
        _engine.say(text)
        _engine.runAndWait()
    except Exception as e:
        print(f"[tts_module] pyttsx3 failed: {e}")
        print(f"🤖 Assistant (TTS Fallback): {text}")

def speak(text: str, block: True):
    """Speak text. If block=True, it will wait. If False, it runs in a thread."""
    if not text:
        return

    if not _pyttsx3_available:
        print(f"🤖 Assistant (TTS Disabled): {text}")
        return

    def _run():
        _speak_pyttsx3(text)

    if block:
        _run()
    else:
        # This part is used for a non-blocking "Yes?" response
        t = threading.Thread(target=_run, daemon=True)
        t.start()