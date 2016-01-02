# -*- coding: utf-8 -*-
import urllib
import urllib2
import re
import sys
import os

class stuGrdSpider:
    xscjcx = 'http://210.33.28.180/stu/xscjcx.asp' # get grade in here
    xskbcx = 'http://210.33.28.180/public/xskbcx.asp' # get student' name in here
    def __init__(self):
        self.sno = ''
        self.name = ''
        self.file = None
        self.zp = 'http://210.33.28.180/zhaopian/'

    def writeGrade(self, grade):
        for row in grade:
            for cell in row:
                self.file.write(cell + ', ')
            self.file.write('\r\n')

    def getImg(self):
        url = self.zp + self.sno[0:4] + '/' + self.sno + '.jpg'
        if not os.path.exists('img'):
            os.mkdir('img')
        f = open('img/' + self.sno + '.jpg', 'wb')
        try:
            img = urllib2.urlopen(url).read()
        except urllib2.URLError, e:
            print e.code()
            print url
        f.write(img)
        f.close()

    def getGrade(self):
        gd = re.compile(r'<TR.*?><TD.*?>(.*?)</TD><TD.*?>(.*?)</TD><TD.*?>(.*?)</TD><TD.*?>.*?</TD><TD.*?>(.*?)</TD><TD.*?>.*?</TD><TD.*?>.*?</TD><TD.*?>(.*?)</TD><TD.*?>(.*?)</TD><TD.*?>(.*?)</TD>').findall
        getData = {'xh': self.sno, 'xm': self.name, 'gnmkdm': 'N121605'}
        postData = {'vxn': '', 'vxq': '', 'vcxfw': '历年成绩'.encode('gb2312'), 'bxqcj': '历年成绩'.encode('gb2312')}
        
        ad = stuGrdSpider.xscjcx + '?' + urllib.urlencode(getData)
        post = urllib2.Request(ad, urllib.urlencode(postData))
        post.add_header('Content-Type', 'application/x-www-form-urlencoded')
        try:
            req = urllib2.urlopen(post).read()
        except urllib2.URLError, e:
            print e.code()
            print 'Link Address Error'
            sys.exit(0)
        grade = gd(req)
        self.writeGrade(grade)
    def getName(self):
        nameMatch = re.compile(ur'姓名：(.*?)</td>'.encode('gb2312'), re.S).search
        postData = {'vxn': '2014-2015', 'vxq': '2', 'vxh': self.sno}
        post = urllib2.Request(stuGrdSpider.xskbcx, urllib.urlencode(postData))
        post.add_header('Content-Type', 'application/x-www-form-urlencoded')
        try:
            req = urllib2.urlopen(post).read()
        except urllib2.URLError, e:
            print e.code()
            print 'Link Address Error'
            sys.exit(0)
        name = nameMatch(req)
        if(name is None):
            # print 'find name error'
            return
        self.name = name.group(1)
        return True
    def start(self, sno, filename):
        if filename:
            self.file = open(filename, 'a')
        self.sno = sno
        if not self.getName():
            # print 'Get Message Error'
            return
            
        self.file.write('名字：'.encode('gb2312') + self.name + '\r\n')
        self.file.write('学号：'.encode('gb2312') + self.sno + '\r\n')
        self.file.write('序号'.encode('gb2312')) # This massage is not given in web page

        self.getGrade()
        self.getImg()
        self.file.close()
    
def startSpider():
    reload(sys)  
    sys.setdefaultencoding('utf8')
    sp = stuGrdSpider()
    sno, esno = 0, 0
    try:
        ssno = int(sys.argv[1])
        esno = int(sys.argv[2])
    except ValueError, e:
        print 'Sno\'s format Error'
        return false
    if ssno > esno :
        print 'The start sno is larger than end sno'
        return False
    if esno - ssno > 100:
        print 'The range of start sno and end sno is too large, which should smaller than 100'
        print 'Please check the start sno and end sno which you input'
        print 'start sno: \t' + str(ssno)
        print 'end sno: \t' + str(esno)
        return
        
    for sno in range(ssno, esno + 1):
        sp.start(str(sno), sys.argv[3])
        sys.stdout.write('-')
        sys.stdout.flush()
    print 'fin'
if len(sys.argv) < 4:
    print 'Usage: python ' + sys.argv[0] + ' startSno endSno filename'
else:
    startSpider()


