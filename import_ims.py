#!/usr/bin/python2.7
"""General importer for all IM logs.

Strategy: look through 'staging' for all these files:
.adiumLog: plaintext Adium chat transcript
    .html: HTML Adium chat transcript
    .chat: iChat log (Binary typedstream)
"""

from BeautifulSoup import BeautifulSoup, NavigableString
from collections import defaultdict
import os
import re
from dateutil import parser
import subprocess


def Run():
  logs_by_type = defaultdict(list)

  log_types = set(['.adiumLog', '.chat', '.html'])

  for root, dirs, files in os.walk('staging'):
    for path in files:
      base, ext = os.path.splitext(path)
      full_path = os.path.join(root, path)

      if ext in log_types:
        logs_by_type[ext].append(full_path)


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

  return dt, buddy, '\n'.join(lines[1:]) + '\n'


def ReadHtmlLog(path):
  """Returns a (datetime, buddy, chat contents) tuple."""
  m = re.match(r'([^ ]*) \((\d\d\d\d\|\d\d\|\d\d)\)', os.path.basename(path))
  assert m
  buddy, date = m.groups()

  # <div class="send"><span class="timestamp">01:24:59</span> <span class="sender">dantheox: </span><pre class="message">Hey Andy Bill, are you going to be playing ultimate again this summer?</pre></div>
  # <div class="receive"><span class="timestamp">01:25:07</span> <span class="sender">awill567: </span><pre class="message">yeah</pre></div>
  out = ""
  bs = BeautifulSoup(file(path))
  for i, div in enumerate(bs("div")):
    parts = []
    for t in div:
      if isinstance(t, NavigableString):
        parts.append(t.string)
      else:
        parts.append(t.renderContents())
        
    out += ''.join(parts)
    out += '\n'
  chat_contents = out

  ts = bs("span", "timestamp")[0].string

  datetime = parser.parse(date.replace('|', '/') + ' ' + ts)
  assert datetime

  return datetime, buddy, chat_contents


def ReadiChatLog(path):
  output = subprocess.check_output(["./extract", path])
  lines = output.split('\n')
  buddy = lines[0]
  dt = parser.parse(lines[1])
  chat_contents = lines[2:]

  return dt, buddy, chat_contents
