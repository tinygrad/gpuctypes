import ctypes
import unittest
# TODO: the import has to not fail if some of the methods are missing
import gpuctypes.opencl as cl

def check(status):
  if status != 0: raise RuntimeError(f"OpenCL Error {status}")

# TODO: this should be in the header
CL_DEVICE_TYPE_DEFAULT = 1

class TestOpenCL(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    num_platforms = ctypes.c_uint32()
    platform_array = (cl.cl_platform_id * 1)()
    check(cl.clGetPlatformIDs(1, platform_array, ctypes.byref(num_platforms)))
    assert num_platforms.value > 0, "didn't get platform"

    device_array = (cl.cl_device_id * 1)()
    num_devices = ctypes.c_uint32()
    check(cl.clGetDeviceIDs(platform_array[0], CL_DEVICE_TYPE_DEFAULT, 1, device_array, ctypes.byref(num_devices)))
    assert num_devices.value > 0, "didn't get device"

    status = ctypes.c_int32()
    context = cl.clCreateContext(None, 1, device_array[0], ctypes.cast(None, cl.clCreateContext.argtypes[3]), None, ctypes.byref(status))
    check(status.value)
    assert context is not None

  def test_malloc(self):
    #cl.clCreateBuffer()
    pass

if __name__ == '__main__':
  unittest.main()
