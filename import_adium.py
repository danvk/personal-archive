#!/usr/bin/python2.7
"""Import Adium chat logs (i.e. ".adiumLog").

Format:
A 2003-02-24 -0600
(20:41:18)iambatman456:how are you?
(20:43:41)dantheox:hey...
"""

from collections import defaultdict
from dateutil import parser
import chardet
import glob
import utils
import os
import re

dirs = [
  "/Users/danvk/tmp/IM Logs.sit Folder/Adium/Users/dantheox/Logs",
  '/Volumes/Backup 5:10:04/Old Library/Application Support/Adium/Users/dantheox/Logs'
]


def ReadAdiumLog(path):
  data = file(path).read()
  enc = chardet.detect(data)['encoding']
  data = data.decode(enc)

  lines = data.split('\n')

  # e.g. 'A 2003-02-24 -0600'
  m = re.search(r'A (\d\d\d\d-\d\d-\d\d) ([-+]\d\d\d\d)$', lines[0])
  assert m, path
  date, timezone = m.groups()

  # e.g. '(20:41:18)iambatman456:how are you?'
  m = re.search(r'\((\d\d:\d\d:\d\d)\)', lines[1])
  assert m, lines[1]
  t = m.group(1)

  # Buddy's handle comes from file name.
  m = re.match(r'([^ ]*) \(', os.path.basename(path))
  assert m, path
  buddy = m.group(1)

  dt = parser.parse('%s %s %s' % (date, t, timezone))
  assert dt

  return dt, buddy, '\n'.join(lines[1:]) + '\n'


def Run(dirs):
  for d in dirs:
    logs = glob.glob('%s/*/*.adiumLog' % d)
    print 'Found %d logs' % len(logs)

    daily_logs = defaultdict(list)  # YYYY-MM-DD -> [(date, buddy, logs), ... ]
    for log_file in logs:
      date, buddy, chat_contents = ReadAdiumLog(log_file)
      day = date.strftime('%Y-%m-%d')
      daily_logs[day].append((date, buddy, chat_contents))

    for day in sorted(daily_logs.keys()):
      d = parser.parse(day)
      chats = []  # [ (lines, user), (lines, user), ... ]
      for log in daily_logs[day]:
        chats.append((log[2].count('\n'), log[1]))
      chats.sort()
      chats.reverse()

      summary = ', '.join(['%s (%d)' % (c[1], c[0]) for c in chats])
      summary = 'Chats with ' + summary 
      utils.WriteSingleSummary(d, maker='adium', summary=summary)


if __name__ == '__main__':
  if len(sys.argv) == 1:
    sys.stderr.write('Usage: %s path/to/Adium/Users/username/Logs\n');
    sys.exit(1)

  Run(sys.argv[1:])
