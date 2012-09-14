#!/usr/bin/python2.7

import sys
import json
import argparse
import mailbox
import dateutil.parser
import itertools

import email.Parser

# Source: http://code.activestate.com/recipes/576553-extract-emails-from-a-mbox-read-on-stdin/
def mbox_generator(input):
  '''Yield each message found in 'input'.'''
  assert type(input) is file
  data = []
  while True:
    line = input.readline()
    if line[:5] == 'From ' or line == '':
      if data and data != ['']:
        yield ''.join(data)
        data = [line]
      elif line == '':
        raise StopIteration
      else:
        data = [line]
    else:   
      data.append(line)


parser = argparse.ArgumentParser(description='Read from mbox files.')
parser.add_argument('mboxes', metavar='mbox', type=str, nargs='+',
                    help='An mbox file to process')
parser.add_argument('--print_field', dest='print_field', default=None,
                    help='Print one field from each message.')
parser.add_argument('--reformat_date', dest='reformat_date', action='store_const',
                    default=False, const=True,
                    help=('Interpret argument values as dates and reformat '
                    'them as YYYY-MM-DD HH:MM:SS before printing.'))
parser.add_argument('--print_mbox_name', dest='print_mbox_name', action='store_const',
                    default=False, const=True,
                    help='Print each mbox path before processing it.')

parser.add_argument('--sort_values', dest='sort_values', action='store_const',
                    default=False, const=True,
                    help='Sort values within each mbox before printing.')

parser.add_argument('--print_counts', dest='print_counts', action='store_const',
                    default=False, const=True,
                    help='Print message counts for each mbox')

parser.add_argument('--output_json', dest='output_json', action='store_const',
                    default=False, const=True,
                    help='Collect unique messages and output a JSON array, '
                    'with each entry containing a header->value dict.')

args = parser.parse_args()

json_out = []
parsestr = email.Parser.Parser().parsestr
for path in args.mboxes:
  if args.print_mbox_name:
    print path

  count = 0
  vals = []
  for raw_msg in mbox_generator(file(path)):
    msg = parsestr(raw_msg)
    if args.output_json:
      json_out.append((msg['Message-Id'], raw_msg))

    count += 1
    pf = args.print_field
    if pf:
      if pf in msg:
        v = msg[pf]
        if args.reformat_date:
          try:
            v = dateutil.parser.parse(v).strftime('%Y-%m-%d %H:%M:%S')
          except ValueError as e:
            sys.stderr.write('Unable to parse "%s"\n' % v)
            raise e
        if args.sort_values:
          vals.append(v)
        else:
          print v
      else:
        print ''

  if args.sort_values:
    print '\n'.join(sorted(vals))
  if args.print_counts:
    print count

if args.output_json:
  # Choose the largest message for each unique ID.
  def msg_id(x):
    return x[0]
  json_out.sort(key=msg_id)
  unique_msgs = []
  for message_id, msgs in itertools.groupby(json_out, msg_id):
    msg_size = [(m, len(m)) for msg_id, m in msgs]
    msg_size.sort(key=lambda x: x[1], reverse=True)
    unique_msgs.append(msg_size[0][0].encode('utf-8'))

  print json.dumps(unique_msgs)
