from flask import Flask,render_template
import sys
from flask_socketio import SocketIO
from time import sleep
import threading
from lib.HandGestureControl import Main
import json
from lib.LlmChatBot.LlmChatBot import AskChatBot
from lib.SpeechToTextModule.SpeechToTextModule import SpeechToText
from lib.Utils import Utils

#Debug logger
import logging 
root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

mutex = threading.Lock()

# Initialize Flask.
app = Flask(__name__)
socket = SocketIO(app)

# This function is the callback when the speech to text module finished transcibing. 
# predictedText is the output if speech to text module.
def onReceiveSpeechToText(predictedText):
    print(predictedText)
    # change "start =" later
    # if Utils.checkStartWithString(start= "where", string=predictedText) :
    #     # if Utils.checkStartWithString(start="", string=):
    #     #This will only render a text in the input form on the front end side. Nothing else.
    #     socket.emit("speechToTextOutPut_chatbot", json.loads(json.dumps({ "speechToTextOutPut_chatbot": predictedText})))

    #     # This will generate the answer and then automatically render to the text box on the front end side.
    #     chatBot.ask(str(predictedText))
    if Utils.checkStartWithString(start="play", string=predictedText):
        #This will only render a text in the input form on the front end side. Nothing else.
        socket.emit("speechToTextOutPut_play", json.loads(json.dumps({ "speechToTextOutPut_play": predictedText[len("play"):]})))
        queryYoutubeVidIdAndSendToFrontEnd(predictedText[len("play"):])
    else:
        #This will only render a text in the input form on the front end side. Nothing else.
        socket.emit("speechToTextOutPut_chatbot", json.loads(json.dumps({ "speechToTextOutPut_chatbot": predictedText})))

        # This will generate the answer and then automatically render to the text box on the front end side.
        chatBot.ask(str(predictedText))


# This function is the callback when the chat bot module finished its works. 
# chatBotAnswer is out in the form of string.
def notifier(chatBotAnswer):
    socket.emit("chatBotAnswer", json.loads(json.dumps({ "answer": chatBotAnswer})))
chatBot = AskChatBot()
chatBot.setNotifier(notifier)



def return_dict():
    dict_here = []
    return dict_here

class MusicController:
    playOrPause = False
    currentSongIndex=1
    debounceTime = 0.3

    @staticmethod
    def playAndPause():
        
        if MusicController.playOrPause:
            socket.send("pause")
            MusicController.playOrPause = False
        else:
            socket.send("play")
            MusicController.playOrPause = True
        sleep(MusicController.debounceTime)
    @staticmethod
    def nextSong():
        if MusicController.currentSongIndex < len(return_dict()):
            MusicController.currentSongIndex = MusicController.currentSongIndex + 1
        else :
            MusicController.currentSongIndex = 1
        x =  '''{ "type":"changeSong", "songId":"''' + str(MusicController.currentSongIndex) + '''"}'''
        socket.emit( 'message', json.loads(x))
        
        
        sleep(MusicController.debounceTime)
    
    @staticmethod
    def previousSong():
        if MusicController.currentSongIndex > 1:
            MusicController.currentSongIndex = MusicController.currentSongIndex - 1
            x =  '''{ "type":"changeSong", "songId":"''' + str(MusicController.currentSongIndex) + '''"}'''
            socket.emit( 'message', json.loads(x))
            
        sleep(MusicController.debounceTime)
    @staticmethod
    def updateSongMetadata():
        socket.emit( 'updateMetaData', json.loads(json.dumps(return_dict()[MusicController.currentSongIndex -1])) )    
        # socket.send("asdnajsdk")



#Route to render GUI
@app.route('/')
def show_entries():
    general_Data = {
        'title': 'Music Player'}
    return render_template('design.html', **general_Data)

@socket.on('connect')
def on_connect(msg):
    print('Server received connection')
    mHandGesture = Main.HandGesture(MusicController.playAndPause, MusicController.nextSong, MusicController.previousSong)
    handGestureThread = threading.Thread(target=mHandGesture.run)
    handGestureThread.start()

@socket.on("userWantToTak")
def talk(msg):
    speechToText = SpeechToText(onReceiveSpeechToText)
    if (msg["userWantToTak"]) and  (not speechToText.isRunning()):
        print(msg["userWantToTak"])
        with mutex:
            speechToText.start()
        
@socket.on('message')
def onSongChange(msg):
    if msg == "onSongChange":
        MusicController.updateSongMetadata()
@socket.on('searchForSong')
def onSearchingForYoutubeSong(msg):
    # socket.send("server received message : " + msg["songName"])
    music_name = msg["songName"]
    queryYoutubeVidIdAndSendToFrontEnd(music_name)
def queryYoutubeVidIdAndSendToFrontEnd(music_name):
    import re, requests, urllib.parse, urllib.request
    from bs4 import BeautifulSoup

    
    query_string = urllib.parse.urlencode({"search_query": music_name})
    formatUrl = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)

    search_results = re.findall(r"watch\?v=(\S{11})", formatUrl.read().decode())
    clip = requests.get("https://www.youtube.com/watch?v=" + "{}".format(search_results[0]))
    clip2 = "https://www.youtube.com/watch?v=" + "{}".format(search_results[0])

    inspect = BeautifulSoup(clip.content, "html.parser")
    yt_title = inspect.find_all("meta", property="og:title")
    def parseYoutubeURL( url:str)->str:
        data = re.findall(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        if data:
            return data[0]
        return ""

    socket.emit("youtubeSongUrl", json.loads(json.dumps({"youtubeSongUrl" : parseYoutubeURL(clip2), "yt_title" : yt_title[0]['content']})))

    

@socket.on('askAQuestion')
def onAskChatBot(msg):
    question = msg["askChatBot"]
    chatBot.ask(str(question))

if __name__ == "__main__":
    app.run(host="localhost", port=5000)
    socket.run(app)
    
