#!/usr/bin/python2.7

from collections import defaultdict
from datetime import date, timedelta
import utils

start_year = 2000
end_year = date.today().year

makers = utils.GetAllMakers()

# date -> # of makers
days = defaultdict(int)

for maker in makers:
  dates = utils.GetActiveDaysForMaker(maker)
  for d in dates:
    days[d] += 1


def USWeekDay(d):
  """Returns weekday, US-style (0=Sunday, 6=Saturday)."""
  w = d.weekday()
  if w == 6: return 0
  return w + 1

def DaysInYear(year):
  days = []
  d = date(year, 1, 1)
  while d.year == year:
    days.append(d)
    d += timedelta(days=1)
  return days


# 365 days * 3 pixels/day = 1095 pixels

print """
<html>
<head>
<style type="text/css">
div.off, div.on {
  display: inline-block;
  width: 3px;
  height: 15px;
  padding: 0;
  margin: 0;
}
div.off {
  background-color: lightgray;
}
div.on {
  background-color: green;
}
</style>
</head><body>
"""

for year in range(start_year, end_year + 1):
  print '<b>%s</b>' % year

  klasses = []
  for d in DaysInYear(year):
    count = days[d]
    klasses.append('on' if count else 'off')

  print ''.join(['<div class="%s"></div>' % k for k in klasses])
  print '<br/>'


print """
</body>
</html>
"""
