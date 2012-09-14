#!/usr/bin/python2.7
"""Import messages from various sent mbox files.

(mount various Backup images)
find /Volumes/Backup\ * -name 'mbox' -iregex '.*sent.*' -print0 | xargs -0 ./scan-mbox.py --output_json > staging/sent-mbox.json
./import_sent_mbox.py staging/sent-mbox.json
"""

import re
import json
import sys
import utils
import dateutil.parser
import email.Parser
import itertools
from collections import defaultdict

# dry_run = True
dry_run = False

assert len(sys.argv) == 2
json_file = sys.argv[1]

parsestr = email.Parser.Parser().parsestr
raw_msgs = json.load(file(json_file))
msgs = []
for raw_msg in raw_msgs:
  m = parsestr(raw_msg.encode('utf8'))
  if 'Date' not in m:
    print m
    sys.exit(0)

  msgs.append(m)


acc = utils.EntryAccumulator(lambda x: dateutil.parser.parse(x['Date']))
for msg in msgs:
  if 'Date' not in msg:
    print msg
    sys.exit(1)
  acc.add(msg)


for day, msgs in acc.iteritems():
  def all_to(msg):
    return [to.strip() for to in msg['To'].split(',')]

  summary = utils.OrderedTallyStr(
      itertools.chain.from_iterable([all_to(msg) for msg in msgs]))
  summary = 'Sent emails to ' + summary
  utils.WriteSingleSummary(day, maker='sent-mbox', summary=summary, dry_run=dry_run)

  counts = defaultdict(int)
  for msg in msgs:
    to = msg['To']
    if ',' in to:
      to = 'multiple'
    else:
      m = re.search(r'([-a-z0-9A-Z.]+@[-a-z0-9A-Z.]+)', to)
      if m:
        to = m.group(1)
    count = '' if to not in counts else str(counts[to])
    counts[to] += 1
    utils.WriteOriginal(day, maker='sent-mbox', filename=to + count + '.txt',
        contents=str(msg), dry_run=dry_run)
