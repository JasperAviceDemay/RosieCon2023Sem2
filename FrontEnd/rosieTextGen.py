import json
import requests
import html
import os.path
from datetime import datetime

class textGen:
    #self.textGenHost="localhost:5000"
    self.textGenHost='52.62.118.55:7860'
    lastResponse = None
    history = {'internal': [], 'visible': []}
    def __init__(self):
        self.logPath = f"{os.path.dirname(os.path.abspath(__file__))}/logs"
        if not os.path.exists(self.logPath):
            os.makedirs(self.logPath)

        logName = f"log-{datetime.today().strftime('%Y-%m-%d')}"

        self.logFile = os.path.abspath(f"{self.logPath}/{logName}.json")
        print(self.logFile)
        if os.path.exists(self.logFile):
            with open(self.logFile, "r") as f:
                self.history = json.load(f)

            f.close()
        

    def textGen(self, input):
        request = {
            'user_input': input,
            'max_new_tokens': 250,
            'auto_max_new_tokens': False,
            'max_tokens_second': 0,
            'history': self.history,
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

        response = requests.post(f"http://{self.textGenHost}/api/v1/chat", json=request)
        if response.status_code == 200:
            result = html.unescape(response.json()['results'][0]['history']['visible'][-1][1])
            self.history =  response.json()['results'][0]['history']
            self.lastResponse = result
            self.__saveHistory()
            return result
        
    def __saveHistory(self):
        with open(self.logFile, 'w') as f:
            json.dump(self.history, f, indent=4)

        f.close()


if __name__ == '__main__':
    txt = textGen()
    while(True):
        print("Rosie: " + txt.textGen(input("You: ")))
