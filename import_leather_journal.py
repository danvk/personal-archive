#!/usr/bin/python
"""Imports entries in the Leather Journal into my archive.

Assumes data is in staging/leather.transcribed.txt.
Format is:
----
(date)
contents
"""

import os
import sys
import journal
from collections import defaultdict
from datetime import date
from dateutil import parser


def Run(maker, leather_file):
  lines = file(leather_file).read().split('\n')

  by_date = defaultdict(str)  # yyyy-mm-dd -> journal

  i = 0
  last_date = None
  while i < len(lines):
    if lines[i] == '----':
      i += 1
      try:
        last_date = parser.parse(lines[i])
        i += 1
      except ValueError:
        print 'Unable to parse %s' % lines[i]
        assert False
      last_date = last_date.strftime('%Y-%m-%d')
      continue

    assert last_date
    by_date[last_date] += lines[i] + '\n'
    i += 1

  journal.ImportJournal(by_date, maker)
  sys.stderr.write('Imported %d entries under "%s"\n' % (len(by_date), maker))


if __name__ == '__main__':
  assert len(sys.argv) == 3, "Usage: %s (maker) (path to journal)"
  Run(sys.argv[1], sys.argv[2])
