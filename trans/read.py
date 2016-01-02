# -*- coding:utf-8 -*
import random
import os
f = open('newWord.txt')
content = f.readlines()
f.close()
words = [c.rstrip().split(':', 1) for c in content]

os.system('clear')
while True:
    input = raw_input('输入e查看所有英文单词，' + 
            '输入c查看所有中文释义，输入a同时查' +
            '看单词和释义，输入q退出程序\n')
    if input == 'e':
        for word in words:
            print word[0]
    elif input == 'c':
        for word in words:
            print word[1]
    elif input == 'a':
        for word in words:
            print '%-30s%s'%(word[0], word[1])
    elif input == 'q':
        break
    else:
        print 'input error'
    raw_input()
