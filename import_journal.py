#!/usr/bin/python
"""Imports entries in the a journal into the archive.

Usage: ./import_journal.py (maker) (path to journal.txt)

Entries in the journal are delimited by a line with four dashes followed by the
date, followed by the entry, like so:
----
(date1)
contents1

----
(date2)
contents2

...
"""

import os
import sys
import chardet
import journal
from collections import defaultdict
from datetime import date
from dateutil import parser


def Run(maker, path):
  data = file(path).read()
  enc = chardet.detect(data)['encoding']
  data = data.decode(enc)
  lines = data.split('\n')

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
