#!/bin/bash -e

out_file=gpuctypes/hip.py
clang2py /opt/rocm/include/hip/hiprtc.h /opt/rocm/include/hip/hip_runtime_api.h /opt/rocm/include/hip/driver_types.h --clang-args="-D__HIP_PLATFORM_AMD__ -I/opt/rocm/include" -o $out_file -l /opt/rocm/lib/libhiprtc.so -l /opt/rocm/lib/libamdhip64.so

# grep FIXME_STUB $out_file || true
# hot patches
get_hiprtc_code="
def get_hiprtc():
    try:
        if 'linux' in sys.platform:
            return ctypes.CDLL(os.path.join('/opt/rocm/lib/libhiprtc.so'))
        elif 'win' in sys.platform:
            hip_path = os.getenv('HIP_PATH', None)
            if not hip_path:
                raise RuntimeError('HIP_PATH is not set')
            return ctypes.CDLL(os.path.join(hip_path, 'bin', 'hiprtc0505.dll'))
        else:
            raise RuntimeError('Only windows and linux are supported')
    except Exception as err:
        raise Exception('Error: {0}'.format(err))
"

get_hip_code="
def get_hip(): 
    try:
        if 'linux' in sys.platform:
            return ctypes.CDLL('/opt/rocm/lib/libamdhip64.so')
        elif 'win' in sys.platform:
            return ctypes.cdll.LoadLibrary('amdhip64')
        else:
            raise RuntimeError('Only windows and linux are supported')
    except Exception as err:
        raise Exception('Error: {0}'.format(err))
"

declare -A patches
patches=(
    ["import ctypes"]="import ctypes, sys, os"
    ["ctypes.CDLL('/opt/rocm/lib/libhiprtc.so')"]="get_hiprtc()"
    ["ctypes.CDLL('/opt/rocm/lib/libamdhip64.so')"]="get_hip()"
)
for key in "${!patches[@]}"; do
    delimiter="@"
    sed -i "s@${key}@${patches[${key}]}@g" $out_file    
done

sed -i '10r /dev/stdin' $out_file <<< "$get_hiprtc_code" 
sed -i '10r /dev/stdin' $out_file <<< "$get_hip_code" 
# sed -i "s\import ctypes\import ctypes, ctypes.util\g" gpuctypes/hip.py
#sed -i "s\ctypes.CDLL('/opt/rocm/lib/libhiprtc.so')\ctypes.CDLL(ctypes.util.find_library('hiprtc'))\g" gpuctypes/hip.py
#sed -i "s\ctypes.CDLL('/opt/rocm/lib/libamdhip64.so')\ctypes.CDLL(ctypes.util.find_library('amdhip64'))\g" gpuctypes/hip.py
python3 -c "import gpuctypes.hip"
