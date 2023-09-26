import os
import requests
import html
import re
import azure.cognitiveservices.speech as speechsdk
from gtts import gTTS
from flask import Flask, request, jsonify, render_template, send_file

app = Flask(__name__)
textGenHost = "localhost:5000"
AzureSpeechKey, AzureSpeechRegion = 'key', 'region'
speech_config = speechsdk.SpeechConfig(subscription=AzureSpeechKey, region=AzureSpeechRegion)
lastResponse = None
recognisedText = None
#set the key phrase, or set it as a array with multi keyphrase
keywords = ['Hey, Rosie', 'Hey Rosie', 'Hi, Rosie', 'Hi Rosie']


@app.route('/')
def index():
    return render_template('index.html')

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
        lastResponse = result
        return result
    
def textToSpeech(text):
    language = request.args.get('lang', 'en')
    tts = gTTS(text=text, lang=language)
    tts.save("static/uploads/speak.wav")

@app.route("/get-last-response")
def getLastResponse():
    return {'response': lastResponse}

@app.route("/get-recognised-text")
def getRecognisedText():
    return {'recognised': recognisedText}

@app.route('/upload-audio-to-self', methods=['POST'])
def SpeechToText():
    response = None
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
        print('Transcription is not None, Its: ', transcription)
        for keyword in keywords:
            match = re.search(re.escape(keyword), transcription, re.IGNORECASE)
            if match:
                print('KeyPhrase detect.')
                # Extract substring from the keyword to the end of the string
                start_index = match.start()
                transcription = transcription[start_index:]

                print('This text will be sent to GPT',transcription)
                response = textGen(transcription)
                break
        if response is not None:
            textToSpeech(response)

    # Return a success message
    return 'Transcription Successful', 200

@app.route('/process-text', methods=['POST'])
def process_text():
    print('Request received')  # Log to console when request is received
    data = request.get_json()
    print('Data received:', data)  # Log received data to console
    data = request.get_json()
    transcription = data.get('text', '')  # Get the text sent from the frontend
    
    response = None
    
    if transcription:
        print('Transcription is not None, Its: ', transcription)
        for keyword in keywords:
            match = re.search(re.escape(keyword), transcription, re.IGNORECASE)
            if match:
                print('KeyPhrase detect.')
                start_index = match.start()
                transcription = transcription[start_index:]
                print('This text will be sent to GPT',transcription)
                
                response = textGen(transcription)  # Call the textGen function with the modified transcription
                break  # Exit the loop once a keyword is found and transcription is updated
        
    if response:
        textToSpeech(response)  # Call the textToSpeech function with the response
        
    return jsonify(status='success')


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

