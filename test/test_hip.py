from typing import List
import unittest
import ctypes
import gpuctypes.hip as hip

def check(status):
  #{ctypes.string_at(hip.hipGetErrorString(hip.hipGetLastError()))}
  if status != 0: raise RuntimeError(f"HIP Error {status}")

# put in ctypes_helpers.py in tinygrad
c_char_p_p = ctypes.POINTER(ctypes.POINTER(ctypes.c_char))
def to_char_p_p(options: List[str]) -> c_char_p_p:
  c_options = (ctypes.POINTER(ctypes.c_char) * len(options))()
  c_options[:] = [ctypes.create_string_buffer(o.encode("utf-8")) for o in options]
  return c_options

class TestHIP(unittest.TestCase):
  def test_malloc(self):
    ptr = ctypes.c_void_p()
    check(hip.hipMalloc(ctypes.byref(ptr), 100))
    assert ptr.value != 0
    check(hip.hipFree(ptr))

  def test_get_device_properties(self) -> hip.hipDeviceProp_t:
    device_properties = hip.hipDeviceProp_t()
    check(hip.hipGetDeviceProperties(device_properties, 0))
    print(device_properties.gcnArchName)
    return device_properties

  def test_compile(self):
    hip.hipSetDevice(0)
    prg = "void test() { }"
    prog = hip.hiprtcProgram()
    check(hip.hiprtcCreateProgram(ctypes.pointer(prog), prg.encode(), "<null>".encode(), 0, None, None))
    # NOTE: this is segfaulting with options
    #options = [f'--offload-arch={self.test_get_device_properties().gcnArchName}']
    options = []
    status = hip.hiprtcCompileProgram(prog, len(options), to_char_p_p(options))
    if status != 0:
      log_size = ctypes.c_size_t()
      check(hip.hiprtcGetProgramLogSize(prog, ctypes.byref(log_size)))
      logstr = ctypes.create_string_buffer(log_size.value)
      check(hip.hiprtcGetProgramLog(prog, logstr))
      print(ctypes.string_at(logstr))
    code_size = ctypes.c_size_t()
    check(hip.hiprtcGetCodeSize(prog, ctypes.byref(code_size)))
    assert code_size.value > 10
    #c_options = (ctypes.POINTER(ctypes.c_char) * 2)()
    #c_options[0] = ctypes.create_string_buffer(f'--offload-arch={self.test_get_device_properties().gcnArchName}'.encode())
    #c_options[1] = None
    #hip.hiprtcCompileProgram(prog, 1, ctypes.cast(c_options, ctypes.POINTER(ctypes.POINTER(ctypes.c_char))))
  #return hip.hiprtcGetCode(prog)

if __name__ == '__main__':
  unittest.main()