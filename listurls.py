import regex
import re
import os
import argparse
import sys

import urllib
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone

from bs4 import BeautifulSoup
import urllib.request

#
# MIT License
#
# https://opensource.org/licenses/MIT
#
# Copyright 2020 Rene Sugar
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#
# Description:
#
# This program lists URLs in a file.
#

def remove_line_breakers(s):
  if s is None:
    return s
  t = s.replace('\n', ' ')
  t = t.replace('\r', ' ')
  t = t.replace('\v', ' ')
  t = t.replace('\x0b', ' ')
  t = t.replace('\f', ' ')
  t = t.replace('\x0c', ' ')
  t = t.replace('\x1c', ' ')
  t = t.replace('\x1d', ' ')
  t = t.replace('\x1e', ' ')
  t = t.replace('\x85', ' ')
  t = t.replace('\u2028', ' ')
  t = t.replace('\u2029', ' ')
  return t

def checkExtension(file, exts):
  name, extension = os.path.splitext(file)
  extension = extension.lstrip(".")
  processFile = 0
  if len(extension) == 0:
    processFile = 0
  elif len(exts) == 0:
    processFile = 1
  elif extension in exts:
    processFile = 1
  else:
    processFile = 0
  return processFile

def checkExclusion(dir, rootPath, excludePaths):
  processDir = 0
  if (dir[0:1] == "."):
    processDir = 0
  elif os.path.join(rootPath,dir) in excludePaths:
    processDir = 0
  else:
    processDir = 1
  return processDir

def filelist(dir, excludePaths, exts):
  allfiles = []
  for path, subdirs, files in os.walk(dir):
    files = [os.path.join(path,x) for x in files if checkExtension(x, exts)]
    # "[:]" alters the list of subdirectories walked by os.walk
    # https://stackoverflow.com/questions/10620737/efficiently-removing-subdirectories-in-dirnames-from-os-walk
    subdirs[:] = [os.path.join(path,x) for x in subdirs if checkExclusion(x, path, excludePaths)]
    allfiles.extend(files)
    for x in subdirs:
      allfiles.extend(filelist(x, excludePaths, exts))
  return allfiles

def main():
  parser = argparse.ArgumentParser(description="listurls")
  parser.add_argument("--path", help="Base path of the project to be scanned", default=".")
  parser.add_argument("--root", help="Root path of the project to be scanned", default="/")
  parser.add_argument("--prefix", help="Replace root path with this prefix", default="/")
  parser.add_argument("--extensions", help="File extensions that are processed", default=".html.htm.c.h.hpp.hxx.cc.cpp.c++.cxx.java.cs.txt")
  parser.add_argument("--exclude", nargs='*', help="Paths of folders to exclude", default=[])
  parser.add_argument("--output", help="Path to output file", default="./output.txt")
  parser.add_argument('--backup', help="Bookmark backup format", dest='backup', action='store_true', default=False)

  args = vars(parser.parse_args())

  outputFile = os.path.abspath(os.path.expanduser(args['output']))

  if os.path.isfile(outputFile):
    # Don't overwrite existing files in case the output file has the same name
    # as a project file and the output path is in a project directory.
    print("Error: output file '" + outputFile + "' already exists.")
    sys.exit(1)

  basePath = os.path.abspath(os.path.expanduser(args['path']))

  rootPath = args['root']

  rootPrefix = args['prefix']

  fileExtensions = args['extensions'].lstrip(".").split(".")

  excludePaths = args['exclude']

  backupFormat = args['backup']

  # Remove trailing path separator from each exclude path
  excludePaths[:] = [x.rstrip(os.sep) for x in excludePaths]

  files = filelist(basePath, excludePaths, fileExtensions)

  titles = {}

  with open(outputFile, "w") as a:
    # Read each file
    for file in files:
      file_canonical = file.replace(rootPath, rootPrefix, 1)

      print("processing %s..." % (str(file_canonical),))

      with open(file, 'r') as f:
        lines = f.readlines()
        data=''.join(lines)

        # Get URLs

        pattern = regex.compile(r'(https?|ftp):\/\/[^\s]+', regex.DOTALL)

        for m in pattern.finditer(data):
          if m.end() > m.start():
            url = m.group(0)
            
            if url.endswith('/'):
              url = url[:-1]

            urlTuple = urllib.parse.urlsplit(url)

            url = urllib.parse.urlunsplit(urlTuple)

            queryDict = urllib.parse.parse_qs(urlTuple[3])

            netloc = urlTuple[1]
            if 'q' in queryDict:
              query = ''.join(queryDict['q'])
            else:
              query = ''

            title = url
            if netloc == "accounts.google.com":
              title = ''
              url = ''
            elif netloc == "www.google.com":
              if len(query) > 0:
                title = query + ' - Google Search'
              else:
                title = 'Google Search'
            else:
              try:
                if url in titles:
                  # cached title
                  title = titles[url]
                else:
                  # request title
                  with urllib.request.urlopen(url) as response:
                    html = response.read()
                    soup = BeautifulSoup(html, features="html.parser")
                    title = soup.title.string
                    # cache title
                    if title is None:
                      title = url
                    else:
                      titles[url] = title
              except:
                title = url

            title = remove_line_breakers(title).strip()

            if len(url) > 0:
              if backupFormat:
                a.write(title)
                a.write(str(os.linesep))
                a.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
                a.write(str(os.linesep))
                a.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
                a.write(str(os.linesep))
                a.write(url)
                a.write(str(os.linesep))
              else:
                a.write(url)
                a.write(str(os.linesep))

if __name__ == "__main__":
  main()

