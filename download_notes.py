#!/usr/bin/python

import json
import imaplib
import email
import datetime
import sys

credentials = json.load(file('gmail-credentials.js'))
assert credentials['email']
assert credentials['password']

# Fetch new messages from gmail.
imap = imaplib.IMAP4_SSL('imap.gmail.com', 993)
imap.login(credentials['email'], credentials['password'])

# True=readonly. Returns ('OK', ['3632'])
status, data = imap.select("Notes", True)

status, messages = imap.search(None, 'ALL')
assert status == 'OK'

# messages is an array of message numbers (as strings)
messages = messages[0].split()
assert messages[0] == '1'
assert messages[-1] == str(len(messages))

start = datetime.datetime.now()
msgs = []
for idx in messages:
  print 'Fetching %s/%d' % (idx, len(messages))
  typ, msg_data = imap.fetch(idx, '(BODY[HEADER] BODY[TEXT])')
  if typ != 'OK':
    sys.stderr.write('Failed to fetch %s\n' % idx)
    continue

  msgs.append(msg_data)
  json.dump(msgs, file('staging/gmail-notes.json', 'w'), indent=2)

end = datetime.datetime.now()
print 'Fetched %d messages in %s' % (len(messages), end - start)
