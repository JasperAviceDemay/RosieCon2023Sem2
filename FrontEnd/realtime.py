#Jiarui
import os
import re
import time
import azure.cognitiveservices.speech as speechsdk
from rosieTextGen import textGen

keywords = ['Hey, Rosie', 'Hey Rosie', 'Hi, Rosie', 'Hi Rosie']
endwords = ['Thank you, Rosie.', 'End conversation.', 'That will be all.']
AzureSpeechKey, AzureSpeechRegion = os.environ.get('AZURESPEECHKEY'), os.environ.get('AZUREREGION')
speech_config = speechsdk.SpeechConfig(subscription=AzureSpeechKey, region=AzureSpeechRegion)
#audio config
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
#default voice can be change or custom
speech_config.speech_synthesis_voice_name='en-US-JennyNeural'
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)



def conversation_transcriber_recognition_canceled_cb(evt: speechsdk.SessionEventArgs):
    print('Canceled event')

def conversation_transcriber_session_stopped_cb(evt: speechsdk.SessionEventArgs):
    print('SessionStopped event')

def conversation_transcriber_transcribed_cb(evt: speechsdk.SpeechRecognitionEventArgs):
    print('TRANSCRIBED:')
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print('\tText={}'.format(evt.result.text))
        print('\tSpeaker ID={}'.format(evt.result.speaker_id))
    elif evt.result.reason == speechsdk.ResultReason.NoMatch:
        print('\tNOMATCH: Speech could not be TRANSCRIBED: {}'.format(evt.result.no_match_details))

def conversation_transcriber_session_started_cb(evt: speechsdk.SessionEventArgs):
    print('SessionStarted event')


def printline(): print('------------------------------------------------\n')


def from_mic():
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    print("Speak into your microphone.")
 
    while True:
        result = speech_recognizer.recognize_once_async().get()
        transcription = result.text.strip()
        print(transcription)
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Recognized: {}".format(transcription))
            
            keyword_detected = False
            endword_detected = any(re.search(re.escape(endword), transcription, re.IGNORECASE) for endword in endwords)
            
            response = None
            for keyword in keywords:
                match = re.search(re.escape(keyword), transcription, re.IGNORECASE)
                if match:
                    print('KeyPhrase detected.')
                    keyword_detected = True
                    # Extract substring from the keyword to the end of the string
                    start_index = match.start()
                    transcription = transcription[start_index:]
                    print(f"This text will be sent to GPT '{transcription}'")
                    printline()
                    response = rosieText.textGen(transcription)
                    if response:
                        to_speaker(response)
                    break
            
            if endword_detected:
                print("Ending conversation.")
                break  # Exit the loop if an endword is detected
            
            if not keyword_detected and not endword_detected:
                print('No keywords detected, continue listening.')
                printline()
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(result.no_match_details))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
                break




def to_speaker(text):
    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
    
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")





# def from_mic():
    # speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    # print("Speak into your microphone.")
    
    # while True:
        # result = speech_recognizer.recognize_once_async().get()
        # transcription = result.text.strip()
        # print(transcription)
        # if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            # print("Recognized: {}".format(transcription))
            
            # response = None
            # if any(re.search(re.escape(keyword), transcription, re.IGNORECASE) for keyword in keywords):
                # print('KeyPhrase detected.')
                # response = rosieText.textGen(transcription)
                
            # if any(re.search(re.escape(endword), transcription, re.IGNORECASE) for endword in endwords):
                # print("Ending conversation.")
                # break
            
            # #if response is not None:
            # #    textToSpeech(response)
                
        # elif result.reason == speechsdk.ResultReason.NoMatch:
            # print("No speech could be recognized: {}".format(result.no_match_details))
        # elif result.reason == speechsdk.ResultReason.Canceled:
            # cancellation_details = result.cancellation_details
            # print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            # if cancellation_details.reason == speechsdk.CancellationReason.Error:
                # print("Error details: {}".format(cancellation_details.error_details))
                # print("Did you set the speech resource key and region values?")
                # break  # Exit the loop in case of an error



# def recognize_from_file():
    # # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    # speech_config = speechsdk.SpeechConfig(subscription = '', region= 'australiaeast')
    # speech_config.speech_recognition_language="en-US"

    # audio_config = speechsdk.audio.AudioConfig(filename="katiesteve.wav")
    # conversation_transcriber = speechsdk.transcription.ConversationTranscriber(speech_config=speech_config, audio_config=audio_config)

    # transcribing_stop = False

    # def stop_cb(evt: speechsdk.SessionEventArgs):
        # #"""callback that signals to stop continuous recognition upon receiving an event `evt`"""
        # print('CLOSING on {}'.format(evt))
        # nonlocal transcribing_stop
        # transcribing_stop = True

    # # Connect callbacks to the events fired by the conversation transcriber
    # conversation_transcriber.transcribed.connect(conversation_transcriber_transcribed_cb)
    # conversation_transcriber.session_started.connect(conversation_transcriber_session_started_cb)
    # conversation_transcriber.session_stopped.connect(conversation_transcriber_session_stopped_cb)
    # conversation_transcriber.canceled.connect(conversation_transcriber_recognition_canceled_cb)
    # # stop transcribing on either session stopped or canceled events
    # conversation_transcriber.session_stopped.connect(stop_cb)
    # conversation_transcriber.canceled.connect(stop_cb)

    # conversation_transcriber.start_transcribing_async()

    # # Waits for completion.
    # while not transcribing_stop:
        # time.sleep(.5)

    # conversation_transcriber.stop_transcribing_async()

# Main

try:
    rosieText = textGen()
    from_mic()
except Exception as err:
    print("Encountered exception. {}".format(err))
