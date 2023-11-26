import unittest
import ctypes
import gpuctypes.hip as hip
from helpers import CI, expectedFailureIf, cuda_compile

def check(status):
  if status != 0: raise RuntimeError(f"HIP Error {status}, {ctypes.string_at(hip.hipGetErrorString(status)).decode()}")

class HIPCompile:
  new = hip.hiprtcProgram
  create = hip.hiprtcCreateProgram
  compile = hip.hiprtcCompileProgram
  getLogSize = hip.hiprtcGetProgramLogSize
  getLog = hip.hiprtcGetProgramLog
  getCodeSize = hip.hiprtcGetCodeSize
  getCode = hip.hiprtcGetCode

class TestHIP(unittest.TestCase):
  def test_has_methods(self):
    assert hip.hipMalloc is not None
    assert hip.hiprtcCompileProgram is not None
    assert hip.hipGetDeviceProperties is not None

  def test_compile_fail(self):
    with self.assertRaises(RuntimeError):
      cuda_compile("void test() { {", ["--offload-arch=gfx1100"], HIPCompile, check)

  def test_compile(self):
    prg = cuda_compile("int test() { return 42; }", ["--offload-arch=gfx1100"], HIPCompile, check)
    assert len(prg) > 10

class TestHIPDevice(unittest.TestCase):
  @expectedFailureIf(CI)
  def test_malloc(self):
    ptr = ctypes.c_void_p()
    check(hip.hipMalloc(ctypes.byref(ptr), 100))
    assert ptr.value != 0
    check(hip.hipFree(ptr))

  @expectedFailureIf(CI)
  def test_device_count(self):
    check(hip.hipGetDeviceCount(ctypes.byref(count := ctypes.c_int())))
    print(f"got {count.value} devices")
    assert count.value > 0

  @expectedFailureIf(CI)
  def test_get_device_properties(self) -> hip.hipDeviceProp_t:
    device_properties = hip.hipDeviceProp_t()
    check(hip.hipGetDeviceProperties(device_properties, 0))
    print(device_properties.gcnArchName)
    return device_properties

if __name__ == '__main__':
  unittest.main()