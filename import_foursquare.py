#!/usr/bin/python2.7

import sys
import json
import utils
from datetime import date, datetime

dry_run = False

assert len(sys.argv) == 2, (
  'Usage: %s foursquare.checkins.json' % sys.argv[0])

datas = json.load(file(sys.argv[1]))

checkins = []
for data in datas:
  batch_checkins = data['response']['checkins']['items']
  checkins += batch_checkins

checkins = sorted(checkins, key=lambda x: x['createdAt'])

acc = utils.EntryAccumulator(lambda x: date.fromtimestamp(x['time_t']))

for x in checkins:
  if 'venue' not in x:
    # mysterious!
    continue

  assert 'checkin' == x['type'] 
  try:
    venue = x['venue']
    loc = venue['location']
    c = {
      'time_t': x['createdAt'],
      'tz': x['timeZoneOffset'],
      'name': venue['name'],
      'location': {
        'city': loc['city'] if 'city' in loc else None,
        'state': loc['state'] if 'state' in loc else None,
        'country': loc['country'],
        'lat': loc['lat'],
        'lng': loc['lng']
      },
    }

    if 'shout' in x:
      c['shout'] = x['shout']

    if len(x['photos']['items']):
      # TODO: support >1 photo
      photo = x['photos']['items'][0]
      # also 36x36, 100x100, 300x300
      c['photo_url'] = photo['prefix'] + '500x500' + photo['suffix']

    if 'categories' in venue and len(venue['categories']) > 0:
      assert x['venue']['categories'][0]['primary']
      cat = x['venue']['categories'][0]
      c['type'] = cat['name']
      c['icon'] = cat['icon']['prefix'] + '32' + cat['icon']['suffix']

    if 'event' in x:
      c['event'] = x['event']['name']

  except Exception as e:
    print json.dumps(x, indent=2)
    raise e

  acc.add(c)


for day, checkins in acc.iteritems():
  anything_special = False
  checkin_strs = []
  full_strs = []
  for checkin in checkins:
    t = datetime.fromtimestamp(checkin['time_t'])
    s = '%s %s' % (t.strftime('%I:%M %p'), checkin['name'])
    full = '<p>%s</p>' % s

    if 'event' in checkin:
      s += ' ' + checkin['event']
      full += '%s<br/>' % checkin['event']
      
    if 'shout' in checkin:
      s += ' ' + checkin['shout']
      full += '%s<br/>' % checkin['shout']

    if 'photo_url' in checkin:
      s += ' (pic)'
      full += '<img src="%s" width=500 height=500 />' % checkin['photo_url']
      anything_special = True

    checkin_strs.append(s)
    full_strs.append(full)

  if len(checkins) > 1:
    summary = '\n' + '\n'.join(checkin_strs)
  else:
    summary = checkin_strs[0]

  if anything_special:
    full = '\n'.join(full_strs)
    utils.WriteOriginal(day, 'foursquare', filename='foursquare.html',
                        contents=full.encode('utf8'), dry_run=dry_run)
  utils.WriteSingleSummary(day, 'foursquare', summary=summary, dry_run=dry_run)
