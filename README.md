## gpuctypes (a low level GPU library for Python)

Do you wish that there were simple wrappers for GPU libraries in Python? Like not pyopencl, pycuda, and (HIP library someday?) here, but just raw access to the APIs?

That's what gpuctypes does! While high level libraries have their place, the world needs more low level libraries. Like gpuctypes. Welcome home.

### Installation (usage)

```sh
pip install gpuctypes
```

### Usage

```py
import gpuctypes.hip as hip
import gpuctypes.cuda as cuda
import gpuctypes.opencl as opencl
```

### How it works

gpuctypes uses [ctypeslib](https://github.com/trolldbois/ctypeslib) to autogenerate Python files from the headers of the respective libraries.

### Installation (development)

```sh
git clone https://github.com/tinygrad/gpuctypes.git
cd gpuctypes
pip install -e .
```

### Current versions

* ROCm 5.7.1
* CUDA 11.5
* OpenCL (whatever is in Ubuntu 22.04)
