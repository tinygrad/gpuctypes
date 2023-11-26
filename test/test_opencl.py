from typing import Optional
import ctypes
import unittest
from helpers import to_char_p_p
import gpuctypes.opencl as cl

def check(status, info:Optional[str]=None):
  if status != 0: raise RuntimeError(f"OpenCL Error {status}" + (("\n\n"+info) if info else ""))

def cl_compile(context, device_array, prog):
  num_programs = 1
  sizes = (ctypes.c_size_t * num_programs)()
  sizes[0] = len(prog)
  status = ctypes.c_int32()
  program = cl.clCreateProgramWithSource(context, num_programs, to_char_p_p([prog]), sizes, ctypes.byref(status))
  assert program is not None
  status = cl.clCompileProgram(program, len(device_array), device_array, None, 0, None, None, ctypes.cast(None, cl.clCompileProgram.argtypes[7]), None)
  if status != 0:
    cl.clGetProgramBuildInfo(program, device_array[0], cl.CL_PROGRAM_BUILD_LOG, 0, None, ctypes.byref(log_size := ctypes.c_size_t()))
    cl.clGetProgramBuildInfo(program, device_array[0], cl.CL_PROGRAM_BUILD_LOG, log_size.value, mstr := ctypes.create_string_buffer(log_size.value), None)
    check(status, ctypes.string_at(mstr, size=log_size.value).decode())
  return program

class TestOpenCL(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    num_platforms = ctypes.c_uint32()
    platform_array = (cl.cl_platform_id * 1)()
    check(cl.clGetPlatformIDs(1, platform_array, ctypes.byref(num_platforms)))
    assert num_platforms.value > 0, "didn't get platform"

    cls.device_array = (cl.cl_device_id * 1)()
    num_devices = ctypes.c_uint32()
    check(cl.clGetDeviceIDs(platform_array[0], cl.CL_DEVICE_TYPE_DEFAULT, 1, cls.device_array, ctypes.byref(num_devices)))
    assert num_devices.value > 0, "didn't get device"

    status = ctypes.c_int32()
    cls.context = cl.clCreateContext(None, 1, cls.device_array, ctypes.cast(None, cl.clCreateContext.argtypes[3]), None, ctypes.byref(status))
    check(status.value)
    assert cls.context is not None

    cls.queue = cl.clCreateCommandQueue(cls.context, cls.device_array[0], 0, ctypes.byref(status))
    check(status.value)
    assert cls.queue is not None

  def test_malloc(self):
    status = ctypes.c_int32()
    buf = cl.clCreateBuffer(self.context, cl.CL_MEM_READ_ONLY, 4 * 5, None, ctypes.byref(status))
    assert buf is not None

  def test_bad_program(self):
    with self.assertRaises(RuntimeError):
      cl_compile(self.context, self.device_array, "__kernel void vector_add() { x }")

  def test_create_program(self):
    program = cl_compile(self.context, self.device_array, """
    __kernel void vector_add(__global int *A, __global const int *B, __global const int *C) {
      int i = get_global_id(0);
      A[i] = B[i] + C[i];
    }""")


if __name__ == '__main__':
  unittest.main()
