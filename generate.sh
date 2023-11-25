#!/bin/bash
clang2py /opt/rocm/include/hip/hiprtc.h /opt/rocm/include/hip/hip_runtime_api.h /opt/rocm/include/hip/driver_types.h --clang-args="-D__HIP_PLATFORM_AMD__ -I/opt/rocm/include" -o gpuctypes/hip.py -l /opt/rocm/lib/libhiprtc.so -l /opt/rocm/lib/libamdhip64.so
clang2py /usr/include/cuda.h /usr/include/nvrtc.h -o gpuctypes/cuda.py -l /usr/lib/x86_64-linux-gnu/libcuda.so -l /usr/lib/x86_64-linux-gnu/libnvrtc.so
grep FIXME_STUB gpuctypes/*
