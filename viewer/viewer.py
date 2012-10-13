#!/usr/bin/python2.7

import web
import sys
import json
import os
from collections import defaultdict
from datetime import date, datetime, timedelta
from cStringIO import StringIO
from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.xhtml.writer import XHTMLWriter
import itertools

import pyth.plugins.rtf15.reader

sys.path.append('..')

import utils

# HACK!
pyth.plugins.rtf15.reader._CODEPAGES[78] = "10001"

urls = (
  '/', 'index',
  '/day/(\d\d\d\d/\d\d/\d\d)', 'oneday',
  '/get_summary', 'get_summary',
  '/coverage', 'coverage'
)

start_year = 2000
end_year = date.today().year

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


def RekeyDates(d):
  """Rekeys a dict by YYYY-MM-DD instead of date objects."""
  rekey = {}
  for day, value in d.iteritems():
    if value:
      rekey[day.strftime('%Y-%m-%d')] = value
  return rekey


class index:
  def GET(self):
    days = utils.GetDailySummaries(dense=True)
    day_keys = sorted(days.keys())
    
    out = StringIO()
    out.write("""<html>
<head>
<link rel="stylesheet" href="/static/viewer.css" />
<script src="/static/jquery-1.7.min.js"></script>
<script src="/static/viewer.js"></script>
</head>
<body>
""")

    out.write("<div id='calendar'>\n")

    for year, keys in itertools.groupby(reversed(list(day_keys)), lambda d: d.year):
      out.write('<div class=year><h1>%d</h1>\n' % year)
      for month, keys in itertools.groupby(reversed(list(keys)), lambda d: d.month):
        out.write('<div class="month month-%d">\n' % month)
        start_d = date(year, month, 1)
        out.write('<h2>%s</h2>' % start_d.strftime('%B'))
        for pad in range(0, USWeekDay(start_d)):
          out.write('<div class="day empty"></div>')
          
        for day in keys:
          if days[day]:
            out.write('<div class="day on" d="%s">' % (day.strftime('%Y-%m-%d')))
          else:
            out.write('<div class="day">')
          out.write('%d</div>' % day.day)
        out.write('</div>\n')
      out.write('</div>\n')

    out.write("</div>\n")

    out.write('<div id=summary></div>');
    out.write('<script type="text/javascript">var data=%s;</script>' % json.dumps(RekeyDates(days)))
    out.write('</html>')
    return out.getvalue()


class oneday:
  def GET(self, day):
    out = StringIO()
    out.write("""<html>
<head>
<link rel="stylesheet" href="/static/viewer.css" />
<script src="/static/jquery-1.7.min.js"></script>
</head>
<body>
<div id="oneday">
""")
    data = utils.GetOneDay(datetime.strptime(day, '%Y/%m/%d').date())
    for maker in sorted(data.keys()):
      out.write('<h2>%s</h2>\n' % maker)
      # TODO(danvk): include URL, thumbnail if available.
      out.write('<p>%s</p>\n' % data[maker]['summary']['summary'].encode('utf8'))

      if 'originals' in data[maker]:
        originals = data[maker]['originals']
        for filename in sorted(originals.keys()):
          out.write('<h3>%s</h3>\n' % filename)
          _, ext = os.path.splitext(filename)
          if ext == '.txt':
            out.write('<pre>%s</pre>\n' % originals[filename])
          elif ext == '.html':
            out.write(originals[filename])
          elif ext == '.rtf':
            f = StringIO(originals[filename])
            doc = Rtf15Reader.read(f)
            html = XHTMLWriter.write(doc).getvalue()
            out.write(html)
          else:
            out.write('<p>(Unknown format "%s")</p>' % ext)
            

      out.write('<hr/>\n')

    out.write('</div></body></html>')
    return out.getvalue()


class get_summary:
  def POST(self):
    params = web.input()
    day_str = params['day']
    day = datetime.strptime(day_str, '%Y-%m-%d')
    print 'Day: %s' % day
    return json.dumps(utils.GetSummariesForDay(day))



class coverage:
  def GET(self):
    makers = sorted(utils.GetAllMakers())
    days = utils.GetDailySummaries()

    out = StringIO()
    out.write('''<html>
<head>
  <link rel=stylesheet href='/static/coverage.css' />
  <script src="/static/jquery-1.7.min.js"></script>
  <script type="text/javascript">
    var makers = %s;
    var day_to_makers = %s;
  </script>
  <script src="/static/coverage.js"></script>
</head>
<body>
  <b style="color:transparent; margin-right: 4px;">0000</b>
  ''' % (json.dumps(makers), json.dumps(RekeyDates(days))))

    for m in range(1, 13):
      month_name = date(2004, m, 1).strftime('%B')
      month_length = (date(2004, (m % 12) + 1, 1) + timedelta(days=-1)).day
      out.write('<div class="month days%d">%s</div>\n' % (month_length, month_name))
    out.write('<br/>\n')

    for year in range(start_year, end_year + 1):
      out.write('<div class=year><b>%s</b>\n' % year)

      klasses = []
      for d in DaysInYear(year):
        k = 'on' if d in days else 'off'
        if d.day == 1:
          k += ' first'
          prev_date = (d + timedelta(days=-1))
          if prev_date.month == 2 and prev_date.day == 28:
            k += ' first-no-leap'
        klasses.append(k)

      out.write(''.join(['<div class="%s"></div>' % k for k in klasses]))
      out.write('\n</div>\n')

    out.write("""
  <p><span id="num-on"></span> days with activity.</p>
  <div id=checks></div>
  <p>
    <button id='btnNone'>Select None</button>
    &nbsp; &nbsp;
    <button id='btnAll'>Select All</button>
  </p>
  </body>
  </html>
  """)
    return out.getvalue()
      


if __name__ == "__main__": 
  app = web.application(urls, globals())
  app.run()        

# Useful bits:
# web.header('Content-Type', 'text/plain')
# params = web.input()
# params['id']
