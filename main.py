import tkinter as tk
from googletrans import Translator
import speech_recognition as sr
from PIL import Image, ImageTk
from tkinter import Toplevel
import threading
from gtts import gTTS
import os
import tempfile
import pygame

is_listening = False

def on_text_change(event=None):
    global translate_job
    if translate_job is not None:
        window.after_cancel(translate_job)
    translate_job = window.after(500, translate_text)

def translate_text():
    global translate_job
    translate_job = None
    original_text = text_input.get("1.0", tk.END).strip()
    if not original_text:
        text_output.delete("1.0", tk.END)
        return

    try:
        detected_lang = translator.detect(original_text).lang
        dest_lang = 'cs' if detected_lang == 'en' else 'en'
        translation = translator.translate(original_text, dest=dest_lang)
        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, translation.text)
    except Exception as e:
        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, f"Chyba při překladu: {e}")

def toggle_listening():
    global is_listening
    if is_listening:
        # Ukončení naslouchání
        is_listening = False
        record_button.config(text="Nahrát hlas")
    else:
        # Spuštění naslouchání v samostatném vlákně
        is_listening = True
        record_button.config(text="Zastavit nahrávání")
        threading.Thread(target=record_voice, daemon=True).start()

def record_voice():
    global is_listening
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        while is_listening:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                voice_text = recognizer.recognize_google(audio)
                text_input.delete("1.0", tk.END)
                text_input.insert(tk.END, voice_text)
                translate_text()
            except sr.WaitTimeoutError:
                continue  # Pokračovat v naslouchání, pokud není zachycen žádný hlas
            except sr.UnknownValueError:
                pass  # Není rozpoznán žádný hlas
            except sr.RequestError as e:
                pass  # Chyba připojení


def speak(text, lang):
    try:
        # Vytvoření názvu dočasného souboru
        temp_file_name = tempfile.mktemp(suffix='.mp3')
        tts = gTTS(text=text, lang=lang)
        tts.save(temp_file_name)

        # Inicializace pygame a přehrání zvuku
        pygame.mixer.init()
        pygame.mixer.music.load(temp_file_name)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():  # Čekání na dokončení přehrávání
            pygame.time.Clock().tick(10)

        # Smazání dočasného souboru
        os.remove(temp_file_name)
    except Exception as e:
        print(f"Chyba při převodu textu na řeč: {e}")

def translate_and_speak():
    translated_text = text_output.get("1.0", tk.END).strip()
    if not translated_text:
        return

    # Detekujeme jazyk originálního textu, ne přeloženého
    original_text = text_input.get("1.0", tk.END).strip()
    detected_lang = translator.detect(original_text).lang
    speak_lang = 'en' if detected_lang == 'cs' else 'cs'
    speak(translated_text, speak_lang)


def open_settings():
    settings_window = Toplevel()
    settings_window.title("Nastavení")
    settings_label = tk.Label(settings_window, text="Zde můžete přidat nastavení aplikace.")
    settings_label.pack(pady=20, padx=20)

# Inicializace Google Translator
translator = Translator()

# Vytvoření hlavního okna
window = tk.Tk()
window.title("Překladač v reálném čase")


# Načtení ikony pro tlačítko nastavení
try:
    settings_icon_image = Image.open("gear.png")  # Nahraďte cestou k vaší ikoně ozubeného kola
    settings_icon = ImageTk.PhotoImage(settings_icon_image.resize((20, 20), Image.Resampling.LANCZOS))
except IOError:
    print("Nelze načíst obrázek pro ikonu nastavení.")
    settings_icon = None

# Inicializace proměnné pro časovač
translate_job = None

# Tlačítko pro nahrávání hlasu
record_button = tk.Button(window, text="Nahrát hlas", command=toggle_listening)
record_button.pack(pady=10)

# Textové pole pro vstupní text
text_input = tk.Text(window, height=10, width=50)
text_input.pack(pady=10)
text_input.bind("<KeyRelease>", on_text_change)

# Textové pole pro přeložený text
text_output = tk.Text(window, height=10, width=50)
text_output.pack(pady=10)

# Tlačítko pro přehrání hlasu
speak_button = tk.Button(window, text="Přehrát hlas", command=translate_and_speak)
speak_button.pack(pady=10)

# Tlačítko pro nastavení
settings_button = tk.Button(window, image=settings_icon, command=open_settings)
settings_button.pack(pady=10)

# Spuštění aplikace
window.mainloop()
