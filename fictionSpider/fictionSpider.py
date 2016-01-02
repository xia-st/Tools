# -*- coding: utf-8 -*-  

import urllib2
import urllib
import re
import sys

class Title:
    def __init__(self, title = ''):
        self.title = title
        self.secondBlock = []
    
    def getsecondBlock(self, s, e, htmlText, st):    #参数分别为 每卷的开始位置、结束位置。文本，使用的正则表达式
        self.secondBlock = st(htmlText[s:e])
        
    def showTitle(self):
        print self.title
        for i, j in self.secondBlock:
            print i, j

class Spider:
    ft = re.compile(r'''<div class='title'><b>.*?</a>&nbsp;(.*?)&nbsp;</b>''', re.S).search
    st = re.compile(r'''<a itemprop='url' href="(.*?)".*?><span itemprop='headline'>(.*?)</span>''', re.S).findall
    
    def __init__(self):
        self.spider = []
    
    def getTitle(self, URL = ''):
        #获取每次寻找到的大标题（第一标题）的位置
        searchEnd = 0
        span = []
        
        htmlText = urllib2.urlopen(URL).read()
        htmlText = htmlText.decode("utf-8")
        while True:
            m = Spider.ft(htmlText[searchEnd:])
            if m is None: break
            self.spider.append(Title(m.group(1)))
            span.append(map(lambda x: x + searchEnd, m.span()))
            searchEnd = span[-1][1]

        #字段与字段之间的位置，即小标题（第二标题）的位置
        for i in range(len(span) - 1):
            span[i][0], span[i][1] = span[i][1], span[i + 1][0]
        span[-1][0], span[-1][1] = span[-1][1], len(htmlText)

        for i in range(len(self.spider)):
            self.spider[i].getsecondBlock(span[i][0], span[i][1], htmlText, Spider.st)
            
    def showTitle(self):
        for s in self.spider:
            s.showTitle()
            
    def getRealText(self, URL = ''):
        htmlText = urllib2.urlopen(URL).read()
        htmlText = htmlText.decode("utf-8")
        exp2RealText = re.compile(r'''<div class="bookcontent".*?>.*?<script src='(.*?)'.*?></script>''', re.S).search
        m = exp2RealText(htmlText)
        realText = urllib2.urlopen(m.group(1)).read()
        realText = realText.decode('gbk')
        realText = realText[16:-123].replace('<p>', '\r\n')
        return realText
        
    def getText(self):
        for spider in self.spider:
            print spider.title
            file = open(spider.title.replace('?', '') + '.txt', 'w')
            file.write(spider.title + '\r\n')
            for secondURL, secondTitle in spider.secondBlock:
                print secondTitle
                file.write(secondTitle + '\r\n')
                file.write(self.getRealText(secondURL) + '\r\n')
            file.close()
    
    def start(self, URL):
        self.getTitle(URL)
        self.getText()

reload(sys)  
sys.setdefaultencoding('utf8') 

spider = Spider()
spider.start('http://read.qidian.com/BookReader/2413595.aspx')
