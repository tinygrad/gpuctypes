#!/bin/bash
clang2py /usr/include/CL/cl.h -o gpuctypes/opencl.py -l /usr/lib/x86_64-linux-gnu/libOpenCL.so
grep FIXME_STUB gpuctypes/opencl.py
