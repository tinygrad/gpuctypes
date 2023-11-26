#!/bin/bash
clang2py /usr/include/CL/cl.h -o gpuctypes/opencl.py -l /usr/lib/x86_64-linux-gnu/libOpenCL.so -k cdefstum
grep FIXME_STUB gpuctypes/opencl.py || true
python3 -c "import gpuctypes.opencl"
