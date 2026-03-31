import os
import re

# We wrap the import in a try-except to avoid crashing the server
# if the user hasn't installed transformers yet. For production,
# a lightweight model like distilbart is best for quick API responses.
try:
    from transformers import pipeline
    print("[INFO] Loading NLP Summarization Model. This may take a moment on first boot...")
    _summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
except Exception as e:
    _summarizer = None
    print(f"[WARNING] NLP Summarizer is unavailable. Please `pip install transformers torch`. Error: {e}")

def summarize_text(text: str, max_length: int = 50, min_length: int = 10) -> str:
    """
    Summarizes a given text using a pre-trained transformer model.
    Short texts are returned verbatim or slightly truncated.
    """
    if not text or len(text.strip()) < 50:
        return text

    if not _summarizer:
        # Fallback if NLP failed to load
        return text[:150] + "..."

    try:
        # We cap the input length to avoid memory blowouts on long articles
        truncated_input = text[:1024]
        
        # distilbart expects at least somewhat long text to summarize
        if len(truncated_input.split()) < 30:
            return text

        summary_obj = _summarizer(truncated_input, max_length=max_length, min_length=min_length, do_sample=False)
        summary = summary_obj[0]['summary_text']
        
        # Clean up weird spacing created by the tokenizer
        summary = re.sub(r'\s([?.!"](?:\s|$))', r'\1', summary)
        return summary.strip()

    except Exception as e:
        print(f"[ERROR] Summarization failed: {e}")
        return text[:150] + "..."
