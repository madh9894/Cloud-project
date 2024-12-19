from fastapi import FastAPI, HTTPException
from transformers import pipeline
from typing import Dict
import uuid

app = FastAPI()

# Load translation model (English to Arabic)
translator_en_to_ar = pipeline("translation_en_to_ar", model="Helsinki-NLP/opus-mt-en-ar")

# Dictionary to store the status of translation requests
translation_status: Dict[str, Dict] = {}

@app.get("/")
def home():
    """
    Root endpoint to confirm the translation service is running.
    """
    return {"message": "EN2AR Translation Service with Status Tracking is running"}

@app.post("/translate/en2ar")
def translate_en2ar(text: str):
    """
    Translate text from English to Arabic and store status.
    """
    if not text:
        raise HTTPException(status_code=400, detail="Text input is required")
    
    # Generate a unique ID for the translation request
    request_id = str(uuid.uuid4())
    
    # Perform translation
    result = translator_en_to_ar(text, max_length=400)[0]['translation_text']
    
    # Update the status dictionary
    translation_status[request_id] = {"status": "completed", "result": result}

    return {
        "request_id": request_id,
        "status": "completed",
        "translated_text": result
    }

@app.get("/translate/en2ar/status/{id}")
def get_en2ar_status(id: str):
    """
    Retrieve the status of an English to Arabic translation request.
    """
    if id not in translation_status:
        raise HTTPException(status_code=404, detail="Request ID not found")
    return {"request_id": id, "status": translation_status[id]["status"], "result": translation_status[id]["result"]}
