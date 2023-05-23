import json
import time
import pyttsx3, pyaudio, vosk
import requests

tts = pyttsx3.init('sapi5')
rate = tts.getProperty('rate') #Скорость произношения
tts.setProperty('rate', rate-40)
voices = tts.getProperty('voices')
tts.setProperty('voices', 'en')

for voice in voices:
    print(voice.name)
    if voice.name == 'Microsoft Zira Desktop - English (United States)':
        tts.setProperty('voice', voice.id)

model = vosk.Model('model_small_en')
record = vosk.KaldiRecognizer(model, 16000)
aud = pyaudio.PyAudio()
stream = aud.open(format=pyaudio.paInt16,
                 channels=1,
                 rate=16000,
                 input=True,
                 frames_per_buffer=8000)
stream.start_stream()


def listen():
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if record.AcceptWaveform(data) and len(data) > 0:
            answer = json.loads(record.Result())
            if answer['text']:
                yield answer['text']


def speak(say):
    tts.say(say)
    print(say)
    tts.runAndWait()


#speak('starting')
speak('Hello, I am here to tell you some jokes...')

prev_data = []
data = []
for text in listen():
    if text in ['close','bye','quit']:
        quit()
    elif text in ['tell joke','tell me a joke','tell me joke','joke','laugh me','next joke','make me laugh','next one','another one']:
        res = requests.get("https://v2.jokeapi.dev/joke/Any")
        prev_data = data
        data = res.json()
        if data['type'] == 'twopart':
            speak(data['setup'])
            time.sleep(1)
            speak(data['delivery'])
        elif data['type'] == 'single':
            speak(data['joke'])

    elif text in ['previous joke','previous one','previous']:
        if prev_data != []:
            if prev_data['type'] == 'twopart':
                speak(prev_data['setup'])
                time.sleep(1)
                speak(prev_data['delivery'])
            elif prev_data['type'] == 'single':
                speak(prev_data['joke'])
            prev_data = []
        else:
            speak('Sorry, I do not remember')

    elif text in ['repeat','repeat please','again','say it again']:
        if data['type'] == 'twopart':
            speak(data['setup'])
            time.sleep(1)
            speak(data['delivery'])
        elif data['type'] == 'single':
            speak(data['joke'])

    elif text in ['laugh']:
        speak('hahahahahahahaha')
    else:
        speak("Sorry, I did not recogize command. I only heared "+text)
