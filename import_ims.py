#!/usr/bin/python2.7
"""General importer for all IM logs.

Strategy: look through 'staging' for all these files:
.adiumLog: plaintext Adium chat transcript
    .html: HTML Adium chat transcript
    .chat: iChat log (Binary typedstream)
"""

from BeautifulSoup import BeautifulSoup, NavigableString
from collections import defaultdict
import chardet
import os
import re
import sys
import utils
from dateutil import parser
import subprocess


def ReadAdiumLog(path):
  """Returns a (datetime, buddy, chat contents) tuple."""
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

  return dt, buddy, '\n'.join(lines[1:]) + '\n', path


def ReadHtmlLog(path):
  """Returns a (datetime, buddy, chat contents) tuple."""
  m = re.match(r'([^(]*) \((\d\d\d\d\|\d\d\|\d\d)\)', os.path.basename(path))
  assert m
  buddy, date = m.groups()

  # <div class="send"><span class="timestamp">01:24:59</span> <span class="sender">dantheox: </span><pre class="message">Hey Andy Bill, are you going to be playing ultimate again this summer?</pre></div>
  # <div class="receive"><span class="timestamp">01:25:07</span> <span class="sender">awill567: </span><pre class="message">yeah</pre></div>
  out = ""
  bs = BeautifulSoup(file(path))

  try:
    ts = bs("span", "timestamp")[0].string
  except IndexError:
    # Chat has no actual content. Not interesting!
    return None

  for i, div in enumerate(bs("div")):
    parts = []
    for t in div:
      if isinstance(t, NavigableString):
        parts.append(t.string)
      else:
        parts.append(t.renderContents())

    try:
      out += u''.join(parts)
    except UnicodeDecodeError:
      out += u''.join([p.decode('utf8') for p in parts])
    out += '\n'
  chat_contents = out

  datetime = parser.parse(date.replace('|', '/') + ' ' + ts)
  assert datetime

  return datetime, buddy, chat_contents, path


def ReadiChatLog(path):
  output = subprocess.check_output(["./extract", path])
  lines = output.split('\n')
  buddy = lines[0]
  dt = parser.parse(lines[1])
  chat_contents = '\n'.join(lines[2:]).decode('utf8') + '\n'

  return dt, buddy, chat_contents, path


def AddToDailyLog(daily_logs, t):
  if not t: return
  date, buddy, chat_contents, path = t
  day = date.strftime('%Y-%m-%d')

  for _, b, c, _ in daily_logs[day]:
    if b == buddy and c == chat_contents:
      return
  daily_logs[day].append((date, buddy, chat_contents, path))
  

def Run(paths=None):
  logs_by_type = defaultdict(list)

  log_types = set(['.adiumLog', '.chat', '.html'])

  if paths:
    for path in paths:
      base, ext = os.path.splitext(path)
      assert ext in log_types
      logs_by_type[ext].append(path)
  else:
    for root, dirs, files in os.walk('staging'):
      for path in files:
        base, ext = os.path.splitext(path)
        full_path = os.path.join(root, path)

        if ext in log_types:
          logs_by_type[ext].append(full_path)

  daily_logs = defaultdict(list)  # YYYY-MM-DD -> [(date, buddy, logs), ... ]

  if '.html' in logs_by_type:
    for path in logs_by_type['.html']:
      print path
      AddToDailyLog(daily_logs, ReadHtmlLog(path))

  if '.adiumLog' in logs_by_type:
    for path in logs_by_type['.adiumLog']:
      print path
      AddToDailyLog(daily_logs, ReadAdiumLog(path))

  if '.chat' in logs_by_type:
    for path in logs_by_type['.chat']:
      print path
      AddToDailyLog(daily_logs, ReadiChatLog(path))

  for day in sorted(daily_logs.keys()):
    d = parser.parse(day)
    chats = []  # [ (lines, user), (lines, user), ... ]
    for log in daily_logs[day]:
      chats.append((log[2].count('\n'), log[1]))
    chats.sort()
    chats.reverse()

    summary = ', '.join(['%s (%d)' % (c[1], c[0]) for c in chats])
    summary = 'Chats with ' + summary 
    utils.WriteSingleSummary(d, maker='chat', summary=summary)

    for _, buddy, contents, path in daily_logs[day]:
      print 'Writing %s' % path
      utils.WriteOriginal(d, maker='chat', filename=('%s.txt' % buddy), contents=contents.encode('utf8'))


if __name__ == '__main__':
  if len(sys.argv) >= 2:
    Run(sys.argv[1:])
  else:
    Run()
