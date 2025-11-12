import json
import requests

# --- Ollama Settings ---
OLLAMA_MODEL = "phi3"  # You can change this to "gemma:2b" or any model you have
OLLAMA_HOST = "http://127.0.0.1:11434"

# This is the "job" we give to the AI.
# It tells the AI what to listen for and how to format its response.
SYSTEM_PROMPT = """
You are a voice assistant's brain. You will receive a user's spoken text.
Your job is to understand the user's intent and extract key entities.
You must respond in JSON format ONLY. Do not write any other text.

Your possible intents are:
- 'control_iot': For turning devices on or off.
- 'perform_search': For any request to find information or search the web.
- 'open_google': For opening the Google homepage.
- 'open_youtube': For opening the YouTube homepage.
- 'play_music': For playing music.
- 'get_time': For asking the current time.
- 'general_question': For conversational chat or questions where the answer should be spoken.
- 'exit': For stopping the assistant.
- 'unknown': If you cannot understand the intent.

JSON format:
{
  "intent": "intent_name",
  "device": "device_name (e.g., 'light', 'heater', or null)",
  "action": "'on', 'off', or null",
  "query": "the search query (or null)",
  "llm_reply": "A helpful, conversational reply for a 'general_question' intent (or null)"
}

Examples:
User: "Turn on the light"
{"intent": "control_iot", "device": "light", "action": "on", "query": null, "llm_reply": null}

User: "Turn the LED off"
{"intent": "control_iot", "device": "led", "action": "off", "query": null, "llm_reply": null}

User: "Search for the weather in London"
{"intent": "perform_search", "query": "weather in London", "device": null, "action": null, "llm_reply": null}

User: "What is the capital of France?"
{"intent": "perform_search", "query": "capital of France", "device": null, "action": null, "llm_reply": null}

User: "Open YouTube"
{"intent": "open_youtube", "device": null, "action": null, "query": null, "llm_reply": null}

User: "What time is it?"
{"intent": "get_time", "device": null, "action": null, "query": null, "llm_reply": null}

User: "How are you?"
{"intent": "general_question", "device": null, "action": null, "query": null, "llm_reply": "I'm doing well, thank you for asking!"}

User: "Goodbye"
{"intent": "exit", "device": null, "action": null, "query": null, "llm_reply": null}

User: "asjdhflk"
{"intent": "unknown", "device": null, "action": null, "query": null, "llm_reply": null}
"""

def infer_intent(text: str, conversation: list = []):
    """
    Sends the user's text to Ollama to get a structured JSON response.
    """
    url = f"{OLLAMA_HOST}/api/generate"
    
    # We use a simplified history
    full_prompt = f"User: \"{text}\""
    
    payload = {
        "model": OLLAMA_MODEL,
        "system": SYSTEM_PROMPT,
        "prompt": full_prompt,
        "format": "json",
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, timeout=20)
        response.raise_for_status() 
        
        response_json = response.json()
        
        intent_json = json.loads(response_json.get("response", "{}"))
        
        # Extract the two things we need
        intent_dict = intent_json
        llm_reply = intent_json.get("llm_reply")

        print(f"[llm_module] Understood intent: {intent_dict}")
        return intent_dict, llm_reply

    except requests.exceptions.ConnectionError:
        print(f"[llm_module] Ollama error: Failed to connect to Ollama. Please check that Ollama is downloaded, running and accessible. https://ollama.com/download")
    except Exception as e:
        print(f"[llm_module] Ollama error: {e}")
        
    # Fallback in case of any error
    return {"intent": "unknown"}, "Sorry, I'm having trouble thinking right now."