import os
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

# app.py
import streamlit as st
import time

# --- Import all our core modules (same as assistant.py) ---
from core import sst_module, action_module, nlp_module, tts_module, iot_module
from core import llm_module as llm_module
from utils.logger import log_event

# --- Page Config ---
st.set_page_config(page_title="Smart Voice Assistant", layout="centered")
st.title("🎙️ Smart Voice Assistant")
st.write("Click the button, speak your command, and see the response.")

# --- Session State Initialization ---
# This holds the chat history for display
if "history" not in st.session_state:
    st.session_state.history = []
# This holds the LLM's conversation context
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# --- Helper Function (adapted from assistant.py) ---
def speak_and_log(response_text: str, add_to_memory: bool = True):
    """
    Shows response in Streamlit, speaks it, and logs it to history.
    """
    if not response_text:
        return
    
    # Show in Streamlit
    st.info(f"🤖 Assistant: {response_text}")
    
    # Speak the response
    # block=False is important for web apps so it doesn't hang
    tts_module.speak(response_text, block=False) 
    
    # Log to file
    log_event(response_text)
    
    # Add to our display history and LLM context
    st.session_state.history.append(("assistant", response_text))
    if add_to_memory:
        st.session_state.conversation.append({"role": "assistant", "content": response_text})

# --- Main App Interface ---
if st.button("🎤 Click to Record Command (4s)"):
    
    # --- STEP 1: Listen for a command ---
    with st.spinner("Listening... (Please allow mic access)"):
        text = sst_module.transcribe_from_microphone(duration=4)
    
    if not text or text == ".":
        st.warning("No speech detected or silent.")
    else:
        # --- 1a. Log User Input ---
        st.success(f"🗣️ You said: {text}")
        st.session_state.history.append(("user", text))
        st.session_state.conversation.append({"role": "user", "content": text})

        # --- 2. Process Command (The Brain) ---
        with st.spinner("Thinking..."):
            intent_dict, llm_reply = llm_module.infer_intent(text, st.session_state.conversation)
        
        # --- 3. Execute Command (The Logic from assistant.py's handle_intent) ---
        intent = (intent_dict or {}).get("intent", "unknown")
        query = intent_dict.get("query")
        
        # --- Fix for "men'ssek" problem ---
        if intent == "open_google" and query:
            st.caption("[Debug] AI was confused, demoting 'open_google' to 'perform_search'")
            intent = "perform_search"
            intent_dict["intent"] = "perform_search"
        
        # --- 1. Handle Actions (Google, YouTube, Search, Time) ---
        action_response = action_module.execute_action(intent_dict)
        if action_response:
            speak_and_log(action_response)

        # --- 2. Handle IoT (Relay) ---
        elif intent == "control_iot":
            device = intent_dict.get("device", "unknown device")
            action = intent_dict.get("action", "off")
            resp = iot_module.control_device(device, action)
            speak_and_log(resp)

        # --- 3. Handle Exit ---
        elif intent == "exit":
            speak_and_log("Goodbye! Have a great day.")
            # We don't exit the web app, just log it.

        # --- 4. Handle General Questions ---
        elif intent == "general_question":
            speak_and_log(llm_reply or "I processed your question.")

        # --- 5. Final Fallback ---
        elif intent == "unknown":
            speak_and_log("Sorry, I didn't understand that.")

# --- Display History (at the bottom) ---
st.markdown("---")
st.subheader("Conversation History")
if not st.session_state.history:
    st.caption("No commands given yet.")

# Display the last 10 messages, most recent at the top
for role, msg in reversed(st.session_state.history[-10:]):
    if role == "user":
        st.markdown(f"**<div style='text-align: right; color: #3399FF;'>🗣️ You: {msg}</div>**", unsafe_allow_html=True)
    else:
        st.markdown(f"**<div style='text-align: left;'>🤖 Assistant: {msg}</div>**", unsafe_allow_html=True)