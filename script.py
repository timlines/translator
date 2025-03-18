import azure.cognitiveservices.speech as speechsdk
import requests
import json
from flask import Flask, render_template
from keys import *

# Azure Region and Endpoint
SPEECH_REGION = "southcentralus"
TRANSLATOR_ENDPOINT = "https://api.cognitive.microsofttranslator.com/"
TRANSLATOR_REGION = "southcentralus"

translated_history = []  # Store last few translations
current_partial = ""  # Store current translation of partial speech

# Flask Web App
app = Flask(__name__)

# Function to translate text using Azure Translator API
def translate_text(text, to_lang="es"):
    headers = {
        'Ocp-Apim-Subscription-Key': TRANSLATOR_KEY,
        'Ocp-Apim-Subscription-Region': TRANSLATOR_REGION,
        'Content-Type': 'application/json'
    }
    body = [{"Text": text}]
    
    response = requests.post(f"{TRANSLATOR_ENDPOINT}/translate?api-version=3.0&to={to_lang}", headers=headers, json=body)
    if response.status_code == 200:
        return response.json()[0]['translations'][0]['text']
    else:
        print(f"❌ Translation failed: {response.text}")
        return "[Translation Error]"

# Function for real-time speech-to-text and translation
def speech_to_text():
    global translated_history, current_partial
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    audio_config = speechsdk.AudioConfig(use_default_microphone=True)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    def recognizing_callback(event):
        """ Translates partial speech to Spanish as the speaker talks. """
        global current_partial
        if event.result.reason == speechsdk.ResultReason.RecognizingSpeech:
            english_text = event.result.text
            current_partial = translate_text(english_text)  # Translate on the fly
            print(f"📝 Partial (Translated): {current_partial}")

    def recognized_callback(event):
        """ Finalizes translation and moves it to history. """
        global translated_history, current_partial
        if event.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            final_text = event.result.text
            print(f"✅ Finalized: {final_text}")

            translated_text = translate_text(final_text)

            # Add to history
            translated_history.append(translated_text)
            if len(translated_history) > 5:
                translated_history.pop(0)

            print(f"🌍 Translated: {translated_text}")
            current_partial = ""  # Reset partial text

    def session_stopped_callback(event):
        print("⚠️ Session stopped. Restarting...")
        recognizer.start_continuous_recognition()

    def canceled_callback(event):
        print(f"❌ Recognition canceled: {event.reason}")
        if event.reason == speechsdk.CancellationReason.Error:
            print(f"Error Code: {event.error_code}")
            print(f"Error Details: {event.error_details}")

    # Connect event handlers
    recognizer.recognizing.connect(recognizing_callback)  # Updates while speaking
    recognizer.recognized.connect(recognized_callback)  # Finalized text
    recognizer.session_stopped.connect(session_stopped_callback)
    recognizer.canceled.connect(canceled_callback)

    print("🎤 Listening for speech (press Ctrl+C to stop)...")
    recognizer.start_continuous_recognition()

    import time
    while True:
        time.sleep(1)

# Start transcription in background
import threading
threading.Thread(target=speech_to_text, daemon=True).start()

@app.route('/')
def index():
    return render_template('display.html', history=translated_history, partial=current_partial)

@app.route('/text')
def get_text():
    return {"history": translated_history, "partial": current_partial}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
