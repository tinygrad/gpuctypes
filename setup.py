#!/usr/bin/env python3
from setuptools import setup
from pathlib import Path

description = (Path(__file__).resolve().parent / "README.md").read_text()
setup(name='gpuctypes',
      version='0.2.0',
      description='ctypes wrappers for HIP, CUDA, and OpenCL',
      author='George Hotz',
      long_description=description,
      long_description_content_type='text/markdown',
      license='MIT',
      packages = ['gpuctypes'],
      python_requires='>=3.8',
      include_package_data=True)
