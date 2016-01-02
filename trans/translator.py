#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import urllib
import urllib2
import json
import codecs
import re
from Tkinter import *
import socket
import os
import threading
import sys
import requests
import keylogger

URL = "http://translate.google.cn/translate_a/single?client=t&sl=en&tl=zh-CN&hl=zh-CN&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&dt=at&ie=UTF-8&oe=UTF-8&otf=1&ssel=0&tsel=0&kc=5&tk=522736|742654&q="

FILENAME = ".translator.opened"

def cur_file_dir():
    path = sys.path[0]
    
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.path = cur_file_dir()
        self.pack()
        self.closed = False
        self.master = master

        self.master.protocol("WM_DELETE_WINDOW", self.quit)

        self.createWidgets()
        self.master.title('translator')

        t = threading.Thread(target=self.key_detect, name="keyloggerThread")
        t.start()

        # t = threading.Thread(target=self.startServer, name='serverThread')
        # t.start()
        # self.after(5, self.startServer)

    def done(self):
        return self.closed

    def key_detect(self):
        def dealKeyCallBack(t, modifiers, keys):
            if((modifiers['left shift'] or modifiers['right shift'])
                    and keys == "<esc>"):
                self.startTrans()
        keylogger.log(self.done, dealKeyCallBack)


    def createWidgets(self):
        self.transLabel = Label(self, text='translator label', width = 50,
                wraplength = 300, justify = 'left')
        self.transLabel.pack()

        self.entrythingy = Entry(self)
        self.entrythingy.pack()

        self.content = StringVar()
        self.content.set("input words in here")
        self.entrythingy.config(textvariable=self.content)
        self.entrythingy.bind('<Key-Return>', self.translateFromEntry)

        self.quitButton = Button(self, text='Quit', command=self.quit)
        self.quitButton.pack()

    def translateFromEntry(self, event):
        text = self.content.get()
        if(not text):
            self.changeLabel('输入框中无内容')
            return
        self.changeLabel('翻译中...')
        trans = self.translate(text)
        if trans:
            self.changeLabel(trans + '\n' + text)

    def changeLabel(self, text):
        self.transLabel['text'] = text
    
    def quit(self):
        global FILENAME
        if os.path.exists(FILENAME):
            os.remove(FILENAME)
        self.closed = True
        self.tk.quit()

    def startTrans(self):
        text = self.getTextFromXclip()
        self.master.wm_attributes('-topmost', 1)
        self.master.wm_attributes('-topmost', 0)
        if(not text):
            self.changeLabel('剪贴板内无内容')
            return
        self.changeLabel('翻译中...')
        trans = self.translate(text)
        if trans:
            self.changeLabel(trans + '\n' + text)

    # def startServer(self):
    #     try:
    #         self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         self.s.bind(('127.0.0.1', 2333))
    #     except socket.error, e:
    #         self.changeLabel('无法开启服务: ' + 
    #                 str(e) + '\n' +
    #                 '点击左上角叉号关闭')
    #         self.s.close()
    #         return
    #     self.s.listen(1)
    #     while(True):
    #         sock, addr = self.s.accept()
    #         data = sock.recv(20)
    #         sock.close()
    #         if data == 'trans':
    #             text = self.getTextFromXclip()
    #             if(not text):
    #                 self.changeLabel('剪贴板内无内容')
    #                 continue
    #             self.changeLabel('翻译中...')
    #             trans = self.translate(text)
    #             if trans:
    #                 self.changeLabel(trans + '\n' + text)
    #         elif data == 'exit':
    #             self.s.close()
    #             break

    def getTextFromXclip(self):
        cmd = "xclip -o"
        text = os.popen(cmd)
        return text.read()

    def translate(self, orginalText):
        transUrl = URL + orginalText.replace(' ', '%20')

        headers = {
            #'Host': 'translate.google.cn',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'http://translate.google.cn/',
            #'Cookie': '_ga=GA1.3.1555123562.1434506244',
            'Connection': 'keep-alive'
        }

        try:
            req = requests.get(transUrl, headers=headers, timeout = 5)
        except requests.exceptions.Timeout, e:
            self.changeLabel('连接超时，请稍后重试' + str(e))
            return False
        resultJson = req.text
        resultJson = re.sub(r'(?<=,)\s*,', ' null,', resultJson)
        resultJson = resultJson.replace('[,', '[null ,')
        resultObj = json.loads(resultJson, encoding="utf8")
        trans = resultObj[0]
        text = [];
        if(not trans):
            self.changeLabel("无翻译结果")
            return False
        for tran in trans:
            if tran[0]:
                text.append(tran[0])
        text = ''.join(text)

        #save new word in text
        f = open(self.path + '/newWord.txt', 'a')
        f.write(orginalText + ': ' + 
                text.encode('utf8') + '\n')
        f.close()

        return text
    
if __name__ == '__main__':
    if not os.path.exists(FILENAME):
        f = open(FILENAME, 'w')
        f.write("opened")
        f.close()
        root = Tk()
        app = Application(root)
        app.mainloop()
