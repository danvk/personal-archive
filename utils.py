"""Tools for building a personal archive in a canonical format."""

from collections import defaultdict
from datetime import date, timedelta
import os
import json
import re
import glob
import shutil

ArchiveDirectory = os.path.expanduser("~/Dropbox/Personal Archive")


def GetDirectoryForDay(d):
  """Returns path to (Personal Archive)/YYYY/MM/DD."""
  return '%s/%04d/%02d/%02d' % (ArchiveDirectory, d.year, d.month, d.day)


def MaybeMakeDirectory(day_dir):
  """Recursively create the path to a directory."""
  if os.path.exists(day_dir): return
  os.makedirs(day_dir)


def WriteSingleSummary(d=0, maker="", summary="", thumbnail="", url="", dry_run=False):
  """Write a single entry for a given date to disk.

  thumbnail is optional, all other arguments are mandatory."""
  assert d
  assert maker
  assert summary

  day_dir = GetDirectoryForDay(d)
  MaybeMakeDirectory(day_dir)
  filename = '%s/%s.json' % (day_dir, maker)

  data = {
    'summary': summary,
  }
  if thumbnail: data['thumbnail'] = thumbnail
  if url: data['url'] = url

  if dry_run:
    print 'Would write to %s:' % filename
    print json.dumps(data)
  else:
    json.dump(data, file(filename, 'wb'))


def WriteOriginal(d=0, maker="", filename="", contents="", dry_run=False):
  """Write out some unsummarized data for a particular maker.
  
  All arguments are required.
  """
  assert d
  assert maker
  assert filename
  assert contents

  maker_dir = '%s/%s' % (GetDirectoryForDay(d), maker)
  MaybeMakeDirectory(maker_dir)
  path = '%s/%s' % (maker_dir, filename)
  if not dry_run:
    file(path, 'wb').write(contents)
  else:
    print 'Would write %d bytes to %s' % (len(contents), path)


def SummarizeText(txt):
  """Cut text off at 160 characters and add '...' if necessary."""
  txt = re.sub(r'\n+', ' ', txt)
  if len(txt) < 160: return txt
  return txt[0:157] + '...'


def GetActiveDaysForMaker(maker):
  """Returns a sorted list of date objects which have data for the maker."""
  assert maker
  dates = []
  for path in glob.glob('%s/????/??/??/%s.json' % (ArchiveDirectory, maker)):
    m = re.search(r'(\d\d\d\d)/(\d\d)/(\d\d)/', path)
    assert m
    year, month, day = m.groups()
    dates.append(date(int(year), int(month), int(day)))

  dates.sort()
  return dates


def GetAllMakers():
  """Returns a list of all makers which have saved data in the archive."""
  makers = set()
  for path in glob.glob('%s/????/??/??/*.json' % ArchiveDirectory):
    maker_ext = os.path.basename(path)
    maker, ext = os.path.splitext(maker_ext)
    makers.add(maker)

  return list(makers)


def GetDailySummaries(dense=False):
  """Returns a date -> maker -> summary dict mapping."""
  days = defaultdict(lambda: {})

  for path in glob.glob('%s/????/??/??/*.json' % ArchiveDirectory):
    m = re.search(r'(\d\d\d\d)/(\d\d)/(\d\d)/([^.]+)', path)
    assert m
    year, month, day, maker = m.groups()
    if year < 2000:
      # (for now)
      continue
    d = date(int(year), int(month), int(day))
    days[d][maker] = json.load(file(path))

  if dense:
    d = date(2000, 1, 1)
    today = date.today()
    while d <= today:
      if d not in days:
        days[d] = {}
      d += timedelta(days=+1)

  return days


def GetOneDay(day):
  """Returns a mapping:
  maker -> {
    'summary': { 'summary': '', 'thumbnail': '', ... },
    'originals': { 'filename1': 'contents1', ... }
  }
  """
  out = {}
  day_dir = GetDirectoryForDay(day)
  for path in glob.glob(day_dir + '/*.json'):
    basename = os.path.basename(path)
    maker, ext = os.path.splitext(basename)
    out[maker] = {}
    out[maker]['summary'] = json.load(file(path))
    originals = {}
    for orig_path in glob.glob('%s/%s/*' % (day_dir, maker)):
      orig_name = os.path.basename(orig_path)
      originals[orig_name] = file(orig_path).read()
    if originals:
      out[maker]['originals'] = originals

  return out


def removeEmptyFolders(path):
  if not os.path.isdir(path):
    return
 
  # remove empty subfolders
  files = os.listdir(path)
  if len(files):
    for f in files:
      fullpath = os.path.join(path, f)
      if os.path.isdir(fullpath):
        removeEmptyFolders(fullpath)
 
  # if folder empty, delete it
  files = os.listdir(path)
  if len(files) == 0:
    print "Removing empty folder:", path
    os.rmdir(path)


def DeleteAllForMaker(maker):
  """Delete all traces of a particular maker in the archive directory."""
  files = glob.glob('%s/????/??/??/%s.json' % (ArchiveDirectory, maker))
  for path in files:
    print 'Deleting %s' % path
    os.remove(path)
  dirs = glob.glob('%s/????/??/??/%s' % (ArchiveDirectory, maker))
  for path in dirs:
    print 'Deleting directory %s' % path
    shutil.rmtree(path)

  removeEmptyFolders(ArchiveDirectory)


def FindFilesWithExtension(path, target_ext):
  """Returns a list of files under the path with the given extension."""
  matching_files = []
  for root, dirs, files in os.walk('staging'):
    for path in files:
      base, ext = os.path.splitext(path)
      if ext != target_ext: continue

      full_path = os.path.join(root, path)
      matching_files.append(full_path)

  return matching_files


def OrderedTallyStr(items):
  """Given a list containing duplicates, return a summary string.

  Something like "X (10), Y(4), Z"."""
  d = defaultdict(int)
  for x in items:
    d[x] += 1
  counts = sorted(d.items(), key=lambda x: -x[1])
  summary = ', '.join([('%s (%d)' % (c[0], c[1]) if c[1] > 1 else c[0]) for c in counts])
  return summary


def RemoveNonAscii(s):
  return "".join(i for i in s if ord(i)<128)


class EntryAccumulator(object):
  """This class assists in grouping items by date."""

  def __init__(self, date_fn):
    """date_fn should map item -> datetime.date"""
    self._date_fn = date_fn
    self._daily_logs = defaultdict(list)

  def add(self, item):
    day = self._date_fn(item)
    assert day
    assert isinstance(day, date)
    self._daily_logs[day].append(item)

  def iteritems(self):
    """Iterate through (day, list of entries) in chronological order."""
    return [(day, self._daily_logs[day])
        for day in sorted(self._daily_logs.keys())]
