import requests
from bs4 import BeautifulSoup

def get_content(url):
    
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
        'User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
    try:
        
        r = requests.get(url, headers=headers, timeout=10)
        r.encoding  = 'utf-8' 
        r.close()
        return r.text#.encode('utf-8', 'inorge')
    except:
        # print('Exception'+ str(e))
        return None

class NewsProvider:
    def __init__(self) -> None:
        self.title = []
        self.description = []
    def fetchingArticles(self):
        # Below is an sample element of articleList 
        #         <article class="article-item" data-content-name="category-highlights"
        #     data-content-piece="category-highlights-position_1"
        #     data-content-target="/the-thao/bao-indonesia-binh-luan-khi-doi-nha-di-tiep-tuyen-viet-nam-bi-loai-20240612123442356.htm"
        #     data-track-content="">
        #     <div class="article-thumb"><a
        #             href="/the-thao/bao-indonesia-binh-luan-khi-doi-nha-di-tiep-tuyen-viet-nam-bi-loai-20240612123442356.htm"><img
        #                 alt="Báo Indonesia bình luận khi đội nhà đi tiếp, tuyển Việt Nam bị loại" height="344"
        #                 src="https://cdnphoto.dantri.com.vn/-7JgbkGwAwjVzbt-wXCaxkrbaw4=/zoom/774_516/2024/06/12/vniraq2-crop-edited-crop-1718172230611.jpeg"
        #                 srcset="https://cdnphoto.dantri.com.vn/7YjbdE0Z8K0xDbP7HKAjmURTqwk=/zoom/1032_688/2024/06/12/vniraq2-crop-edited-crop-1718172230611.jpeg 2x, https://cdnphoto.dantri.com.vn/-7JgbkGwAwjVzbt-wXCaxkrbaw4=/zoom/774_516/2024/06/12/vniraq2-crop-edited-crop-1718172230611.jpeg 1x"
        #                 width="516" /></a></div>
        #     <div class="article-content">
        #         <h3 class="article-title"><a class="dt-text-black-mine"
        #                 href="/the-thao/bao-indonesia-binh-luan-khi-doi-nha-di-tiep-tuyen-viet-nam-bi-loai-20240612123442356.htm">Báo
        #                 Indonesia bình luận khi đội nhà đi tiếp, tuyển Việt Nam bị loại</a></h3>
        #         <div class="article-excerpt"><a
        #                 href="/the-thao/bao-indonesia-binh-luan-khi-doi-nha-di-tiep-tuyen-viet-nam-bi-loai-20240612123442356.htm">Nhiều
        #                 tờ báo của Indonesia hân hoan khi đoàn quân HLV Shin Tae Yong là đội bóng duy nhất Đông Nam Á góp mặt ở
        #                 vòng loại thứ ba World Cup 2026, còn hai đội tuyển Việt Nam và Thái Lan đều bị loại.</a></div>
        #     </div>
        # </article>
        rawContent = get_content("https://dantri.com.vn/tin-moi-nhat.htm")
        soup = BeautifulSoup(rawContent, 'html.parser')
        articleList = soup.find_all("article", {"class":"article-item"})
        for article in articleList:
            _title = BeautifulSoup(str(article), 'html.parser').find_all("h3", {"class":"article-title"})
            _description = BeautifulSoup(str(article), 'html.parser').find_all("div", {"class":"article-excerpt"})
            self.title.append(_title[0].get_text() if _title != [] else "" )
            self.description.append(_description[0].get_text() if _description != [] else "" )
    def clearArticleList(self):
        self.title = []
        self.description = []
    def toTitleDescriptionListDict(self):
        result = []
        for title, description in zip(self.title, self.description):
            result.append({"title": title, "description": description})
        return result
if __name__ == "__main__":
    newsProvider = NewsProvider()
    newsProvider.fetchingArticles()
    # print(list(dict(zip(newsProvider.title, newsProvider.description))))
    print(newsProvider.toTitleDescriptionListDict())