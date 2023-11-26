#!/usr/bin/env python3
from setuptools import setup
from pathlib import Path

description = (Path(__file__).resolve().parent / "README.md").read_text()
setup(name='gpuctypes',
      version='0.1.1',
      description='ctypes wrappers for HIP, CUDA, and OpenCL',
      author='George Hotz',
      long_description=description,
      license='MIT',
      packages = ['gpuctypes'],
      python_requires='>=3.8',
      include_package_data=True)
