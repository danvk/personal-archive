#!/usr/bin/python2.7

import plistlib
import journal
import os
import re
from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.plaintext.writer import PlaintextWriter

import StringIO


def Run():
  this_dir = os.path.dirname(__file__)
  journal_file = os.path.join(this_dir, '../old journal app/journal.dat')
  raw_entries = plistlib.readPlist(journal_file)

  entries = {}
  for k, v in raw_entries.iteritems():
    # 12/29/2001 -> 2001-12-29
    new_k = re.sub(r'(\d\d)/(\d\d)/(\d\d\d\d)', r'\3-\1-\2', k)

    if isinstance(v, plistlib.Data):
      f = StringIO.StringIO(v.data)
      doc = Rtf15Reader.read(f)
      v = PlaintextWriter.write(doc).getvalue()

    entries[new_k] = v

  journal.ImportJournal(entries, 'osxapp')


if __name__ == '__main__':
  Run()
