import keylogger

def key_detect(t, modifiers, keys):
    print modifiers, keys
    if((modifiers['left shift'] or modifiers['right shift'])
            and keys == "<esc>"):
        print 'ok'

done = lambda : False
keylogger.log(done, key_detect)
