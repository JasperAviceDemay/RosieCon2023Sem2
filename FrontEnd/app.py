import os
import requests
import openai
import json
import html
from gtts import gTTS
from flask import Flask, request, jsonify, render_template, send_file
from pydub import AudioSegment
from pydub.playback import play
from playsound import playsound
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

app = Flask(__name__)
textGenHost = "localhost:5000"

@app.route('/')
def index():
    return render_template('index.html')

def transcribe(audio_output_file_path, openAI_API_key):
    openai.api_key = openAI_API_key

    with open(audio_output_file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

    transcribed_text = transcript['text']
    return transcribed_text

def send_string_to_endpoint(endpoint, text):
    try:
        response = requests.post(endpoint, json={'data': text})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f'Failed to send string to endpoint: {e}')
        return False
    except ValueError as e:
        print(f'Response body is not valid JSON: {e}')
        return False
    return True

def textGen(input):
    textgenURL = f"http://{textGenHost}/api/v1/chat"
    request = {
        'user_input': input,
        'max_new_tokens': 250,
        'auto_max_new_tokens': False,
        'max_tokens_second': 0,
        'mode': 'chat',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'character': 'Rosie',
        'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
        'your_name': 'You',
        'regenerate': False,
        '_continue': False,
        'chat_instruct_command': 'Continue the chat dialogue below. Write a single reply for the character "<|character|>".\n\n<|prompt|>',

        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',
        'do_sample': True,
        'temperature': 0.7,
        'top_p': 0.1,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.18,
        'repetition_penalty_range': 0,
        'top_k': 40,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,
        'guidance_scale': 1,
        'negative_prompt': '',

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 2048,
        'ban_eos_token': False,
        'custom_token_bans': '',
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    print("Generating...")
    response = requests.post(textgenURL, json=request)
    print(response.status_code)
    if response.status_code == 200:
        result = html.unescape(response.json()['results'][0]['history']['visible'][-1][1])
        print(result)
        return result


@app.route('/get-audio-timestamp')
def get_audio_timestamp():
    audio_file_path = 'static/uploads/speak.wav'
    if os.path.exists(audio_file_path):
        last_modified = os.path.getmtime(audio_file_path)
        return {'timestamp': last_modified}
    return {'timestamp': None}, 404

@app.route('/upload-audio-to-self', methods=['POST'])
def speech_to_text():
    # Define the path to where the audio file should be saved
    audio_output_file_path = 'static/uploads/audio_file.wav'

    # Retrieve OpenAI API key and Think endpoint from environment variables
    openAI_API_key = os.environ.get('OPENAI_API_KEY') or "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"
    # think_endpoint = os.environ.get('THINK_SERVICE') or "http://think_service:5080/think"

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
    print("Transcribing")
    transcription = transcribe(audio_output_file_path, openAI_API_key)
    print(transcription)
    response = textGen(transcription)
    if response is not None:
        tts(response)
    # send_string_to_endpoint(think_endpoint, query_for_think)
    
    # Return a success message
    return 'Audio file saved successfully', 200
    
def tts(input):
    language = request.args.get('lang', 'en')

    tts = gTTS(text=input, lang=language)
    tts.save("static/uploads/speak.wav")

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
    app.run(port=5001)

