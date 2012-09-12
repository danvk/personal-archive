#!/usr/bin/python2.7

from collections import defaultdict
import re
import email
import json
import sys
from dateutil import parser
import gmail_utils
import utils

dry_run = False


def Run(json_path):
  acc = utils.EntryAccumulator(lambda x: x['date'].date())

  data = json.load(file(json_path))
  for idx, msg in enumerate(data):
    data = gmail_utils.ParseMessagePair(msg, 'text/html')
    acc.add(data)

  for day, entries in acc.iteritems():
    day_counts = defaultdict(int)
    user_chats = defaultdict(list)

    for msg in entries:
      m = re.search(r'([0-9a-zA-Z.]+)@', msg['from'])
      assert m, msg['from']
      buddy = m.group(1)
      day_counts[msg['from']] += msg['contents'].count('<div>')
      user_chats[buddy].append(msg['contents'])

    summary = utils.OrderedTallyStr(day_counts)
    utils.WriteSingleSummary(day, 'gmail-chat', summary=summary, dry_run=dry_run)
    for user, chats in user_chats.iteritems():
      filename = user + '.html'
      contents = '<html>' + '<hr/>\n'.join(chats) + '</html>'
      utils.WriteOriginal(day, 'gmail-chat', filename=filename,
          contents=contents.encode('utf8'), dry_run=dry_run)


if __name__ == '__main__':
  assert 2 == len(sys.argv)
  Run(sys.argv[1])

