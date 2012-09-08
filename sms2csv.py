#!/usr/bin/python2.7

# requires a patched version of pygooglevoice.
# (from http://productforums.google.com/forum/#!topic/voice/OS-abSdgz-k)

from googlevoice import Voice 
import re 
import sys 
import csv 
import datetime 
import StringIO 
import BeautifulSoup 
import pickle 
import json


def nextConversation(json, html) : 
    tree = BeautifulSoup.BeautifulSoup(html) 
    convBlock = tree.findAll('div', attrs={'id' : True}, recursive=False) 
    jsonMessages = json['messages'] 
    for conv in convBlock : 
        convId = conv['id'] 
        convmap = jsonMessages[convId] 
        rows = conv.findAll(attrs={'class' : 'gc-message-sms-row'}) 
        messages = [] 
        for row in rows: 
            spans = row.findAll('span', attrs={'class' : True}, recursive=False) 
            msgitem = {} 
            for span in spans: 
                cl = span['class'].replace('gc-message-sms-', '') 
                msgitem[cl] = (' '.join(span.findAll(text=True))).strip() 
            messages.append(msgitem) 
        convmap['messages'] = messages 
        yield convmap 
    return 

RTStamp = datetime.datetime.now() 
print 'started at ' + str(RTStamp) 

#try opening the log, if it fails, create the log but don't read from it 
#additionally, create a timestamp from 1985, thus ensuring all messages are downloaded 
#if it succeeds in opening, read the timestamp from the file 
try: 
        TSfile = open('RunTimeStamp.txt','r') 
except IOError: 
        TSfile = open('RunTimeStamp.txt','a') 
        lastRTStamp = datetime.datetime(1985, 1, 1) 
else:         
        lastRTStamp = pickle.load(TSfile)         
        print 'file contained ' + str(lastRTStamp) + ' as the last time this was run' 
TSfile.close() 


credentials = json.load(file('gmail-credentials.js'))
assert credentials['email']
assert credentials['password']
         
voice = Voice() 
voice.login(credentials['email'], credentials['password']) # leave out the arguments to make it ask each time so you don't have your password floating around in plain text. 

header = ('id', 'phone', 'date', 'time', 'from', 'text') 
conversations = [] 
page = 0 
dtdate = datetime.date 
cont = True 
while cont: 
    page += 1 
    voice.sms(page) 
    count = 0 
    for conv in nextConversation(voice.sms.data, voice.sms.html): 
        count += 1 
        startTime   = conv['startTime'].encode("utf-8") #not really "start" time it's actually "last message received at" time, but start is shorter 
        phoneNumber = conv['phoneNumber'].encode("utf-8") 
        floatTime   = float(startTime) / 1000.0 
        date                = dtdate.fromtimestamp(floatTime).strftime('%Y-%m-%d').encode('utf-8') 
        compareTime        = datetime.datetime.fromtimestamp(floatTime) 
        item = 0 
                #if starttime is less than lastRTStamp then break cause these messages were got last time this was run 
        if compareTime < lastRTStamp: 
                        cont = False 
                        break 
        messages = conv['messages'] 
        for message in messages: 
            messageFrom = message['from'].encode("utf-8") 
            messageTime = message['time'].encode("utf-8") 
            messageText = message['text'].encode("utf-8") 
            id = ('%s-%04d' % (startTime, item)).encode("utf-8") 
            conversations.append((id, phoneNumber, date, messageTime, messageFrom, messageText)); 
                                  
            item += 1 
    if count < 1: 
        cont = False 
    sys.stderr.write("retrieved page %d\n" % page) 

#make sure the annoyingly long fileName string is on a single line 
first = True 
nameStamp = RTStamp.replace(microsecond=0) 
fileName = 'GVsms ' + str(nameStamp.date()) + ' ' + str(nameStamp.hour) + '-' + str(nameStamp.minute) + '-' + str(nameStamp.second) + '.csv' 
output = open(fileName,'wb') 
csvWriter = csv.writer(output, quoting=csv.QUOTE_MINIMAL) 
for conv in sorted(conversations, key=lambda element: element[0]): 
    if first: 
        first = False 
        csvWriter.writerow(header) 
    csvWriter.writerow(conv) 

output.close() 

#add runtime timestamp to log file 
TSfile = open('RunTimeStamp.txt','wb') 
pickle.dump(RTStamp, TSfile) 
TSfile.close()
