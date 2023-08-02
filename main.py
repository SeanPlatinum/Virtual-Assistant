import speech_recognition as sr
import pyttsx3
import tkinter as tk
import threading
import webbrowser
from twilio.rest import Client
import time
class Settings:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")

        # Create labels and entry fields
        self.sid_label = tk.Label(self.window, text="Twilio Account SID:")
        self.sid_label.pack()
        self.sid_entry = tk.Entry(self.window)
        self.sid_entry.pack()

        self.token_label = tk.Label(self.window, text="Twilio Auth Token:")
        self.token_label.pack()
        self.token_entry = tk.Entry(self.window, show="*")  # Hide the entered token
        self.token_entry.pack()

        self.phone_label = tk.Label(self.window, text="Twilio Phone Number:")
        self.phone_label.pack()
        self.phone_entry = tk.Entry(self.window)
        self.phone_entry.pack()

        # Add a save button
        self.save_button = tk.Button(self.window, text="Save", command=self.save_settings)
        self.save_button.pack()

    def save_settings(self):
        self.account_sid = self.sid_entry.get()
        self.auth_token = self.token_entry.get()
        self.phone_number = self.phone_entry.get()
        self.parent.twilio_account_sid = self.account_sid
        self.parent.twilio_auth_token = self.auth_token
        self.parent.twilio_phone_number = self.phone_number
        print("Settings saved:")  # Debugging print statement
        print(f"SID: {self.parent.twilio_account_sid}")
        print(f"Token: {self.parent.twilio_auth_token}")
        print(f"Phone: {self.parent.twilio_phone_number}")

        # Close the settings window
        self.window.destroy()

class VoiceAssistant:

    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("500x500")
        self.command_frame = tk.Frame(self.root, bg='#1E2D2F')
        self.command_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.suggestion_frame = tk.Frame(self.root, bg='#1E2D2F')
        self.suggestion_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.label = tk.Label(master=self.command_frame, text="Voice Recognition By Sean Diaz", bg='#F7F7FF')
        self.label.pack(pady=10)
        self.listening_label = tk.Label(master=self.command_frame, text="NOT LISTENING", font=('', 30),bg='#1E2D2F')
        self.listening_label.pack(pady=10)
        self.button = tk.Button(master=self.command_frame, text="Talk to me", command=self.start_listening)
        self.button.pack(pady=10)
        self.suggestions = ["Search", "add to list", "text"]
        self.suggestion_index = 0
        settings_button = tk.Button(self.root, text="Settings", command=self.open_settings)
        settings_button.pack()
        self.suggestion = tk.Label(self.suggestion_frame, text="Suggested Commands", font=("Arial", 24),bg='#1E2D2F')
        self.suggestion.pack(pady=10)

        self.suggestion_label = tk.Label(self.suggestion_frame, text=self.suggestions[self.suggestion_index],
                                         font=("", 20))
        self.suggestion_label.pack(pady=10)
        self.rotate_suggestions()
        self.todolist = []
        self.r = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.audio_text = ""
        self.listening_event = threading.Event()
        self.twilio_account_sid = 'ACce3fb82c81b76acdb69c37bb5bcdf429'
        self.twilio_auth_token = 'b565f8c6209a9cec48dc4d37c4dbab22'
        self.twilio_phone_number = '+18552741255'
        self.root.mainloop()

    def open_settings(self):
        self.settings = Settings(self)

    def rotate_suggestions(self):
        self.suggestion_index = (self.suggestion_index + 1) % len(self.suggestions)
        self.suggestion_label.config(text=self.suggestions[self.suggestion_index])
        self.root.after(3000, self.rotate_suggestions)  # 3000 milliseconds = 3 seconds
    def start_listening(self):
        if self.listening_event.is_set(): #true
            self.listening_event.clear()  # Stop any currently running listening_loop // make thread event false
            self.listening_label.config(text="WAITING")
            self.engine.say("processing")
            self.engine.runAndWait()
            self.root.update()
        else:
            self.listening_event.set()  # Start a new listening_loop // initiated as false
            self.engine.say("Go Ahead")
            self.engine.runAndWait()
            self.listening_label.config(text="LISTENING")
            self.root.update()
            threading.Thread(target=self.listening_loop).start()
    def quick_get_audio(self):
        with sr.Microphone() as source:
            audio = self.r.listen(source)
        try:
            return self.r.recognize_google(audio)
        except sr.UnknownValueError as e:
            error_message = str(e) if str(e) else "Unable to recognize speech"
            self.engine.say("I'm sorry I do not understand, please try again from the beginning")
            self.engine.runAndWait()
            self.listening_label.config(text=error_message)

    def listening_loop(self):
        while self.listening_event.is_set():
            with sr.Microphone() as source:
                audio = self.r.listen(source)
            try:
                self.audio_text = self.r.recognize_google(audio)
                self.engine.say(f"okay you said {self.audio_text}")
                self.engine.runAndWait()
                self.response(self.audio_text)
            except sr.UnknownValueError as e:
                error_message = str(e) if str(e) else "Unable to recognize speech"
                self.engine.say("I'm sorry I do not understand, please pick a command from the list")
                self.engine.runAndWait()
                self.listening_label.config(text=error_message)
            self.listening_event.clear()

    def send_text(self, message, to):
        client = Client(self.twilio_account_sid, self.twilio_auth_token)
        message = client.messages.create(
            body=message,
            from_=self.twilio_phone_number,
            to=to
        )
        return message.sid
    def response(self, audio):
        if "search" in audio:
            self.engine.say("heres what I found")
            self.engine.runAndWait()
            search = audio.split("search",1)[1]
            url = "https://www.google.com/search?q=" + search
            webbrowser.open(url)
        elif "add to list" in audio:
            self.engine.say("making you a list now")
            self.engine.runAndWait()
            item = audio.split("add to list", 1)[1].strip()
            self.todolist.append(item)
            self.engine.say("Added " + item + " to your to-do list")
            self.engine.runAndWait()
        elif "text message" in audio:
            self.engine.say("formulating your message now")
            self.engine.runAndWait()
            text = audio.split("text message",1)[1].strip()
            self.engine.say("who would you like to send this message to?")
            self.engine.runAndWait()
            recipient = self.quick_get_audio()
            self.send_text(text, recipient)
            self.engine.say("message sent")
            self.engine.runAndWait()
            time.sleep(3)



    def main_loop(self):
        self.root.mainloop()

if __name__ == '__main__':
    assistant = VoiceAssistant()
    assistant.main_loop()