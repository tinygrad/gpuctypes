#!/usr/bin/env python3
from setuptools import setup

description = """Do you wish that there were simple wrappers for GPU libraries in Python?

Like not pyopencl, pycuda, and <HIP library someday?> here, but just raw access to the APIs?

That's what gpuctypes does! While high level libraries have their place, the world needs more low level libraries.

Like gpuctypes. Welcome home.
"""

setup(name='gpuctypes',
      version='0.1.0',
      description='ctypes wrappers for HIP, CUDA, and OpenCL',
      author='George Hotz',
      long_description=description,
      license='MIT',
      packages = ['gpuctypes'],
      python_requires='>=3.8',
      include_package_data=True)

