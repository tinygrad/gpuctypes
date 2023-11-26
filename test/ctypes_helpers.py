from typing import List
import ctypes

c_char_p_p = ctypes.POINTER(ctypes.POINTER(ctypes.c_char))
def to_char_p_p(options: List[str]) -> c_char_p_p:
  c_options = (ctypes.POINTER(ctypes.c_char) * len(options))()
  c_options[:] = [ctypes.create_string_buffer(o.encode("utf-8")) for o in options]
  return c_options