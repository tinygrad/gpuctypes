import ctypes
import unittest
import gpuctypes.cuda as cuda

def check(status):
  if status != 0:
    error = ctypes.POINTER(ctypes.c_char)()
    check(cuda.cuGetErrorString(status, ctypes.byref(error)))
    raise RuntimeError(f"CUDA Error {status}, {ctypes.string_at(error).decode()}")

class TestCUDA(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    check(cuda.cuInit(0))
    cls.device = cuda.CUdevice()
    check(cuda.cuDeviceGet(ctypes.byref(cls.device), 0))
    cls.context = cuda.CUcontext()
    check(cuda.cuCtxCreate_v2(ctypes.byref(cls.context), 0, cls.device))

  def test_device_count(self):
    count = ctypes.c_int()
    check(cuda.cuDeviceGetCount(ctypes.byref(count)))
    print(f"got {count.value} devices")
    assert count.value > 0

  def test_malloc(self):
    ptr = ctypes.c_ulong()
    check(cuda.cuMemAlloc_v2(ctypes.byref(ptr), 16))
    assert ptr.value != 0
    print(ptr.value)

if __name__ == '__main__':
  unittest.main()