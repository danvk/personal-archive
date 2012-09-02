#!/usr/bin/python
"""Imports OhLife journal entries into my archive.

Assumes ohlife JSON is in ../ohlife/entries.json.
"""

import os
import journal
import json

def UrlForDay(d):
  return 'https://ohlife.com/entries/%04d/%02d/%02d' % (
      d.year, d.month, d.day)


def Run():
  this_dir = os.path.dirname(__file__)
  ohlife_file = os.path.join(this_dir, '../ohlife/entries.json')
  entries = json.load(file(ohlife_file))

  journal.ImportJournal(entries, 'ohlife', UrlForDay)


if __name__ == '__main__':
  Run()
