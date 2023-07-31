import speech_recognition as sr
import pyttsx3
import tkinter as tk
import threading
import webbrowser

class VoiceAssistant:

    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("500x500")
        self.frame = tk.Frame(master=self.root, bg='#131112').pack()
        self.label = tk.Label(master=self.frame, text= "Voice Recognition By Sean Diaz", bg='#F7F7FF').pack()
        self.listening_label = tk.Label(master=self.root, text="NOT LISTENING", font=('', 30))
        self.listening_label.pack()
        self.todoList = []
        self.suggestions = ["Search","add to list","text"]
        self.suggestion_index = 0
        self.r = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.audio_text = ""
        self.listening_event = threading.Event()
        self.suggestion = tk.Label(self.root, text="Suggested Commands", font=("Arial", 24))
        self.suggestion.pack(side=tk.LEFT, fill=tk.Y)
        self.suggestion_label = tk.Label(self.root, text=self.suggestions[self.suggestion_index])
        self.suggestion_label.pack(side=tk.LEFT, fill=tk.Y)
        self.rotate_suggestions()
        button = tk.Button(master=self.frame, text="Talk to me",command=self.start_listening).pack()
        self.root.mainloop()

    def rotate_suggestions(self):
        # Update the suggestion
        self.suggestion_index = (self.suggestion_index + 1) % len(self.suggestions)
        self.suggestion_label.config(text=self.suggestions[self.suggestion_index])

        # Schedule the next update
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
                self.engine.say("Im sorry I do not understand, please pick a command from the list")
                self.engine.runAndWait()
                self.listening_label.config(text=error_message)

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
            self.todo_list.append(item)
            self.engine.say("Added " + item + " to your to-do list")
            self.engine.runAndWait()
        elif "text message" in audio:
            self.engine.say("What message would you like to send?")
            self.engine.runAndWait()
            self.start_listening()

    def main_loop(self):
        self.root.mainloop()

if __name__ == '__main__':
    assistant = VoiceAssistant()
    assistant.main_loop()