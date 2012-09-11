#!/usr/bin/python2.7
"""Imports the "Old Mail of unknown provenance" .tar.gz files."""

import chardet
import tarfile
import sys
import re
from dateutil import parser
import utils

dry_run = False


def ParseMessage(contents):
  msg = ''
  headers = {}
  in_headers = True
  last_key = None
  is_first = True
  for line in contents.split('\n'):
    if is_first:
      assert ':' in line
      is_first = False

    if line == '':
      in_headers = False
      continue

    if in_headers:
      if not ':' in line:
        assert last_key, contents
        headers[last_key] += ', ' + line.strip()
        continue
      m = re.match(r'^([A-Za-z]*): *(.*)', line)
      assert m, contents
      key, value = m.groups()
      if key == 'To' and ',' in value:
        value = re.sub(r', (.*)', r' <\1>', value)
      headers[key] = value.strip()
      last_key = key

    if not in_headers:
      msg += line + '\n'

  for k in ['Received', 'Sent']:
    if k in headers:
      headers[k] = parser.parse(headers[k])

  return headers, msg
  

acc = utils.EntryAccumulator(lambda x: x[0].date())

for f in sys.argv[1:]:
  tf = tarfile.open(f, 'r')
  for member in tf.getmembers():
    if not member.isfile(): continue
    if '.DS_Store' in member.name: continue

    s = tf.extractfile(member)
    if not s:
      sys.stderr.write('Could not extract %s\n' % member.name)
      continue
    contents = s.read()
    contents = re.sub(r'\r\n', '\n', contents)
    contents = re.sub(r'\r', '\n', contents)
    headers, msg = ParseMessage(contents)
    headers['Content'] = msg

    acc.add((headers['Sent'], headers['To'], contents))


for day, entries in acc.iteritems():
  summary = utils.OrderedTallyStr([x[1] for x in entries])
  utils.WriteSingleSummary(day, maker='old-emails',
      summary=utils.RemoveNonAscii(summary), dry_run=dry_run)

  original = '\n\n\n'.join([entry[2] for entry in entries])
  utils.WriteOriginal(day, maker='old-emails', contents=original,
      filename='emails.txt', dry_run=dry_run)
