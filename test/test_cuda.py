import ctypes
import unittest
import gpuctypes.cuda as cuda
from helpers import CI, cuda_compile

def check(status):
  if status != 0:
    error = ctypes.POINTER(ctypes.c_char)()
    check(cuda.cuGetErrorString(status, ctypes.byref(error)))
    raise RuntimeError(f"CUDA Error {status}, {ctypes.string_at(error).decode()}")

class CUDACompile:
  new = cuda.nvrtcProgram
  create = cuda.nvrtcCreateProgram
  compile = cuda.nvrtcCompileProgram
  getLogSize = cuda.nvrtcGetProgramLogSize
  getLog = cuda.nvrtcGetProgramLog
  getCodeSize = cuda.nvrtcGetCUBINSize
  getCode = cuda.nvrtcGetCUBIN

class TestCUDA(unittest.TestCase):
  def test_has_methods(self):
    assert cuda.cuInit is not None
    assert cuda.cuDeviceGetCount is not None
    assert cuda.cuMemAlloc_v2 is not None

  def test_compile_fail(self):
    with self.assertRaises(RuntimeError):
      cuda_compile("__device__ void test() { {", ["--gpu-architecture=sm_60"], CUDACompile, check)

  def test_compile(self):
    prg = cuda_compile("__device__ int test() { return 42; }", ["--gpu-architecture=sm_60"], CUDACompile, check)
    assert len(prg) > 10

@unittest.skipIf(CI, "cuda doesn't work in CI")
class TestCUDADevice(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    check(cuda.cuInit(0))
    cls.device = cuda.CUdevice()
    check(cuda.cuDeviceGet(ctypes.byref(cls.device), 0))
    cls.context = cuda.CUcontext()
    check(cuda.cuCtxCreate_v2(ctypes.byref(cls.context), 0, cls.device))

  # NOTE: this requires cuInit, so it doesn't run in CI
  def test_device_count(self):
    check(cuda.cuDeviceGetCount(ctypes.byref(count := ctypes.c_int())))
    print(f"got {count.value} devices")
    assert count.value > 0

  def test_malloc(self):
    check(cuda.cuMemAlloc_v2(ctypes.byref(ptr := ctypes.c_ulong()), 16))
    assert ptr.value != 0
    print(ptr.value)

if __name__ == '__main__':
  unittest.main()