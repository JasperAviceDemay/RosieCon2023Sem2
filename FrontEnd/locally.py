import os
import re
import time
#from rosieTextGen import textGen

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print("""
    Importing the Speech SDK for Python failed.
    Refer to
    https://docs.microsoft.com/azure/cognitive-services/speech-service/quickstart-python for
    installation instructions.
    """)
    import sys
    sys.exit(1)


keywords = ['Hey, Rosie', 'Hey Rosie', 'Hi, Rosie', 'Hi Rosie']
endwords = ['Thank you, Rosie.', 'End conversation.', 'That will be all.']
AzureSpeechKey, AzureSpeechRegion = os.environ.get('AZURESPEECHKEY'), os.environ.get('AZUREREGION')
speech_config = speechsdk.SpeechConfig(subscription=AzureSpeechKey, region=AzureSpeechRegion)
#audio config
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
#default voice can be change or custom
speech_config.speech_synthesis_voice_name='en-US-JennyNeural'
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
speech_config.set_profanity(speechsdk.ProfanityOption.Removed)



def speech_recognize_once_with_auto_language_detection_from_mic():
    """performs one-shot speech recognition from the default microphone with auto language detection"""
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

    # create the auto detection language configuration with the potential source language candidates
    auto_detect_source_language_config = \
        speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["zh-CN", "en-US"])
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, auto_detect_source_language_config=auto_detect_source_language_config)
    result = speech_recognizer.recognize_once()

    # Check the result
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        auto_detect_source_language_result = speechsdk.AutoDetectSourceLanguageResult(result)
        print("Recognized: {} in language {}".format(result.text, auto_detect_source_language_result.language))
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            
            
def speech_recognize_keyword_locally_from_microphone():
    print('local run')
    model = speechsdk.KeywordRecognitionModel("92687bb9-1131-4b6d-b25d-0f9a7dd608bb.table")
    keyword = "Hey Rosie"
    keyword_recognizer = speechsdk.KeywordRecognizer()

    keyword_detected = False

    def recognized_cb(evt):
        nonlocal keyword_detected
        result = evt.result
        if result.reason == speechsdk.ResultReason.RecognizedKeyword:
            print("RECOGNIZED KEYWORD: {}".format(result.text))
            keyword_detected = True

    def canceled_cb(evt):
        result = evt.result
        if result.reason == speechsdk.ResultReason.Canceled:
            print('CANCELED: {}'.format(result.cancellation_details.reason))

    keyword_recognizer.recognized.connect(recognized_cb)
    keyword_recognizer.canceled.connect(canceled_cb)

    result_future = keyword_recognizer.recognize_once_async(model)
    print('Say something starting with "{}" followed by whatever you want...'.format(keyword))
    result = result_future.get()

    if result.reason == speechsdk.ResultReason.RecognizedKeyword:
        time.sleep(2)
        result_stream = speechsdk.AudioDataStream(result)
        result_stream.detach_input()

        save_future = result_stream.save_to_wav_file("AudioFromRecognizedKeyword.wav")
        print('Saving file...')
        #saved = save_future.get()
        #stop_future = keyword_recognizer.stop_recognition_async()
        #print('Stopping...')
        #stopped = stop_future.get()
    return keyword_detected

def from_mic():
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    print("Speak into your microphone.")
    to_speaker('Keyword Detected, conversation activated. Please ask your question')
    while True:
        result = speech_recognizer.recognize_once_async().get()
        transcription = result.text.strip()
        print(transcription)
        to_speaker(transcription)
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Recognized: {}".format(transcription))
            # Add your logic here, if needed
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


#try:
    #rosieText = textGen()
    
if speech_recognize_keyword_locally_from_microphone():
    print ('open mic')
    from_mic()
print("Program continues here.")
#except Exception as err:
#    print("Encountered exception. {}".format(err))
    
    
    
