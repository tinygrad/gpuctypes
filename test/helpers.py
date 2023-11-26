from typing import List
import unittest, os, ctypes

c_char_p_p = ctypes.POINTER(ctypes.POINTER(ctypes.c_char))
def to_char_p_p(options: List[str]):
  c_options = (ctypes.POINTER(ctypes.c_char) * len(options))()
  c_options[:] = [ctypes.cast(ctypes.create_string_buffer(o.encode("utf-8")), ctypes.POINTER(ctypes.c_char)) for o in options]
  return c_options

def expectedFailureIf(condition):
  def wrapper(func):
    if condition: return unittest.expectedFailure(func)
    else: return func
  return wrapper
CI = os.getenv("CI", "") != ""

def get_bytes(arg, get_sz, get_str, check) -> bytes:
  sz = ctypes.c_size_t()
  check(get_sz(arg, ctypes.byref(sz)))
  mstr = ctypes.create_string_buffer(sz.value)
  check(get_str(arg, mstr))
  return ctypes.string_at(mstr, size=sz.value)
