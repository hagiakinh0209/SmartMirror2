import speech_recognition as sr

class SpeechToText:
    def __init__(self, onReceiveSpeechToText) -> None:
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.onReceiveSpeechToText = onReceiveSpeechToText
        self.__isRunning = False

    

    def start(self):
        self.__isRunning = True
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(self.mic, timeout=3)
            self.onReceiveSpeechToText(self.recognizer.recognize(audio)) #Output
        self.__isRunning = False

    def isRunning(self):
        return self.__isRunning