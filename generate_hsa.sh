clang2py \
    /opt/rocm/include/hsa/hsa.h \
    /opt/rocm/include/hsa/hsa_ext_amd.h \
    /opt/rocm/include/hsa/hsa_ext_finalize.h /opt/rocm/include/hsa/hsa_ext_image.h \
    --clang-args="-I/opt/rocm/include" \
    -o gpuctypes/hsa.py -l /opt/rocm/lib/libhsa-runtime64.so

python3 -c $'import re

with open("gpuctypes/hsa.py", "r") as file:
    txt = file.read()

def fix_anons(match):
    filename = match.group(1)
    line_number = match.group(2)
    return f"_{filename}_h_{line_number}"

# Need to patch all unnamed and anon structs
pattern = r"\s+\\(unnamed at\s+.*/(.*?).h:(\\d+):\\d+\\)"
txt = re.sub(pattern, fix_anons, txt)

pattern = r"\s+\\(anonymous at\s+.*/(.*?).h:(\\d+):\\d+\\)"
txt = re.sub(pattern, fix_anons, txt)

# Put our lib insted of stubs
txt = txt.replace("_libraries[\'FIXME_STUB\'] = FunctionFactoryStub()", "_libraries[\'libhsa\'] = ctypes.CDLL(\'/opt/rocm/lib/libhsa-runtime64.so\')")
txt = txt.replace("_libraries[\'FIXME_STUB\'].", "_libraries[\'libhsa\'].")

with open("gpuctypes/hsa.py", "w") as file:
    file.write(txt)
'

grep FIXME_STUB gpuctypes/hsa.py || true