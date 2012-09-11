#!/usr/bin/python
"""Reads in data from my high school Classic Mac OS journal program."""

import journal
import json
import os
import utils
from datetime import datetime

dry_run = False
def Run():
  path = '~/Dropbox/Treasure Trove/misc journals/summer 2001/journal.json'
  path = os.path.expanduser(path)

  entries = json.load(file(path))
  acc = utils.EntryAccumulator(lambda kv: datetime.strptime(kv[0], '%Y-%m-%d'))
  for kv in entries.iteritems():
    if not kv[1]: continue
    acc.add(kv)

  for day, kv in acc.iteritems():
    assert len(kv) == 1
    entry = kv[0][1]
    utils.WriteSingleSummary(day, maker='journwfork',
        summary=utils.SummarizeText(entry), dry_run=dry_run)
    utils.WriteOriginal(day, maker='journwfork', contents=entry.encode('utf8'),
        filename='journal.txt', dry_run=dry_run)


if __name__ == '__main__':
  Run()
