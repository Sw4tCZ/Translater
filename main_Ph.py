import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
import pygame
from googletrans import Translator

# Inicializace komponent
recognizer = sr.Recognizer()
translator = Translator()

def speak(text, lang):
    try:
        temp_file_name = tempfile.mktemp(suffix='.mp3')
        tts = gTTS(text=text, lang=lang)
        tts.save(temp_file_name)
        pygame.mixer.init()
        pygame.mixer.music.load(temp_file_name)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        os.remove(temp_file_name)
    except Exception as e:
        print(f"Chyba při převodu textu na řeč: {e}")

def listen_and_translate(from_lang, to_lang):
    with sr.Microphone() as source:
        print(f"Mluvte nyní ({from_lang}):")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language=from_lang)
            print(f"Rozpoznaný text: {text}")
            translated_text = translator.translate(text, src=from_lang, dest=to_lang).text
            print(f"Přeložený text: {translated_text}")
            speak(translated_text, to_lang)
        except sr.UnknownValueError:
            print("Nerozpoznal jsem hlas.")
        except sr.RequestError as e:
            print(f"Chyba připojení: {e}")

# Proces překladu z češtiny do angličtiny
listen_and_translate('cs', 'en')

# Proces překladu z angličtiny do češtiny (odkomentujte pro použití)
# listen_and_translate('en', 'cs')
