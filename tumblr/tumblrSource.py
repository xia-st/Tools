import requesocks as requests
import re
import logging
import logging.config
import os
import sqlite3

class TumblrVideo:
    databaseName = "db/url.db"
    def __init__(self, tumblrName, isProxies=False):
        self.tumblrName = tumblrName
        self.isProxies = isProxies

        self.headers = { #'Host': 'translate.google.cn',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'http://translate.google.cn/',
            #'Cookie': '_ga=GA1.3.1555123562.1434506244',
            'Connection': 'keep-alive'
        }
        self.proxies = {
                'http': 'socks5://127.0.0.1:7070',
                'https': 'socks5://127.0.0.1:7070'
        }

        self.getVideoUrl = re.compile(r"https://www.tumblr.com/video/{0}/\d+/\d+/".format(tumblrName)).findall
        self.getTrueVideoUrl = re.compile(r'https://www.tumblr.com/video_file/[^"]+').findall
        self.getImageUrl = re.compile(r'src="(http://{0}.tumblr.com/post/[^"]+)'.format(tumblrName)).findall
        self.getTrueImageUrl = re.compile(r'href="(http://\d+.media.tumblr.com/[^"]+)').findall

        self.conn = self.connectDatabase()

    def connectDatabase(self):
        if os.path.exists(TumblrVideo.databaseName):
            return sqlite3.connect(TumblrVideo.databaseName)
        else:
            index = TumblrVideo.databaseName.rfind('/')
            folder, trueName = TumblrVideo.databaseName.rsplit('/', 1)
            print folder, trueName
            if not os.path.exists(folder):
                os.makedirs(folder)
            conn = sqlite3.connect(TumblrVideo.databaseName)
            cursor = conn.cursor()
            cursor.execute("create table video(feature varchar(20) primary key, time datetime, url varchar(100))")
            cursor.execute("create table image(feature varchar(20) primary key, time datetime, url varchar(100))")
            cursor.close()
            conn.commit()
            return conn

    def closeDatabase(self):
        if self.conn:
            self.conn.close()

    def getContent(self, url, timeout=180):
        print url
        s = requests.Session()
        try:
            if self.isProxies:
                html = s.get(url, headers=self.headers, proxies=self.proxies, timeout=timeout)
            else:
                html = s.get(url, headers=self.headers, timeout=timeout)
        except Exception, e:
            print "Exception:", e
            return ""
        return html.content

    def checkUrl(self, feature, urlType = "video"):
        cursor = self.conn.cursor()
        if urlType == "video":
            cursor.execute("select feature, time from video where feature = ?", (feature,))
        elif urlType == "image":
            cursor.execute("select feature, time from image where feature = ?", (feature,))
        results = cursor.fetchall()
        cursor.close()
        if not results:
            return None
        return results[0]

    def saveToDB(self, feature, url, fileType = "video"):
        cursor = self.conn.cursor()
        if fileType == "video":
            cursor.execute("insert into video (feature, time, url) \
                values(?, datetime('now'), ?)", (feature, url))
        elif fileType == "image":
            cursor.execute("insert into image (feature, time, url) \
                values(?, datetime('now'), ?)", (feature, url))
        cursor.close()
        self.conn.commit()

    def saveVideo(self, url, fileName=None):
        urlSplit = url.split('/')
        if(len(urlSplit) < 2):
            print " format error:", url
            return False
        for u in urlSplit[::-1]:
            if not u.isdigit():
                feature = u
                break

        if not fileName:
            fileName = self.tumblrName + '/video/' + feature + '.mp4'

        result = self.checkUrl(feature)
        if result:
            print fileName, " was downloaded in ", result[1]
            return True

        video = self.getContent(url)
        if video:
            f = open(fileName, "wb")
            f.write(video)
            f.close()

            self.saveToDB(feature, url)

            print fileName, "save succeed."
            return True
        else:
           print fileName, "download failed."
           return False

    def saveImage(self, imageUrl):
        fileName = imageUrl.rsplit("/", 1)[1]
        feature = fileName.split('.')[0]
        fileName = self.tumblrName + "/image/" + fileName

        result = self.checkUrl(feature, urlType = "image")
        if result:
            print fileName, "was downloaded in ",result[1]
            return True
        image = self.getContent(imageUrl)
        if image:
            f = open(fileName, "wb")
            f.write(image)
            f.close()
            
            self.saveToDB(feature, imageUrl, fileType = "image")

            print fileName, "save succeed"
            return True
        else:
            print fileName, "download failed"
            return False

    def startDownload(self, startPage=1, endPage=1):
        folder = self.tumblrName + "/"

        if not os.path.exists(folder):
            os.mkdir(folder)
        if not os.path.exists(folder + "/video"):
            os.mkdir(folder + "/video")
        if not os.path.exists(folder + "/image"):
            os.mkdir(folder + "/image")
        for page in range(startPage, endPage + 1):
            url = "http://{0}.tumblr.com/page/{1}" .format(self.tumblrName, page)
            content = self.getContent(url)

            videoUrls =  self.getVideoUrl(content)
            imgUrls = self.getImageUrl(content)

            for videoUrl in videoUrls:
                content = self.getContent(videoUrl)
                trueVideoUrl = self.getTrueVideoUrl(content)
                if not trueVideoUrl:
                    print("Can't find true video url")
                    continue
                trueVideoUrl = trueVideoUrl[0]
                self.saveVideo(trueVideoUrl)

            for imgUrl in imgUrls:
                content = self.getContent(imgUrl)
                trueImageUrls = self.getTrueImageUrl(content)
                if not trueImageUrls:
                    print("Can't find true image url")
                    continue
                for trueImageUrl in trueImageUrls:
                    self.saveImage(trueImageUrl)
        self.closeDatabase()
if __name__ == '__main__':
    # logger = logging.getLogger("simpleExample")
    tumblrVideo = TumblrVideo('xincyqing')
    tumblrVideo.startDownload(1, 2)
