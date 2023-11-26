import ctypes
import unittest
from helpers import to_char_p_p
import gpuctypes.opencl as cl

def check(status):
  if status != 0: raise RuntimeError(f"OpenCL Error {status}")

class TestOpenCL(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    num_platforms = ctypes.c_uint32()
    platform_array = (cl.cl_platform_id * 1)()
    check(cl.clGetPlatformIDs(1, platform_array, ctypes.byref(num_platforms)))
    assert num_platforms.value > 0, "didn't get platform"

    device_array = (cl.cl_device_id * 1)()
    num_devices = ctypes.c_uint32()
    check(cl.clGetDeviceIDs(platform_array[0], cl.CL_DEVICE_TYPE_DEFAULT, 1, device_array, ctypes.byref(num_devices)))
    assert num_devices.value > 0, "didn't get device"

    status = ctypes.c_int32()
    cls.context = cl.clCreateContext(None, 1, device_array, ctypes.cast(None, cl.clCreateContext.argtypes[3]), None, ctypes.byref(status))
    check(status.value)
    assert cls.context is not None

    cls.queue = cl.clCreateCommandQueue(cls.context, device_array[0], 0, ctypes.byref(status))
    check(status.value)
    assert cls.queue is not None

  def test_malloc(self):
    status = ctypes.c_int32()
    buf = cl.clCreateBuffer(self.context, cl.CL_MEM_READ_ONLY, 4 * 5, None, ctypes.byref(status))
    assert buf is not None

  def test_create_program(self):
    prog = """
    __kernel void vector_add(__global const int *A, __global const int *B, __global int *C) {
      int i = get_global_id(0);
      C[i] = A[i] + B[i];
    }
    """
    num_programs = 1
    sizes = (ctypes.c_size_t * num_programs)()
    sizes[0] = len(prog)
    status = ctypes.c_int32()
    program = cl.clCreateProgramWithSource(self.context, num_programs, to_char_p_p([prog]), sizes, ctypes.byref(status))
    assert program is not None

if __name__ == '__main__':
  unittest.main()
