#!/usr/bin/env python3
from setuptools import setup
setup(name='gpuctypes',
      version='0.1.0',
      description='ctypes wrappers for HIP, CUDA, and OpenCL',
      author='George Hotz',
      license='MIT',
      packages = ['gpuctypes'],
      python_requires='>=3.8',
      include_package_data=True)

