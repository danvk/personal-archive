#!/usr/bin/python
#
# Note: I had to follow these instructions to enable chat logs/IMAP:
# http://dataliberation.blogspot.com/2011/09/gmail-liberates-recorded-chat-logs-via.html

import json
import imaplib
import email
import datetime

credentials = json.load(file('gmail-credentials.js'))
assert credentials['email']
assert credentials['password']

# Fetch new messages from gmail.
imap = imaplib.IMAP4_SSL('imap.gmail.com', 993)
imap.login(credentials['email'], credentials['password'])

# True=readonly. Returns ('OK', ['3632'])
status, data = imap.select("[Gmail]/Chats", True)

status, messages = imap.search(None, 'ALL')
assert status == 'OK'

# messages is an array of message numbers (as strings)
messages = messages[0].split()
assert messages[0] == '1'
assert messages[-1] == str(len(messages))

print 'Fetching headers 1:' + messages[-1]
start = datetime.datetime.now()
typ, msg_data = imap.fetch('1:' + messages[-1], '(BODY.PEEK[HEADER])')
end = datetime.datetime.now()
assert typ == 'OK'
print 'Fetched %d messages in %s' % (len(messages), end - start)

assert len(msg_data) == 2 * len(messages)
json.dump(msg_data, file('staging/gmail-chats.json', 'w'), indent=2)

