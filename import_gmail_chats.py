#!/usr/bin/python2.7

import email
import json
import sys
from dateutil import parser

def ReadChatData(json_file):
  """Returns a list of (buddy, datetime) pairs."""
  msg_data = json.load(file(json_file))

  chats = []
  for idx, msg in enumerate(msg_data):
    if msg == ')': continue

    assert len(msg) == 2
    assert ' (BODY[HEADER]' in msg[0]
    headers = msg[1]

    m = email.message_from_string(headers.encode('utf8'))
    dt = parser.parse(m['Date'])

    if not m['From']:
      sys.stderr.write('Chat w/o From line: %d' % idx)
      continue

    # TODO(danvk): get link via the Message-ID parameter?
    buddy = m['From']

    chats.append((dt, buddy))

  return chats


if __name__ == '__main__':
  assert 2 == len(sys.argv)
  data = ReadChatData(sys.argv[1])
