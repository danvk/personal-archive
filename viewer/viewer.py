#!/usr/bin/python2.7

import web
import sys
import json
from datetime import date
from cStringIO import StringIO
import itertools

sys.path.append('..')

import utils

urls = (
  '/', 'index'
)


def USWeekDay(d):
  """Returns weekday, US-style (0=Sunday, 6=Saturday)."""
  w = d.weekday()
  if w == 6: return 0
  return w + 1


class index:
  def GET(self):
    days = utils.GetDailySummaries(dense=True)
    day_keys = sorted(days.keys())
    
    out = StringIO()
    out.write("""<html>
<head>
<link rel="stylesheet" href="static/viewer.css" />
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>
<script src="static/viewer.js"></script>
</head>\n""")
    for year, keys in itertools.groupby(day_keys, lambda d: d.year):
      out.write('<div class=year><h1>%d</h1>\n' % year)
      for month, keys in itertools.groupby(keys, lambda d: d.month):
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

    days_rekey = {}
    for day, value in days.iteritems():
      if value:
        days_rekey[day.strftime('%Y-%m-%d')] = value

    out.write('<div id=summary></div>');
    out.write('<script type="text/javascript">var data=%s;</script>' % json.dumps(days_rekey))
    out.write('</html>')
    return out.getvalue()


if __name__ == "__main__": 
  app = web.application(urls, globals())
  app.run()        
