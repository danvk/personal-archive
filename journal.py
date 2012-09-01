"""Utilities for importing journal entries."""

import utils
from datetime import datetime

def ImportJournal(entries, maker, url_maker=None):
  for date_str, entry in entries.iteritems():
    if not entry: continue

    d = datetime.strptime(date_str, '%Y-%m-%d')
    summary = utils.SummarizeText(entry)
    url = None
    if url_maker:
      url = url_maker(d)
    utils.WriteSingleSummary(d, maker=maker, summary=summary, url=url)
