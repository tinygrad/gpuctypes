import ctypes
import unittest
import gpuctypes.cuda as cuda
from helpers import to_char_p_p, CI, get_bytes

def check(status):
  if status != 0:
    error = ctypes.POINTER(ctypes.c_char)()
    check(cuda.cuGetErrorString(status, ctypes.byref(error)))
    raise RuntimeError(f"CUDA Error {status}, {ctypes.string_at(error).decode()}")

def _test_compile(prg):
  prog = cuda.nvrtcProgram()
  check(cuda.nvrtcCreateProgram(ctypes.pointer(prog), prg.encode(), "<null>".encode(), 0, None, None))
  options = ["--gpu-architecture=sm_35"]
  status = cuda.nvrtcCompileProgram(prog, len(options), to_char_p_p(options))
  if status != 0:
    log = get_bytes(prog, cuda.nvrtcGetProgramLogSize, cuda.nvrtcGetProgramLog, check)
    raise RuntimeError(f"CUDA compile failed: {log}")
  return get_bytes(prog, cuda.nvrtcGetCUBINSize, cuda.nvrtcGetCUBIN, check)

class TestCUDA(unittest.TestCase):
  def test_has_methods(self):
    assert cuda.cuInit is not None
    assert cuda.cuDeviceGetCount is not None
    assert cuda.cuMemAlloc_v2 is not None

  def test_compile_fail(self):
    with self.assertRaises(RuntimeError):
      _test_compile("__device__ void test() { {")

  def test_compile(self):
    prg = _test_compile("__device__ int test() { return 42; }")
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