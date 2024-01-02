import ctypes

def is_libnvrtc_available():
  try:
    ctypes.CDLL("libnvrtc.so")
    return True
  except OSError:
    return False

def is_libcuda_available():
  try:
    ctypes.CDLL("libcuda.so")
    return True
  except OSError:
    return False

def is_cuda_available():
  if is_libcuda_available() and is_libnvrtc_available():
    pass
  else:
    raise ImportError("libcuda.so  or libnvrtc.so is not available. Please check your CUDA installation!")

is_cuda_available()

