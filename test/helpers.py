from typing import List
import unittest, os, ctypes

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
  check(get_sz(arg, ctypes.byref((sz := ctypes.c_size_t()))))
  check(get_str(arg, (mstr := ctypes.create_string_buffer(sz.value))))
  return ctypes.string_at(mstr, size=sz.value)

def compile(prg, options, f, check):
  check(f.create(ctypes.pointer((prog := f.new())), prg.encode(), "<null>".encode(), 0, None, None))
  status = f.compile(prog, len(options), to_char_p_p(options))
  if status != 0: raise RuntimeError(f"compile failed: {get_bytes(prog, f.getLogSize, f.getLog, check)}")
  return get_bytes(prog, f.getCodeSize, f.getCode, check)
