#!/usr/bin/python2.7
"""Greps through really old emails, which may have odd characters in their file
names and dos-style newlines.
"""

import re
import sys
import glob

assert len(sys.argv) == 2
pat = sys.argv[1]

for f in glob.glob('*'):
  contents = file(f).read()
  contents = re.sub(r'\r\n', '\n', contents)
  contents = re.sub(r'\r', '\n', contents)
  for line in contents.split('\n'):
    if re.search(pat, line):
      print '%s: %s' % (f, line)
