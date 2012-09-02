"""Tools for building a personal archive in a canonical format."""

from datetime import date
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
    json.dump(data, file(filename, 'w'))


def SummarizeText(txt):
  """Cut text off at 160 characters and add '...' if necessary."""
  txt = re.sub(r'\n+', ' ', txt)
  if len(txt) < 160: return txt
  return txt[0:157] + '...'


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
