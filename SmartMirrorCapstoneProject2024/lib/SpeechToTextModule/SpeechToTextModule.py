import speech_recognition as sr
import traceback

class SpeechToText:
    def __init__(self, onReceiveSpeechToText) -> None:
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.onReceiveSpeechToText = onReceiveSpeechToText
        self.__isRunning = False

    

    def start(self):
        self.__isRunning = True
        try:
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.record(self.mic, duration=5)
                self.onReceiveSpeechToText(self.recognizer.recognize(audio)) #Output
        except Exception:
            print(traceback.format_exc())
        self.__isRunning = False
        

    def isRunning(self):
        return self.__isRunning