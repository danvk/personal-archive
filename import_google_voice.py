#!/usr/bin/python2.7
"""Imports Google Voice conversations from a CSV file.

This can be created by running sms2csv.py and copying the resulting file into
the staging directory.
"""

import csv
import json
import re
import sys
import utils
from collections import defaultdict
from dateutil import parser
import itertools

dry_run = False

if len(sys.argv) != 2:
  sys.stderr.write('Usage: %s path/to/gvsms.csv\n', sys.argv[0])
  sys.exit(1)


sms_file = sys.arv[1]
data = csv.DictReader(file(sms_file))

# Prepopulated with a few special numbers that have never texted me back.
# Sample google-voice.config.json file:
# {
#   "extra-numbers": {
#     "+19876543210": "John Doe",
#     "+11234567890": "Jane Doe"
#   }
# }
config = json.load(file("google-voice.config.json"))
number_to_name = config['extra-numbers']
acc = utils.EntryAccumulator(lambda row: parser.parse(row['date']))

for idx, row in enumerate(data):
  # i.e. "Me:" -> "Me"
  row['from'] = re.sub(r':$', '', row['from'])

  num, name = row['phone'], row['from']
  if name == '': continue

  acc.add(row)
  if name == 'Me': continue

  if num in number_to_name:
    assert number_to_name[num] == name, '%5d %s: %s vs %s (%s)' % (
        idx, num, name, number_to_name[num], row)
  else:
    number_to_name[num] = name


for day, entries in acc.iteritems():
  # Collect all the entries into a single text file and summarize them.
  others = []
  by_other = defaultdict(list)
  for row in sorted(entries, key=lambda r: parser.parse(r['time'])):
    other = number_to_name[row['phone']]
    others.append(other)
    by_other[other].append('(%8s) %14s: %s' % (row['time'], row['from'], row['text']))

  summary = utils.OrderedTallyStr(others)

  text = ''
  for other in sorted(by_other.keys()):
    text += '%s\n----\n' % other
    text += '\n'.join(by_other[other])
    text += '\n\n'

  utils.WriteSingleSummary(day, maker='sms', summary=summary, dry_run=dry_run)
  utils.WriteOriginal(day, maker='sms',
      filename='sms.txt', contents=text, dry_run=dry_run)
