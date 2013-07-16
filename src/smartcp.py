#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function # for python 2 and stderr
from .__version__ import version
import yaml
import itertools
import os
import filecmp
import sys
import getopt
import shutil

def usage():
  print('''\
Usage: {0} [OPTION]... [FILE]...
Read FILE(s) and do smart copies accordingly

-s, --set        with the syntax arg=value,
                 set the argument with lablel arg to value instead of
                 iterating over all different possible values
-v               increment verbose level, -vv gives the most verbose output
-h, --help       display this help and exit
    --version    output version information and exit

With no FILE, or when FILE is -, read standard input.

Examples:
{0} config.yml - */config.yml  Do smart copies for config.yml,
                               then standard input,
                               then all config.yml in a subdirectory.
{0}                            Do smart copies for standard output.'''.
format(program_name))

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

def get(hash_map, key, raise_err = True):
  if key in hash_map:
    return hash_map[key]
  else:
    if raise_err:
      print_err('Missing key `{}\' in `{}\''.format(key, hash_map))
      sys.exit(1)
    else:
      return None

def build_path(path_desc, arguments):
  if 'path_format' in path_desc:
    if 'parameters' in path_desc:
      params = [build_path(param, arguments)
          for param in path_desc['parameters']]
      # Use python3 to avoid problem with accents here
      return path_desc['path_format'].format(*params)
    else:
      return path_desc['path_format']
  elif 'mapping' in path_desc:
    mapping = path_desc['mapping']
    key = build_path(get(path_desc, 'key'), arguments)
    if key in mapping:
      return mapping[key]
    else:
      return key
  elif 'arg' in path_desc:
    if arguments:
      label = path_desc['arg']
      # Si le label est 1 et que les keys sont 'a', 'b',
      # la valeur de arguments[1] sera indéterminée,
      # ça dépendra de l'ordre des keys du hash. Évitons cela
      #if type(label) == int
      # Let's check it anyway
      if label in arguments:
        return arguments[label]
      else:
        print_err("unknown label `{}', it should be in {}".
            format(label, arguments.keys()))
        sys.exit(1)
    else:
      print_err("didn't expect `arg' since \
there is no argument for this client")
      sys.exit(1)
  else:
    print_err("{} should have `arg', `mapping' or `parameters'".
        format(path_desc))
    sys.exit(1)

def smart_copy(config_file, arg_set):
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
    # If no arguments, simply means path_format do not contain parameters
    arguments = get(client, 'arguments', False)
    # With &label and *label in YAML,
    # the arrays/hash are shared between all clients in python !!!!
    # It should not cause any problem here
    # (see if I modify config anywhere else)
    if arguments:
      if type(arguments) != dict:
        print_err("arguments which is `{}' should be a hash".format(arguments))
        sys.exit(1)
      for key, value in arguments.items():
        if key in arg_set:
          # Solve the problem with non-string
          # not being compared properly with components of arg_set which are
          # strings
          value = [str(arg) for arg in value]
          setting = arg_set[key]
          if setting in value:
            arguments[key] = [setting]
          else:
            # itertools.product will return an empty iterator
            arguments[key] = []
            # So no need to go further
            break

    # if there is no arguments we just need one loop without any arguments
    # so [None] do the trick
    for args_items in (itertools.product(*arguments.values()) if arguments else [None]):
      if args_items:
        args = dict(zip(arguments.keys(), args_items))
      else:
        args = None
      input_path  = os.path.join(get(config, 'input_base'),
          build_path(get(client, 'input'), args))
      if os.path.exists(input_path):
        output_path = os.path.join(get(config, 'output_base'),
            build_path(get(client, 'output'), args))
        if parent_dir_exists(output_path):
          if up_to_date(input_path, output_path):
            print_verbose(u'`{}\' == `{}\''.format(input_path, output_path), 2)
            # u is only for python 2
          else:
            print_verbose(u'`{}\' -> `{}\''.format(input_path, output_path))
            # u is only for python 2
            shutil.copyfile(input_path, output_path)
        else:
          print_verbose(u'`{}\' /\ `{}\''.format(input_path, output_path))
          # u is only for python 2
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
  arg_set = {}
  global verbose
  try:
    # gnu_getopt allow opts to be after args. For
    # $ smartcp.py config.yml -v
    # gnu_getopt will consider -v as an option and getopt
    # will see it as an arg like config.yml
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hs:v",
        ["help", "set", "version"])
  except getopt.GetoptError as err:
    print_err(str(err))
    usage()
    sys.exit(2)
  for o, a in opts:
    if o == "-v":
      verbose += 1
    elif o in ("-h", "--help"):
      usage()
      sys.exit()
    elif o in ("-s", "--set"):
      try:
        (arg, value) = a.split("=")
      except ValueError as e:
        print_err("{} should have the format `arg=value'".format(a))
        sys.exit(2)
      arg_set[arg] = value
    elif o == "--version":
      show_version()
      sys.exit()
    else:
      assert False, "unhandled option"
  if not args:
    smart_copy(None, arg_set)
  else:
    for config_file in args:
      if config_file == "-":
        smart_copy(None, arg_set)
      else:
        if os.path.exists(config_file):
          smart_copy(config_file, arg_set)
        else:
          print_err("{}: No such file or directory".format(config_file))
          sys.exit(1)

if __name__ == "__main__":
    main()
