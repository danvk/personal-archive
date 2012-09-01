#!/usr/bin/python
"""Reads in data from my high school Classic Mac OS journal program."""

import journal
import json
import os

def Run():
  path = '~/Dropbox/Treasure Trove/misc journals/summer 2001/journal.json'
  path = os.path.expanduser(path)

  entries = json.load(file(path))
  journal.ImportJournal(entries, 'journwfork')


if __name__ == '__main__':
  Run()
