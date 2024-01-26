clang2py \
    /opt/rocm/include/hsa/hsa.h \
    /opt/rocm/include/hsa/hsa_ext_amd.h \
    /opt/rocm/include/hsa/hsa_ext_finalize.h /opt/rocm/include/hsa/hsa_ext_image.h \
    --clang-args="-I/opt/rocm/include" \
    -o gpuctypes/hsa.py -l /opt/rocm/lib/libhsa-runtime64.so

grep FIXME_STUB gpuctypes/hsa.py || true