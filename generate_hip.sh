#!/bin/bash -e
clang2py /opt/rocm/include/hip/hiprtc.h /opt/rocm/include/hip/hip_runtime_api.h /opt/rocm/include/hip/driver_types.h --clang-args="-D__HIP_PLATFORM_AMD__ -I/opt/rocm/include" -o gpuctypes/hip.py -l /opt/rocm/lib/libhiprtc.so -l /opt/rocm/lib/libamdhip64.so
grep FIXME_STUB gpuctypes/hip.py || true
