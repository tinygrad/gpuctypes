#!/bin/bash
clang2py /usr/include/cuda.h /usr/include/nvrtc.h -o gpuctypes/cuda.py -l /usr/lib/x86_64-linux-gnu/libcuda.so -l /usr/lib/x86_64-linux-gnu/libnvrtc.so
grep FIXME_STUB gpuctypes/cuda.py
