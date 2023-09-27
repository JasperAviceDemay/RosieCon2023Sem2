import os
import requests
import html
import azure.cognitiveservices.speech as speechsdk
from gtts import gTTS
from flask import Flask, request, jsonify, render_template, send_file
from rosieTextGen import textGen

app = Flask(__name__)
AzureSpeechKey, AzureSpeechRegion = os.environ.get('AZURESPEECHKEY'), os.environ.get('AZUREREGION')
speech_config = speechsdk.SpeechConfig(subscription=AzureSpeechKey, region=AzureSpeechRegion)
lastResponse = None
recognisedText = None

def transcribeFile(audio_output_file_path):
    audio_config = speechsdk.AudioConfig(filename=audio_output_file_path)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    result = speech_recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")

def textToSpeech(text):
    language = request.args.get('lang', 'en')
    tts = gTTS(text=text, lang=language)
    tts.save("static/uploads/speak.wav")

# Flask Routing
@app.route('/')
def index():
    return render_template('index.html')

@app.route("/get-last-response")
def getLastResponse():
    return {'response': lastResponse}

@app.route("/get-recognised-text")
def getRecognisedText():
    return {'recognised': recognisedText}

@app.route('/upload-audio-to-self', methods=['POST'])
def SpeechToText():
    # Define the path to where the audio file should be saved
    audio_output_file_path = 'static/uploads/audio_file.wav'

    # Retrieve OpenAI API key from environment variables
    #openAI_API_key = os.environ.get('OPENAI_API_KEY') or "<insert your API key here>"
    openAI_API_key = 'OPENAI_API_KEY'

    # Check if the audio_url field is present in the request JSON payload
    if 'file' not in request.files:
        return 'No file part in the request', 400
    audio_file = request.files['file']
    if not audio_file:
        return 'No file selected for upload', 400

    # Download the audio file from the specified URL
    audio_file.save(audio_output_file_path)
    # Save the downloaded audio file to disk
    
    
    # Transcribe the audio file using OpenAI and send the query to the Think endpoint
    print("Transcribing File")
    transcription = transcribeFile(audio_output_file_path)
    if transcription is not None:
        global recognisedText
        recognisedText = transcription
        print(transcription)
        response = rosieText.textGen(transcription)
        if response is not None:
            textToSpeech(response)
    
    
    # Return a success message
    return 'Transcription Successful', 200


@app.route('/rosie-speak', methods=['POST'])
def text_to_speech():
    try:
        data_string = request.json.get('data')
        if not data_string:
            raise ValueError('Invalid request: missing data field')
    except ValueError as e:
        return str(e), 400

    language = request.args.get('lang', 'en')

    tts = gTTS(text=data_string, lang=language)
    tts.save("static/uploads/speak.wav")

    return jsonify({"response": "Audio file saved successfully"}), 200

if __name__ == '__main__':
    rosieText = textGen()
    app.run(port=5001)

