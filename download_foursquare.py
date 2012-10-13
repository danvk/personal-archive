#!/usr/bin/python2.7
"""Scrape foursquare data into staging/foursquare.json

TODO: Write up the simplest way to get a Foursquare OAuth token.
"""

import sys
import json
import urllib2

assert len(sys.argv) == 3, (
  'Usage: %s OAUTH_TOKEN foursquare.checkins.json' % sys.argv[0])

oauth_token, output_file = sys.argv[1:]

batch_size = 250
endpoint = 'https://api.foursquare.com/v2/users/self/checkins?oauth_token=%s&v=20120918&limit=%d' % (oauth_token, batch_size)

# TODO: support resume
offset = 0
datas = []
while True:
  url = endpoint
  if offset:
    url += '&offset=%d' % offset
  response = urllib2.urlopen(url)
  data = json.load(response)

  assert data['meta']['code'] == 200
  assert 'errorType' not in data['meta'], json.dumps(data['meta'])

  datas.append(data)
  json.dump(datas, file(output_file, 'w'))

  num_checkins = data['response']['checkins']['count']
  checkins = data['response']['checkins']['items']
  offset += len(checkins)
  print 'Fetched %d/%d checkins' % (offset, num_checkins)
  if len(checkins) != batch_size or offset >= num_checkins:
    break

print 'DONE'
