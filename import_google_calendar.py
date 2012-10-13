#!/usr/bin/python2.7
"""Imports Google Calendar events into the archive.

Assumes you've downloaded all of them by running something like:
google calendar list --date 2005-09-03,$(date +%Y-%m-%d) --delimiter '_!_!_' --fields title,when,where > staging/calendar.data.txt
"""

from dateutil import parser
import utils

acc = utils.EntryAccumulator(lambda x: x[0].date())

for line in file('staging/calendar.data.txt'):
  description, dtspan, where = line.strip().split('_!_!_')
  if ' - ' in dtspan:
    start, stop = dtspan.split(' - ')
  else:
    start, stop = dtspan, dtspan

  try:
    start = parser.parse(start)
  except ValueError as e:
    print start
    print line
    raise e

  try:
    stop = parser.parse(stop)
  except ValueError as e:
    print stop
    print line
    raise e

  acc.add((start, stop, description, where))


def FormatRange(start, stop):
  # TODO(danvk): include stop?
  return start.strftime('%I:%m %p')


for day, entry in acc.iteritems():
  summary = ''
  for start, stop, description, where in sorted(entry):
    summary += '%s: %s' % (FormatRange(start, stop), description)
    if where != 'None' and where not in description:
      summary += ' @ ' + where
    summary += '\n'

  utils.WriteSingleSummary(day, maker="gcal", summary=summary.strip())
