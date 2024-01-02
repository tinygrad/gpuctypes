#!/bin/bash -e
clang2py /usr/include/cuda.h /usr/include/nvrtc.h -o gpuctypes/cuda.py -l /usr/lib/x86_64-linux-gnu/libcuda.so -l /usr/lib/x86_64-linux-gnu/libnvrtc.so
sed -i "s\import ctypes\import ctypes, ctypes.util, gpuctypes.check_cuda\g" gpuctypes/cuda.py
sed -i "s\ctypes.CDLL('/usr/lib/x86_64-linux-gnu/libcuda.so')\ctypes.CDLL(ctypes.util.find_library('cuda'))\g" gpuctypes/cuda.py
sed -i "s\ctypes.CDLL('/usr/lib/x86_64-linux-gnu/libnvrtc.so')\ctypes.CDLL(ctypes.util.find_library('nvrtc'))\g" gpuctypes/cuda.py
grep FIXME_STUB gpuctypes/cuda.py || true
