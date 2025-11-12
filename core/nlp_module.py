import pandas as pd
import os

INTENTS_FILE = os.path.join("data", "intents.csv")

def _load_intents():
    try:
        df = pd.read_csv(INTENTS_FILE)
        if "intent" not in df.columns or "response" not in df.columns:
            return pd.DataFrame(columns=["intent", "response"])
        return df
    except Exception:
        return pd.DataFrame(columns=["intent", "response"])

intents_df = _load_intents()

def handle_intent(text: str):
    """Check intents CSV for substring matches. Returns response string or None."""
    if not text:
        return None
    txt = text.lower()
    for _, row in intents_df.iterrows():
        intent_phrase = str(row.get("intent", "")).lower()
        if intent_phrase and intent_phrase in txt:
            return str(row.get("response", ""))
    return None
