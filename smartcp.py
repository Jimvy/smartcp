#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function # for python 2 and stderr
from __version__ import version
import yaml
import itertools
import os
import filecmp
import sys
import getopt

def usage():
  print('''\
Usage: {0} [OPTION]... [FILE]...
Read FILE(s) and do smart copies accordingly

-v               increment verbose level, -vv gives the most verbose output
-h, --help       display this help and exit
    --version    output version information and exit

With no FILE, or when FILE is -, read standard input.

Examples:
{0} config.yml - */config.yml  Do smart copies for config.yml, then standard input, then all config.yml in a subdirectory.
{0}                            Do smart copies for standard output.'''.format(program_name))

def show_version():
  print('''\
{} {}
Copyright (C) 2013 Benoît Legat.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.

Written by Benoît Legat.'''.format(program_name, version))

def parent_dir_exists(path):
  # we take the absolute path to be to transform './...' in '/...'
  folder = os.path.dirname(os.path.abspath(path))
  last = None
  current = folder
  while not os.path.exists(current):
    last = current
    current = os.path.dirname(current)
  if current != folder:
    print_err('There is no {} in {}'.format(os.path.basename(last), current))
    return False
  return True

def up_to_date(input_path, output_path):
  return os.path.exists(output_path) and filecmp.cmp(input_path, output_path)

def get(hash_map, key):
  if key in hash_map:
    return hash_map[key]
  else:
    print_err('Missing key {} in {}', key, hash_map)
    sys.exit(1)

def build_path(path_desc, arguments):
  if 'path_format' in path_desc:
    if 'parameters' in path_desc:
      params = [build_path(param, arguments)
          for param in path_desc['parameters']]
      #pf = unicode(path_desc['path_format'], 'UTF-8')
      #pf = path_desc['path_format'].encode('utf-8')
      pf = path_desc['path_format']
      # Use python3 to avoid problem with accents
      return pf.format(*params)
    else:
      return path_desc['path_format']
  elif 'mapping' in path_desc:
    mapping = path_desc['mapping']
    key = build_path(get(path_desc, 'key'), arguments)
    if key in mapping:
      return mapping[key]
    else:
      return key
  else:
    return arguments[get(path_desc, 'arg')]

def smart_copy(config_file):
  global indent_level
  if config_file:
    stream = open(config_file, 'r')
    print_verbose('Using {}'.format(config_file))
  else:
    stream = sys.stdin
    print_verbose('Using stdin')
  indent_level += 1
  config = yaml.load(stream)
  if not config:
    print_err('Empty config file')
    sys.exit(1)

  for client in get(config, 'clients'):
    print_verbose('Updating {}'.format(get(client, 'name')))
    indent_level += 1
    for args in itertools.product(*get(client, 'arguments')):
      input_path  = os.path.join(get(config, 'input_base'), build_path(get(client, 'input'), args))
      if os.path.exists(input_path):
        output_path = os.path.join(get(config, 'output_base'), build_path(get(client, 'output'), args))
        if parent_dir_exists(output_path):
          if up_to_date(input_path, output_path):
            print_verbose(u'"{}" == "{}"'.format(input_path, output_path), 2) # u is for python 2 only
          else:
            print_verbose(u'"{}" -> "{}"'.format(input_path, output_path)) # u is for python 2 only
        else:
          print_verbose(u'"{}" -> "{}" failed'.format(input_path, output_path)) # u is for python 2 only
          sys.exit(1)
    indent_level -= 1
  indent_level -= 1

program_name = 'smartcp'

def print_err(message):
  print("{0}: {1}".format(program_name, message),
      file = sys.stderr)

verbose = 0
indent_level = 0

def print_verbose(message, level = 1):
  if level <= verbose:
    print("{}{}".format("  " * indent_level, message))

def main():
  global verbose
  try:
    # gnu_getopt allow opts to be after args. For
    # $ smartcp.py config.yml -v
    # gnu_getopt will consider -v as an option and getopt
    # will see it as an arg like config.yml
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hv", ["help", "version"])
  except getopt.GetoptError as err:
    print(str(err))
    usage()
    sys.exit(2)
  for o, a in opts:
    if o == "-v":
      verbose += 1
    elif o in ("-h", "--help"):
      usage()
      sys.exit()
    elif o == "--version":
      show_version()
      sys.exit()
    else:
      assert False, "unhandled option"
  if not args:
    smart_copy(None)
  else:
    for config_file in args:
      if config_file == "-":
        smart_copy(None)
      else:
        if os.path.exists(config_file):
          smart_copy(config_file)
        else:
          print_err("{}: No such file or directory".format(config_file))
          sys.exit(1)

if __name__ == "__main__":
    main()
