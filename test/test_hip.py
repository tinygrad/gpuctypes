import unittest
import ctypes
import gpuctypes.hip as hip
from helpers import to_char_p_p, CI, expectedFailureIf, get_bytes

def check(status):
  if status != 0: raise RuntimeError(f"HIP Error {status}, {ctypes.string_at(hip.hipGetErrorString(status)).decode()}")

def _test_compile(prg):
  prog = hip.hiprtcProgram()
  check(hip.hiprtcCreateProgram(ctypes.pointer(prog), prg.encode(), "<null>".encode(), 0, None, None))
  options = ["--offload-arch=gfx1100"]
  status = hip.hiprtcCompileProgram(prog, len(options), to_char_p_p(options))
  if status != 0:
    log = get_bytes(prog, hip.hiprtcGetProgramLogSize, hip.hiprtcGetProgramLog, check)
    raise RuntimeError(f"HIP compile failed: {log}")
  return get_bytes(prog, hip.hiprtcGetCodeSize, hip.hiprtcGetCode, check)

class TestHIP(unittest.TestCase):
  def test_has_methods(self):
    assert hip.hipMalloc is not None
    assert hip.hiprtcCompileProgram is not None
    assert hip.hipGetDeviceProperties is not None

  def test_compile_fail(self):
    with self.assertRaises(RuntimeError):
      _test_compile("void test() { {")

  def test_compile(self):
    prg = _test_compile("int test() { return 42; }")
    assert len(prg) > 10

class TestHIPDevice(unittest.TestCase):
  @expectedFailureIf(CI)
  def test_malloc(self):
    ptr = ctypes.c_void_p()
    check(hip.hipMalloc(ctypes.byref(ptr), 100))
    assert ptr.value != 0
    check(hip.hipFree(ptr))

  @expectedFailureIf(CI)
  def test_get_device_properties(self) -> hip.hipDeviceProp_t:
    device_properties = hip.hipDeviceProp_t()
    check(hip.hipGetDeviceProperties(device_properties, 0))
    print(device_properties.gcnArchName)
    return device_properties

if __name__ == '__main__':
  unittest.main()