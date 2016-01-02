# -*- coding:utf-8 -*
import random
import os
f = open('newWord0.txt')
content = f.readlines()
f.close()
words = [c.rstrip().split(':', 1) for c in content]

backup = words[:]

os.system('clear')
print '开始背诵单词'
while len(words) > 0:
    r = random.randint(0, len(words) - 1)
    print words[r][1].strip()
    input = raw_input()
    if input != words[r][0].strip():
        print '拼写错误，答案为：' + words[r][0].strip()
    else:
        print '拼写正确'
        del words[r]
    raw_input()
    os.system('clear')
print '第一次背诵完毕'
print '第二次背诵'
words = backup
while len(words) > 0:
    r = random.randint(0, len(words) - 1)
    print words[r][1]
    input = raw_input()
    if input != words[r][0].strip():
        print '拼写错误，答案为：' + words[r][0].strip()
    else:
        print '拼写正确'
        del words[r]
    raw_input()
    os.system('clear')
print '结束背诵'
