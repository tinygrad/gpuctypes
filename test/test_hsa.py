import unittest
import ctypes
import gpuctypes.hsa as hsa
from helpers import CI, expectedFailureIf

def check(status):
  if status != 0: raise RuntimeError(f"HSA Error {status}")

def find_agent(typ, device_id):
  @ctypes.CFUNCTYPE(hsa.hsa_status_t, hsa.hsa_agent_t, ctypes.c_void_p)
  def __filter_amdgpu_agent(agent, data):
    status = hsa.hsa_agent_get_info(agent, hsa.HSA_AGENT_INFO_DEVICE, ctypes.byref(device_type := hsa.hsa_device_type_t()))
    if status == 0 and device_type.value == typ:
      ret = ctypes.cast(data, ctypes.POINTER(hsa.hsa_agent_t))
      print(ret[0].handle)
      if ret[0].handle < device_id:
        ret[0].handle = ret[0].handle + 1
        return hsa.HSA_STATUS_SUCCESS

      ret = ctypes.cast(data, ctypes.POINTER(hsa.hsa_agent_t))
      ret[0] = agent
      return hsa.HSA_STATUS_INFO_BREAK
    return hsa.HSA_STATUS_SUCCESS

  agent = hsa.hsa_agent_t()
  agent.handle = 0
  hsa.hsa_iterate_agents(__filter_amdgpu_agent, ctypes.byref(agent))
  return agent

def get_amd_memory_pool(agent, segtyp=-1, flags=-1, location=-1):
  @ctypes.CFUNCTYPE(hsa.hsa_status_t, hsa.hsa_amd_memory_pool_t, ctypes.c_void_p)
  def __filter_amd_memory_pools(mem_pool, data):
    if segtyp != -1:
      check(hsa.hsa_amd_memory_pool_get_info(mem_pool, hsa.HSA_AMD_MEMORY_POOL_INFO_SEGMENT, ctypes.byref(segment := hsa.hsa_amd_segment_t())))
      if segment.value != segtyp: return hsa.HSA_STATUS_SUCCESS

    if flags != -1:
      check(hsa.hsa_amd_memory_pool_get_info(mem_pool, hsa.HSA_AMD_MEMORY_POOL_INFO_GLOBAL_FLAGS, ctypes.byref(fgs := hsa.hsa_amd_memory_pool_global_flag_t())))
      if fgs.value != flags: return hsa.HSA_STATUS_SUCCESS

    if location != -1:
      check(hsa.hsa_amd_memory_pool_get_info(mem_pool, hsa.HSA_AMD_MEMORY_POOL_INFO_LOCATION, ctypes.byref(loc := hsa.hsa_amd_memory_pool_location_t())))
      if loc.value != location: return hsa.HSA_STATUS_SUCCESS

    ret = ctypes.cast(data, ctypes.POINTER(hsa.hsa_amd_memory_pool_t))
    ret[0] = mem_pool
    return hsa.HSA_STATUS_INFO_BREAK

  region = hsa.hsa_amd_memory_pool_t()
  region.handle = 0
  hsa.hsa_amd_agent_iterate_memory_pools(agent, __filter_amd_memory_pools, ctypes.byref(region))
  return region

class TestHSA(unittest.TestCase):
  def test_hsa_methods(self):
    assert hsa.hsa_memory_allocate is not None
    assert hsa.hsa_agent_get_info is not None
    assert hsa.hsa_amd_memory_pool_allocate is not None

class TestHSADevice(unittest.TestCase):
  def setUp(self):
    if not CI: check(hsa.hsa_init())
  def tearDown(self):
    if not CI: check(hsa.hsa_shut_down())

  @expectedFailureIf(CI)
  def test_amd_malloc(self):
    agent = find_agent(hsa.HSA_DEVICE_TYPE_GPU, device_id=0)
    gpu_memory_pool = get_amd_memory_pool(agent, segtyp=hsa.HSA_AMD_SEGMENT_GLOBAL, location=hsa.HSA_AMD_MEMORY_POOL_LOCATION_GPU)

    sz = 2 << 20
    check(hsa.hsa_amd_memory_pool_allocate(gpu_memory_pool, sz, 0, ctypes.byref(buf0 := ctypes.c_void_p())))
    assert buf0 != 0
    check(hsa.hsa_amd_memory_pool_free(buf0))

  @expectedFailureIf(CI)
  def test_get_device_properties(self):
    agent = find_agent(hsa.HSA_DEVICE_TYPE_GPU, device_id=0)
    assert agent.handle != 0, "no agent found"

    check(hsa.hsa_agent_get_info(agent, hsa.HSA_AGENT_INFO_NAME, ctypes.byref(buf := ctypes.create_string_buffer(256))))
    print(ctypes.string_at(buf).decode())

if __name__ == '__main__':
  unittest.main()