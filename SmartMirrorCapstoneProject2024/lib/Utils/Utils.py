import os

talkingDuration = 8
startWordToPlayYoutubeVid = "bật youtube"
onListeningErrorText = "Âm thanh không rõ ràng, vui lòng thủ lại."

def checkStartWithString(start : str, string : str) -> bool:
    return string.lower().startswith(start.lower())

def playNotificationSound(isIntro: bool):
    command = ("ffplay -nodisp -autoexit ")
    if isIntro:
        os.system("{} /home/kinh/DoAn/SmartMirrorCapstoneProject2024/static/asset/start_talking_notifications-sound.mp3".format(command))
    else:
        os.system("{} /home/kinh/DoAn/SmartMirrorCapstoneProject2024/static/asset/stop_talking_notifications-sound.mp3".format(command))

if __name__ == "__main__":
    print(checkStartWithString("bật", "bẬT youtube"))
    from time import sleep
    playNotificationSound(isIntro=True)
    sleep(4)
    playNotificationSound(isIntro=False)
