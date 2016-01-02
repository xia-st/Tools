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

        self.videoUrlRE = re.compile(r'https://www.tumblr.com/video_file/[^"]+')
        self.linkUrlRE = re.compile(r"https://www.tumblr.com/video/{0}/\d+/\d+/".format(tumblrName))

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
            cursor.execute("create table video(feature varchar(20), time datetime, url varchar(100))")
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

    def checkUrl(self, feature):
        cursor = self.conn.cursor()
        cursor.execute("select feature, time from video where feature = ?", (feature,))
        results = cursor.fetchall()
        cursor.close()
        if not results:
            return None
        return results[0]

    def saveToDB(self, feature, url):
        cursor = self.conn.cursor()
        cursor.execute("insert into video(feature, time, url) \
                values(?, datetime('now'), ?)", (feature, url))
        cursor.close()
        self.conn.commit()

    def setUrl(self, feature, url):
        cursor = self.conn.cursor()
        cursor.execute("select url from video where feature = ?", (feature,))
        results = cursor.fetchall()
        if not results[0][0]:
            cursor.execute("update video set url = ? where feature = ?", (url, feature))
            print "set this url to database"
        cursor.close()
        self.conn.commit()

    def saveVideo(self, url, fileName=None):
# get the feature of url
        urlSplit = url.split('/')
        if(len(urlSplit) < 2):
            print " format error:", url
            return False
        for u in urlSplit[::-1]:
            if not u.isdigit():
                feature = u
                break

        if not fileName:
            fileName = self.tumblrName + '/' + feature + '.mp4'

        result = self.checkUrl(feature)
        if result:
            print url
            print fileName, "was downloaded in", result[1]
            self.setUrl(feature, url)
            return True

        video = self.getContent(url)
        if video:
            f = open(fileName, "wb")
            f.write(video)
            f.close()

            self.saveToDB(feature, url)

            print fileName + " save succeed."
            return True
        else:
           print fileName, "save failed."
           return False

    def getVideoUrl(self, url):
        # content = open('2.html', 'r').read()
        content = self.getContent(url)
        result = self.videoUrlRE.findall(content)
        return result

    def getLinkUrl(self, page):
        url = "http://{0}.tumblr.com/page/{1}" .format(self.tumblrName, page)
        content = self.getContent(url)
        # content = open("1.htm", "r").read()

        result = self.linkUrlRE.findall(content)
        return result

    def startDownload(self, startPage=1, endPage=1):
        folder = self.tumblrName + "/"

        if not os.path.exists(folder):
            os.mkdir(folder)
        for page in range(startPage, endPage + 1):
            linkUrls =  self.getLinkUrl(page)
            for linkUrl in linkUrls:
                url = self.getVideoUrl(linkUrl)
                if len(url) == 0:
                    continue
                url = url[0]
                self.saveVideo(url)
        self.closeDatabase()
if __name__ == '__main__':
    # logger = logging.getLogger("simpleExample")
    tumblrVideo = TumblrVideo('hsexh233')
    tumblrVideo.startDownload(1, 15)
