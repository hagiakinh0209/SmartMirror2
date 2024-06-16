import os


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

talkingDuration = 8
startWordToPlayYoutubeVid = "bật youtube"
onListeningErrorText = "Âm thanh không rõ ràng, vui lòng thủ lại."
speakAloudCmd = "Đọc thành tiếng"

def checkStartWithString(start : str, string : str) -> bool:
    return string.lower().startswith(start.lower())

def playNotificationSound(isIntro: bool):
    command = ("ffplay -nodisp -autoexit ")
    if isIntro:
        os.system("{} {}/start_talking_notifications-sound.mp3".format(command, __location__))
    else:
        os.system("{} {}/stop_talking_notifications-sound.mp3".format(command, __location__))

if __name__ == "__main__":
    print(checkStartWithString("bật", "bẬT youtube"))
    from time import sleep
    playNotificationSound(isIntro=True)
    sleep(4)
    playNotificationSound(isIntro=False)
