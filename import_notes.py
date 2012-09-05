#!/usr/bin/python2.7

from collections import defaultdict
import json
import email.parser
import datetime
import dateutil.parser
import utils

data = json.load(file('staging/gmail-notes.json'))

by_day = defaultdict(list)  # date -> [(subject, contents), ...]

for idx, msg in enumerate(data):
  body = msg[0][1]
  header = msg[1][1]

  fp = email.parser.FeedParser()
  fp.feed(header)
  fp.feed(body)
  m = fp.close()
  assert m

  subj = m['Subject']
  dt = dateutil.parser.parse(m['Date'])

  if 'Big password list' in subj:
    continue

  contents = None
  for part in m.walk():
    if part.get_content_type() == 'text/plain':
      contents = part.get_payload()
      break

  if not contents:
    continue

  if contents.count('\n') < 5:
    continue

  day = datetime.date(dt.year, dt.month, dt.day)
  by_day[day].append((subj, contents))


for day, notes in by_day.iteritems():
  summary = ', '.join([subj for subj, _ in notes])
  utils.WriteSingleSummary(d=day, maker="notes", summary=summary)

  for idx, note in enumerate(notes):
    subj, contents = note
    str_idx = str(idx) if len(notes) > 1 else ''
    utils.WriteOriginal(d=day, maker="notes",
        filename="note%s.txt" % str_idx, contents=contents.encode('utf8'))

  print '%s: %s' % (day, summary)
