#!/usr/bin/python2.7
"""Imports Google Voice conversations from a CSV file.

This can be created by running sms2csv.py and copying the resulting file into
the staging directory.
"""

import csv
import re
import utils
from collections import defaultdict
from dateutil import parser

dry_run = False

sms_file = 'staging/GVsms 2012-09-08 18-24-18.csv'
data = csv.DictReader(file(sms_file))

# Prepopulated with a few special numbers that have never texted me back.
number_to_name = {
  '+12077250808': 'David Quaid',
  '+14153519439': 'Jeremy Ginsberg',
  '+18185770007': 'Dani Derse',
  '+16464508191': 'Alastair Tse?',
  '+14155137688': 'Bradvertising',
  '+13472212282': 'Anthony Robredo'
  # There are a bunch of other numbers that are numbers only (no names)
}
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
  counts = defaultdict(int)
  text = ''
  for row in entries:
    other = number_to_name[row['phone']]
    counts[other] += 1
    direction = '->' if row['from'] == 'Me' else '<-'
    text += '%8s %s %s: %s\n' % (row['time'], direction, other, row['text'])

  counts = sorted(counts.items(), key=lambda x: -x[1])
  summary = ', '.join(['%s (%d)' % (c[0], c[1]) for c in counts])

  utils.WriteSingleSummary(day, maker='sms', summary=summary, dry_run=dry_run)
  utils.WriteOriginal(day, maker='sms',
      filename='sms.txt', contents=text, dry_run=dry_run)