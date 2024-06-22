from random import randrange

class YoutubeVid:
    def __init__(self, youtubeVidUrl, yt_title):
        self.youtubeVidUrl = youtubeVidUrl
        self.yt_title = yt_title
    def getYoutubeVidUrl(self):
        return self.youtubeVidUrl
    def getYoutubetTitle(self):
        return self.yt_title
    def __str__(self) -> str:
        return "url = {0}; title = {1}".format(self.getYoutubeVidUrl, self.getYoutubetTitle)


class YoutubeVidList :
    def __init__(self) :
        self.youtubeVidList = []
    def addYoutubeVidMetadata(self, youtubeVid : YoutubeVid):
        self.youtubeVidList.append(youtubeVid)
    def insertRandomYoutubeVidMetadata(self, youtubeVid : YoutubeVid):
        self.__random_insert(self.youtubeVidList, youtubeVid)
    def getYoutubeSongUrl(self, position):
        return self.youtubeVidList[position].getYoutubeVidUrl()
    def getYoutubetTitle(self, position):
        return self.youtubeVidList[position].getYoutubetTitle()
    def getSize(self):
        return len(self.youtubeVidList)
    def getYoutubeVidList(self):
        return self.youtubeVidList
    def clearYoutubeVidList(self):
        self.youtubeVidList = []
    def __random_insert(self, lst, item):
        lst.insert(randrange(len(lst)+1), item)


if __name__ == "__main__":
    youtubeVidList = YoutubeVidList()
    youtubeVidList.addYoutubeVidMetadata(YoutubeVid("url1", "title1"))
    youtubeVidList.addYoutubeVidMetadata(YoutubeVid("url2", "title2"))
    youtubeVidList.addYoutubeVidMetadata(YoutubeVid("url3", "title3"))

    print("size ", youtubeVidList.getSize())
    print("url 2 ", youtubeVidList.getYoutubeSongUrl(2))
    print("title 2", youtubeVidList.getYoutubetTitle(2))