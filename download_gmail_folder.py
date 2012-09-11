#!/usr/bin/python
"""Downloads all messages & headers from a Gmail folder into a JSON file.

Usage: ./download_gmail_folder.py (folder) (output.json)

When run with no arguments, this will list your gmail folders.

The JSON file contains raw IMAP results. You'll want to use email.parser to
read them. See import_notes.py.
"""

import chardet
import json
import imaplib
import email
import datetime
import sys
import os

credentials = json.load(file('gmail-credentials.js'))
assert credentials['email']
assert credentials['password']

# Fetch new messages from gmail.
imap = imaplib.IMAP4_SSL('imap.gmail.com', 993)
imap.login(credentials['email'], credentials['password'])

if len(sys.argv) == 1:
  status, data = imap.list()
  assert status == 'OK'
  print '\n'.join(sorted(data))
  sys.exit(0)

assert len(sys.argv) == 3, (
  'Usage: %s (folder) (output.json)' % sys.argv[0])

folder, out_json = sys.argv[1:]

# True=readonly. Returns ('OK', ['3632'])
status, data = imap.select(folder, True)

status, messages = imap.search(None, 'ALL')
assert status == 'OK'

# messages is an array of message numbers (as strings)
messages = messages[0].split()
assert messages[0] == '1'
assert messages[-1] == str(len(messages))

def GetIdFromMessage(msg):
  info = msg[0][0]
  return info[0:info.find(' ')]


start = datetime.datetime.now()
preloaded_idxs = set()
if os.path.exists(out_json):
  msgs = json.load(file(out_json))
  for msg in msgs:
    preloaded_idxs.add(GetIdFromMessage(msg))
else:
  msgs = []

for idx in messages:
  if idx in preloaded_idxs:
    print '(cached) %s/%d' % (idx, len(messages))
    continue

  print 'Fetching %s/%d' % (idx, len(messages))
  typ, msg_data = imap.fetch(idx, '(BODY[HEADER] BODY[TEXT])')
  if typ != 'OK':
    sys.stderr.write('Failed to fetch %s\n' % idx)
    continue

  body = msg_data[0][1]
  msg_data[0] = [msg_data[0][0], body.decode(chardet.detect(body)['encoding'])]

  msgs.append(msg_data)
  if len(msgs) % 50 == 0:
    print '(writing to disk)'
    json.dump(msgs, file(out_json, 'w'), indent=2, encoding="utf-8")

json.dump(msgs, file(out_json, 'w'), indent=2, encoding="utf-8")

end = datetime.datetime.now()
print 'Fetched %d messages in %s' % (len(messages), end - start)
