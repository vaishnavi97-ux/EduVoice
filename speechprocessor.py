from transformers import pipeline
import whisper
import re
from openai import OpenAI
client = OpenAI(api_key="YOUR_API_KEY")
whisper_model = whisper.load_model("base")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
# SPEECH TO TEXT (UPLOAD)
def speech_to_text(audio_path):
    result = whisper_model.transcribe(audio_path)
    return result["text"]

BANNED_WORDS = [
    "shut up",
    "shutup",
    "idiot",
    "keep quiet",
    "dont make noise",
    "listen",
    "silence",
    "stop talking",
    "pay attention",
    "focus",
    "be quiet"
]
def clean_text(text):
    if not text.strip():
        return ""
    text = re.sub(r'\s+', ' ', text)
    for word in BANNED_WORDS:
        text = re.sub(rf"\b{word}\b", "", text, flags=re.IGNORECASE)
    return text.strip()

# =============================
# GPT SUMMARIZATION
# =============================
def summarize(text):
    if not text or len(text.split()) < 10:
        return "• Audio is too short to generate summary."
    try:
        max_len = min(len(text.split()), 300)
        notes = summarizer(
            text,
            max_length=max_len,
            min_length=80,
            do_sample=False
        )[0]["summary_text"]
        return f"""📘 Detailed Notes {notes}"""
    except Exception as e:
        print("SUMMARY ERROR:", e)
        # Fallback: simple sentence extraction
        sentences = re.split(r'[.!?]', text)
        bullets = [s.strip().capitalize() for s in sentences if len(s.split()) > 6][:5]
        return "📘 Quick Notes\n\n" + "\n".join("• " + b for b in bullets)
def process_audio(filepath):
    text = speech_to_text(filepath)
    cleaned = clean_text(text)
    summary = summarize(cleaned)
    return text, summary