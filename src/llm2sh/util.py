#!/usr/bin/env python3

import fcntl
import os
import sys
from typing import List

def instance_already_running(label="default"):
  lock_file_pointer = os.open(f"/tmp/instance_{label}.lock", os.O_WRONLY | os.O_CREAT)

  try:
    fcntl.lockf(lock_file_pointer, fcntl.LOCK_EX | fcntl.LOCK_NB)
    already_running = False
  except IOError:
    already_running = True

  return already_running


def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)


def ethrow(*args, **kwargs):
  eprint(*args, **kwargs)
  raise Exception(*args)


def remove_if_exists(path, *args, **kwargs):
  if os.path.exists(path):
    os.remove(path, *args, **kwargs)


def flatten(xs):
    result = []
    if isinstance(xs, (list, tuple)):
        for x in xs:
            result.extend(flatten(x))
    else:
        result.append(xs)
    return result


def quote(x: str) -> str:
  return f'"{x}"'


def unquote(x: str, quote='"') -> str:
  if x.startswith(quote) and x.endswith(quote):
    return x[1:-1]
  return x


def unquote_all(x: str, quotes: List[str]) -> str:
  for quote in quotes:
    x = unquote(x, quote)
  return x


def nullif(value: str, null_value: str) -> str:
  return None if value == null_value else value
