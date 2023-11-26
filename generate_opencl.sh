#!/bin/bash
clang2py /usr/include/CL/cl.h -o gpuctypes/opencl.py -l /usr/lib/x86_64-linux-gnu/libOpenCL.so -k cdefstum
grep FIXME_STUB gpuctypes/opencl.py || true
# hot patches
sed -i "s\import ctypes\import ctypes, ctypes.util\g" gpuctypes/opencl.py
sed -i "s\ctypes.CDLL('/usr/lib/x86_64-linux-gnu/libOpenCL.so')\ctypes.CDLL(ctypes.util.find_library('OpenCL'))\g" gpuctypes/opencl.py
python3 -c "import gpuctypes.opencl"
