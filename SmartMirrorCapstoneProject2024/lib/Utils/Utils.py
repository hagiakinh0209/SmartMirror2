import os

talkingDuration = 8

def checkStartWithString(start : str, string : str) -> bool:
    return string.lower().startswith(start.lower())

def playNotificationSound(isIntro: bool):
    command = ("ffplay -nodisp -autoexit ")
    if isIntro:
        os.system("{} /home/kinh/DoAn/SmartMirrorCapstoneProject2024/static/asset/start_talking_notifications-sound.mp3".format(command))
    else:
        os.system("{} /home/kinh/DoAn/SmartMirrorCapstoneProject2024/static/asset/stop_talking_notifications-sound.mp3".format(command))

if __name__ == "__main__":
    from time import sleep
    playNotificationSound(isIntro=True)
    sleep(4)
    playNotificationSound(isIntro=False)
