from flask import Flask,render_template
import sys
from flask_socketio import SocketIO
import threading
from lib.HandGestureControl import Main
import json
from lib.LlmChatBot.LlmChatBot import AskChatBot
from lib.SpeechToTextModule.SpeechToTextModule import SpeechToText
from lib.Utils import Utils
from model.YoutubeVidModel import YoutubeVidList, YoutubeVid
from pynput.keyboard import Listener, KeyCode
from lib.Utils import Utils
from lib.NewsProvider.NewsProvider import NewsProvider
from lib.RecommendationSystem.RecommendationSystem import RecommendationSystem
from lib.ImgProvider.ImgProvider import ImgProvider
import time
import os
import re, requests, urllib.parse, urllib.request
from bs4 import BeautifulSoup

# reactive python module
import multiprocessing
import rx
from rx.scheduler import ThreadPoolScheduler
from rx import operators as ops

#Debug logger
import logging 

# Initialize Flask.
app = Flask(__name__)
socket = SocketIO(app)


# This function is the callback when the speech to text module finished transcibing. 
# predictedText is the output if speech to text module.
def onReceiveSpeechToText(predictedText):
    predictedText = predictedText.replace("*", "")
    if Utils.checkStartWithString(start = Utils.startWordToPlayYoutubeVid, string=predictedText):
        #This will only render a text in the input form on the front end side. Nothing else.
        socket.emit("speechToTextOutPut_play", json.loads(json.dumps({ "speechToTextOutPut_play": predictedText[len(Utils.startWordToPlayYoutubeVid):]})))
        queryYoutubeVidIdAndSendToFrontEnd(predictedText[len(Utils.startWordToPlayYoutubeVid):])
    elif str(predictedText).lower() == Utils.speakAloudCmd.lower():
        socket.send("speak-aloud")
    else:
        #This will only render a text in the input form on the front end side. Nothing else.
        socket.emit("speechToTextOutPut_chatbot", json.loads(json.dumps({ "speechToTextOutPut_chatbot": predictedText})))
        chatBot.ask(str(predictedText))

def onListeningError():
    socket.emit("speechToTextOutPut_chatbot", json.loads(json.dumps({ "speechToTextOutPut_chatbot": Utils.onListeningErrorText})))
    socket.emit("chatBotAnswer", json.loads(json.dumps({ "answer": ""})))

# This function is the callback when the chat bot module finished its works. 
# chatBotAnswer is out in the form of string.
def notifier(chatBotAnswer):
    chatBotAnswer = chatBotAnswer.replace("*", "")
    socket.emit("chatBotAnswer", json.loads(json.dumps({ "answer": chatBotAnswer})))
    socket.send("speak-aloud")




def return_dict():
    return []

class MusicController:
    playOrPause = False
    currentSongIndex=1

    @staticmethod
    def playAndPause():
        
        if MusicController.playOrPause:
            socket.send("pause")
            MusicController.playOrPause = False
        else:
            socket.send("play")
            MusicController.playOrPause = True
    @staticmethod
    def nextSong():
        if MusicController.currentSongIndex < youtubeVidList.getSize():
            MusicController.currentSongIndex = MusicController.currentSongIndex + 1
        else :
            MusicController.currentSongIndex = 1
        socket.emit("youtubeSongUrl", json.loads(json.dumps({"youtubeSongUrl" : youtubeVidList.getYoutubeSongUrl(MusicController.currentSongIndex), "yt_title" : youtubeVidList.getYoutubetTitle(MusicController.currentSongIndex)})))
        
        
        
    
    @staticmethod
    def previousSong():
        if MusicController.currentSongIndex > 1:
            MusicController.currentSongIndex = MusicController.currentSongIndex - 1
            socket.emit("youtubeSongUrl", json.loads(json.dumps({"youtubeSongUrl" : youtubeVidList.getYoutubeSongUrl(MusicController.currentSongIndex), "yt_title" : youtubeVidList.getYoutubetTitle(MusicController.currentSongIndex)})))
            
            
    @staticmethod
    def updateSongMetadata():
        socket.emit( 'updateMetaData', json.loads(json.dumps(return_dict()[MusicController.currentSongIndex -1])) )    
    
    @staticmethod
    def onModeChange(curMode):
        socket.emit("gestureModeChange", json.loads(json.dumps({"gestureModeChange" : curMode})))
def onTalk(key):
    if (key == KeyCode(char="c")) and (not speechToText.isRunning()):
        print("we got key " + str(key))
        def playNotificationSound():
            Utils.playNotificationSound(isIntro=True)
            socket.send("pause")
            MusicController.playOrPause = False
            mHandGesture.stopFlag = True
            imgProvider.stopFlag = True

            time.sleep(Utils.talkingDuration)
            
            mHandGesture.stopFlag = False
            imgProvider.stopFlag = False

            Utils.playNotificationSound(isIntro=False)

        threading.Thread(target=playNotificationSound).start()
        threading.Thread(target=speechToText.start).start()
        


#Route to render GUI
@app.route('/')
def show_entries():
    
    newsProvider = NewsProvider()
    newsProvider.fetchingArticles()
    articles = newsProvider.toTitleDescriptionListDict()
    return render_template('design.html', articles = articles)

def onReceiveImage(image):
    try:
        imgProvider.stopFlag = True
        mHandGesture.stopFlag = True
        from lib.SentimentAnalysis.SentimentAnalysis import FER

        fer = FER()
        analyzer =  fer.analyzeSentiment(image)
        imgProvider.stopFlag = False
        mHandGesture.stopFlag = False
        if analyzer != None:
            topEmotion, score = analyzer
            if topEmotion == "angry" or topEmotion == "angry" or topEmotion == "disgust" or topEmotion == "fear" or topEmotion == "sad":
                recommendedSongs = getRandomSongsIndex(clusterIndex=[0,1], numberOfSongs=1)
            else:
                recommendedSongs = getRandomSongsIndex(clusterIndex=[0,1,2,3,4], numberOfSongs=1)
            print(recommendedSongs)
            
            cluster = recommendationSystem.getCluster()
            def fetchingRecommendedSongs():
                query_string = urllib.parse.urlencode({"search_query": cluster[songIndex][1]})
                formatUrl = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
                search_results = re.findall(r"watch\?v=(\S{11})", formatUrl.read().decode())

                fetchingSingleYoutubeVid(i = 0, search_results= search_results, renderToFrontEnd=False, addOrInsertRandomly="insert")

            for songIndex in recommendedSongs:
                fetchingYoutubeVidDisposable = rx.range(1).pipe(
                ops.do_action(lambda i : fetchingRecommendedSongs()),
                ops.subscribe_on(thread_pool_scheduler)
                ).subscribe(
                on_error=lambda e : print("fetching recommeded songs error, {e}"),
                on_completed=lambda c : print("fetching recommeded songs completed")
            )
    except:
        print("err in onReceiveImage \n\n\n")
        import traceback
        traceback.print_exc()
        



@socket.on('connect')
def on_connect(msg):
    print('Server received connection')
    handGestureThread = threading.Thread(target=mHandGesture.run)
    handGestureThread.start()
    queryYoutubeVidIdAndSendToFrontEnd("most viral songs")

    imgProvider.setSampleImagesCallback(onReceiveImage, Utils.imageSamplingInterval)
    threading.Thread(target=recommendationSystem.crawTrackAnalysisDataAndPredict).start()


        
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

    
    query_string = urllib.parse.urlencode({"search_query": music_name})
    formatUrl = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)

    search_results = re.findall(r"watch\?v=(\S{11})", formatUrl.read().decode())
    youtubeVidsize = len(search_results) if  len(search_results)<= 4 else 4
    def on_subscribe():
        isFetching = True
        print("start fetching youtube vid")
    def on_error(e):
        isFetching = False
        print("error :" + str(e))
    def on_completed():
        isFetching = False
        print("fetching complete")
    
    youtubeVidList.clearYoutubeVidList()
    
    if isFetching and (fetchingYoutubeVidDisposable != None):
        fetchingYoutubeVidDisposable.dispose()
        print("dispose! fetching youtube vids")
    fetchingYoutubeVidDisposable = rx.range(youtubeVidsize).pipe(
        ops.do_action(lambda i : fetchingSingleYoutubeVid(i, search_results=search_results)),
        ops.subscribe_on(thread_pool_scheduler)
        ).subscribe(
        on_error=on_error,
        on_completed=on_completed
    )
    on_subscribe()
def fetchingSingleYoutubeVid(i, search_results, renderToFrontEnd = True, addOrInsertRandomly = "add"):
    
    clip = requests.get("https://www.youtube.com/watch?v=" + "{}".format(search_results[i]))
    clip2 = "https://www.youtube.com/watch?v=" + "{}".format(search_results[i])

    inspect = BeautifulSoup(clip.content, "html.parser")
    yt_title = inspect.find_all("meta", property="og:title")
    def parseYoutubeURL( url:str)->str:
        data = re.findall(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        if data:
            return data[0]
        return ""
    if i == 0 and renderToFrontEnd:
        socket.emit("youtubeSongUrl", json.loads(json.dumps({"youtubeSongUrl" : parseYoutubeURL(clip2), "yt_title" : yt_title[0]['content']})))
    if addOrInsertRandomly == "add":
        youtubeVidList.addYoutubeVidMetadata(YoutubeVid(parseYoutubeURL(clip2), yt_title[0]['content']))
    else :
        youtubeVidList.insertRandomYoutubeVidMetadata(YoutubeVid(parseYoutubeURL(clip2), yt_title[0]['content']))
    print(youtubeVidList.getYoutubeVidList())
    

@socket.on('askAQuestion')
def onAskChatBot(msg):
    question = msg["askChatBot"]
    chatBot.ask(str(question))

def getRandomSongsIndex(clusterIndex, numberOfSongs: int):
    import random
    clusterAssocitedWithIndex = [] 
    for i, song in enumerate(recommendationSystem.getCluster()) :
        if int(song[0][0]) in clusterIndex:
            clusterAssocitedWithIndex.append(i)
    return random.sample(clusterAssocitedWithIndex, k = numberOfSongs)

if __name__ == "__main__":
    usingRealsense =  Utils.usingRealsense
    imgProvider = ImgProvider(usingRealsense)
    recommendationSystem = RecommendationSystem()
    recommendationSystem.crawTrendingSongs()

    recommendedSongs = []
    mHandGesture = Main.HandGesture(MusicController.playAndPause, MusicController.nextSong, MusicController.previousSong, MusicController.onModeChange, usingRealsense)

    
    
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

    speechToText = SpeechToText(onReceiveSpeechToText, onListeningError)


    listener = Listener(on_press = onTalk)  
    listener.start()
    print(" Start listener to listen to c press")
        
    youtubeVidList = YoutubeVidList()

    # calculate cpu count, using which will create a ThreadPoolScheduler
    thread_count = multiprocessing.cpu_count()
    thread_pool_scheduler = ThreadPoolScheduler(thread_count)
    
    isFetching = False
    fetchingYoutubeVidDisposable =  None

    chatBot = AskChatBot()
    chatBot.setNotifier(notifier)


    app.run(host="localhost", port=5000)
    socket.run(app)
    
