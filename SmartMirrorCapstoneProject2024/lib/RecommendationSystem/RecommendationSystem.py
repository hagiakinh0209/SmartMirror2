import requests
from bs4 import BeautifulSoup
import subprocess
import json
from sklearn.utils._openmp_helpers import _openmp_effective_n_threads
import pickle
import os
import numpy as np
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
class RecommendationSystem:
    def __init__(self) -> None:
        kmeans = os.path.join(__location__, 'cluster.sav')
        self.loaded_cluster_model = pickle.load(open(kmeans, 'rb'))
        self.loaded_cluster_model._n_threads = _openmp_effective_n_threads()
        if not os.path.isfile("songsCluster.csv"):
            self.getAccessToken()

    def get_content(self, url):
        
        """
        Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
        Accept-Encoding:gzip, deflate, sdch
        Accept-Language:en-US,en;q=0.8,vi;q=0.6
        Connection:keep-alive
        Cookie:__ltmc=225808911; __ltmb=225808911.202893004; __ltma=225808911.202893004.204252493; _gat=1; __RC=4; __R=1; _ga=GA1.3.938565844.1476219934; __IP=20217561; __UF=-1; __uif=__ui%3A-1%7C__uid%3A877575904920217840%7C__create%3A1475759049; __tb=0; _a3rd1467367343=0-9
        Host:dantri.com.vn
        Referer:http://dantri.com.vn/su-kien.htm
        Upgrade-Insecure-Requests:1
        User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36
        """
        
        domains = url.split('/')
        if (domains.__len__() >= 3): domain = domains[2]
            
        headers = dict()
        headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        headers['Accept-Encoding'] = 'gzip, deflate, sdch'
        headers['Accept-Language'] = 'en-US,en;q=0.8,vi;q=0.6'
        headers['Connection'] = 'keep-alive'
        headers['Host'] = domain
        headers['Referer'] = url
        headers['Upgrade-Insecure-Requests'] = '1'
        headers[
            'User-Agent'] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0"
        try:
            
            r = requests.get(url, headers=headers, timeout=10)
            r.encoding  = 'utf-8' 
            r.close()
            return r.text#.encode('utf-8', 'inorge')
        except:
            # print('Exception'+ str(e))
            return None
    def getAccessToken(self):
        getSessionTokenCmd= '''
                        curl -X POST "https://accounts.spotify.com/api/token" \\
                            -H "Content-Type: application/x-www-form-urlencoded" \\
                            -d "grant_type=client_credentials&client_id=afff1980293440d5be9c61212ac13ef6&client_secret=e9b699b7f8eb4767966c93d62db5d804"
                        '''
        output = subprocess.check_output(getSessionTokenCmd, shell=True)     
        self.accessToken = json.loads(output.decode("utf-8"))["access_token"]
        return self.accessToken
    

    def crawTrendingSongs(self):

        rawContent = self.get_content("https://kworb.net/spotify/country/vn_weekly.html")
        soup = BeautifulSoup(rawContent, 'html.parser')
        songs = soup.find_all("td", {"class":"text mp"})
        self.spotifyIds = []
        self.songsName = []
        for song in songs:
            songNameRaw = BeautifulSoup(str(song), 'html.parser').find_all("a")
            songName = str(songNameRaw[0].contents[0]) + " - " + str(songNameRaw[1].contents[0])
            spotifyId = songNameRaw[1].get("href")[len("../track/"):-len(".html")]
            self.spotifyIds.append(spotifyId)
            self.songsName.append(songName)


    def crawTrackAnalysisDataAndPredict(self):
        
        if os.path.isfile("songsCluster.csv"):
            self.clusterPrediction = np.loadtxt("songsCluster.csv",
                    delimiter=",", dtype=str)
        else:
            import time
            self.trackAnalysis = []
            self.clusterPrediction = []
            for i, spotifyId in enumerate (self.spotifyIds):
                cmd = '''curl --request GET \\
                        --url https://api.spotify.com/v1/audio-features/''' + spotifyId+  ''' \\
                        --header 'Authorization: Bearer ''' + self.accessToken +''''
                        '''
                output = subprocess.check_output(cmd, shell=True)    
                data = json.loads(output.decode("utf-8"))
                print(data)
                self.trackAnalysis.append(data)
                time.sleep(0.5)
                try :
                    prediction = self.loaded_cluster_model.predict([[data['acousticness'] ,	data['danceability'], 	data['liveness'], 	data['energy'] ,	data['instrumentalness'], 	data['loudness'], 	data['speechiness']]])
                    self.clusterPrediction.append([prediction[0], self.songsName[i]])
                except:
                    pass
            np.savetxt("songsCluster.csv",
            self.clusterPrediction,
            delimiter =", ",
            fmt ='% s')

    def getCluster(self):         
        return self.clusterPrediction
if __name__ == "__main__":
    recommendationSystem = RecommendationSystem()
        
    recommendationSystem.crawTrendingSongs()
    recommendationSystem.crawTrackAnalysisDataAndPredict()
    cluster = recommendationSystem.getCluster()
    for i, songs in enumerate(cluster):
        print(songs[0][0])