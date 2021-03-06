"""Utilities for importing journal entries."""

import utils
from datetime import datetime

def ImportJournal(entries, maker, url_maker=None, dry_run=False):
  """entries maps %Y-%m-%d -> contents"""
  for date_str, entry in entries.iteritems():
    if not entry: continue

    d = datetime.strptime(date_str, '%Y-%m-%d')
    summary = utils.SummarizeText(entry)
    url = None
    if url_maker:
      url = url_maker(d)
    utils.WriteSingleSummary(
        d, maker=maker, summary=summary, url=url, dry_run=dry_run)
    utils.WriteOriginal(
        d, maker=maker, dry_run=dry_run,
        contents=entry.encode('utf8'), filename='journal.txt')
