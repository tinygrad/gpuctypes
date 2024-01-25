#!/bin/bash -e
clang2py -k acdefstu /opt/rocm/include/amd_comgr/amd_comgr.h /opt/rocm/include/hip/hip_ext.h /opt/rocm/include/hip/hiprtc.h /opt/rocm/include/hip/hip_runtime_api.h /opt/rocm/include/hip/driver_types.h --clang-args="-D__HIP_PLATFORM_AMD__ -I/opt/rocm/include -x c++" -o gpuctypes/hip.py -l /opt/rocm/lib/libhiprtc.so -l /opt/rocm/lib/libamdhip64.so -l /opt/rocm/lib/libamd_comgr.so
echo "hipDeviceProp_t = hipDeviceProp_tR0600" >> gpuctypes/hip.py
echo "hipGetDeviceProperties = hipGetDevicePropertiesR0600" >> gpuctypes/hip.py
grep FIXME_STUB gpuctypes/hip.py || true
# we can trust HIP is always at /opt/rocm/lib
#sed -i "s\import ctypes\import ctypes, ctypes.util\g" gpuctypes/hip.py
#sed -i "s\ctypes.CDLL('/opt/rocm/lib/libhiprtc.so')\ctypes.CDLL(ctypes.util.find_library('hiprtc'))\g" gpuctypes/hip.py
#sed -i "s\ctypes.CDLL('/opt/rocm/lib/libamdhip64.so')\ctypes.CDLL(ctypes.util.find_library('amdhip64'))\g" gpuctypes/hip.py
python3 -c "import gpuctypes.hip"
