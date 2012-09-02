#!/usr/bin/python
"""Find IM logs in the damaged backup disk from July 2006.

There are ~650 of these and they span from late March 2006 to mid-July.
"""

import mmap
import re
from dateutil import parser
import json

disk_file = '/Users/danvk/transfer/backup-2006-07-15.img'

im_start = 'Conversation with '

f = open(disk_file, 'rb')
s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

out = []

num = 0
for m in re.finditer('Conversation with [^\0]+\0', s):
  log = m.group(0)
  m = re.match('Conversation with ([^ ]*) at (.*?) on', log)
  if not m:
    # False positive, e.g. email starting with 'Conversation with...'
    continue

  user, date = m.groups()
  date = parser.parse(date)
  num += 1
  log = log[0:-1]  # strip trailing nul

  out.append({
    'buddy': user,
    'date': date.strftime('%Y-%m-%d %H:%M:%s'),
    'contents': '\n'.join(log.split('\r\n')[1:])
  })

print json.dumps(out, indent=2)
