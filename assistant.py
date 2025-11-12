import os
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import time
import json
from pathlib import Path
import queue  

# --- Import all our core modules ---
from core import sst_module, action_module, nlp_module, tts_module, iot_module
from core import llm_module as llm_module
from utils.logger import log_event

alert_queue = queue.Queue()
# --------------------------------------

CONV_FILE = Path("conversation.json")
MAX_PERSIST_TURNS = 50

# --- Conversation loading logic ---
if CONV_FILE.exists():
    try:
        with open(CONV_FILE, "r", encoding="utf-8") as f:
            conversation = json.load(f)
            if not isinstance(conversation, list):
                conversation = []
    except Exception:
        conversation = []
else:
    conversation = []


def _persist_conversation():
    """Save conversation to disk (trims older entries)."""
    try:
        trimmed = conversation[-MAX_PERSIST_TURNS:]
        with open(CONV_FILE, "w", encoding="utf-8") as f:
            json.dump(trimmed, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[assistant] Failed to persist conversation: {e}")


def respond_and_log(response_text: str, add_to_memory: bool = True):
    """Speak, print, and log the assistant's reply."""
    if not response_text:
        return
    print(f"🤖 Assistant: {response_text}")
    tts_module.speak(response_text, block=True)
    log_event(response_text)
    
    try:
        word_count = len(response_text.split())
        duration = 1.0 + (word_count * 0.15)
        print(f"[assistant] Pausing for {duration:.2f}s to prevent feedback...")
        time.sleep(duration)
    except Exception as e:
        print(f"[assistant] time.sleep error: {e}")
        time.sleep(3) # Fallback to a 3-second sleep
    # --- END OF FIX ---

    if add_to_memory:
        conversation.append({"role": "assistant", "content": response_text})
        _persist_conversation()


def handle_intent(intent_dict: dict, llm_reply: str, original_text: str):
    """
    Routes the parsed intent to the correct action module.
    """
    intent = (intent_dict or {}).get("intent", "unknown")
    query = intent_dict.get("query") # Get the query
    
    if intent == "open_google" and query:
        print("[assistant_fix] AI was confused, demoting 'open_google' to 'perform_search'")
        intent = "perform_search"
        intent_dict["intent"] = "perform_search" 
    
    action_response = action_module.execute_action(intent_dict)
    if action_response:
        respond_and_log(action_response)
        return None 

    if intent == "control_iot":
        device = intent_dict.get("device", "unknown device")
        action = intent_dict.get("action", "off")
        resp = iot_module.control_device(device, action)
        respond_and_log(resp)

    elif intent == "exit":
        respond_and_log("Goodbye! Have a great day.")
        return "exit" 

    elif intent == "general_question":
        respond_and_log(llm_reply or "I processed your question.")

    elif intent == "unknown":
        respond_and_log("Sorry, I didn't understand that.")

    return None

# --- UPDATED FUNCTION ---
def handle_iot_alert(message: str):
    """
    This function is GIVEN to the iot_module and is called
    from the BACKGROUND MQTT THREAD.
    It must NOT call speech functions directly.
    Instead, it puts the message in a queue for the main thread.
    """
    if message == "HIGH":
        alert_text = "Alert! The temperature is over 40 degrees!"
        print(f"[assistant] Queuing IoT Alert: {alert_text}")
        alert_queue.put(alert_text) # <-- Put message in queue
        
    elif message == "NORMAL":
        alert_text = "The temperature has returned to normal."
        print(f"[assistant] Queuing IoT Alert: {alert_text}")
        alert_queue.put(alert_text) # <-- Put message in queue
# --------------------


def main():
    # --- Set up the IoT alert callback ---
    iot_module.set_alert_callback(handle_iot_alert)
    # -------------------------------------
    
    greeting = "Hello! I am your Smart Voice Assistant. How can I help you?"
    respond_and_log(greeting)

    while True:
        try:
            # --- NEW: STEP 0: Check for Alerts ---
            # Check if the IoT (background) thread has sent us an alert.
            if not alert_queue.empty():
                alert_message = alert_queue.get()
                # We are in the main thread, so this call is safe.
                respond_and_log(alert_message, add_to_memory=False)
                continue # Skip listening and go to top of loop
            # -------------------------------------

            # --- STEP 1: Listen for a command ---
            print("\n🎙️  Listening for your command...")
            text = sst_module.transcribe_from_microphone(duration=4)
            if not text or text == ".": # Filter out quiet noise
                print("... (Silence detected) ...")
                continue

            print(f"🗣 You said: {text}")
            conversation.append({"role": "user", "content": text})
            _persist_conversation()

            # --- STEP 2: Process Command (The Brain) ---
            intent_dict, llm_reply = llm_module.infer_intent(text, conversation=conversation)
            
            # --- STEP 3: Execute Command ---
            if handle_intent(intent_dict, llm_reply, text) == "exit":
                break

        except KeyboardInterrupt:
            respond_and_log("Goodbye!")
            break
        except Exception as e:
            print(f"⚠️ Main loop error: {e}")
            respond_and_log("Something- wrong. Let's try again.")
            time.sleep(1)


if __name__ == "__main__":
    print("🚀 Starting Smart Voice Assistant...")
    main()