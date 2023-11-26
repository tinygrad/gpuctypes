# -*- coding: utf-8 -*-
#
# TARGET arch is: ['-D__HIP_PLATFORM_AMD__', '-I/opt/rocm/include']
# WORD_SIZE is: 8
# POINTER_SIZE is: 8
# LONGDOUBLE_SIZE is: 16
#
import ctypes, sys

class AsDictMixin:
    @classmethod
    def as_dict(cls, self):
        result = {}
        if not isinstance(self, AsDictMixin):
            # not a structure, assume it's already a python object
            return self
        if not hasattr(cls, "_fields_"):
            return result
        # sys.version_info >= (3, 5)
        # for (field, *_) in cls._fields_:  # noqa
        for field_tuple in cls._fields_:  # noqa
            field = field_tuple[0]
            if field.startswith('PADDING_'):
                continue
            value = getattr(self, field)
            type_ = type(value)
            if hasattr(value, "_length_") and hasattr(value, "_type_"):
                # array
                if not hasattr(type_, "as_dict"):
                    value = [v for v in value]
                else:
                    type_ = type_._type_
                    value = [type_.as_dict(v) for v in value]
            elif hasattr(value, "contents") and hasattr(value, "_type_"):
                # pointer
                try:
                    if not hasattr(type_, "as_dict"):
                        value = value.contents
                    else:
                        type_ = type_._type_
                        value = type_.as_dict(value.contents)
                except ValueError:
                    # nullptr
                    value = None
            elif isinstance(value, AsDictMixin):
                # other structure
                value = type_.as_dict(value)
            result[field] = value
        return result


class Structure(ctypes.Structure, AsDictMixin):

    def __init__(self, *args, **kwds):
        # We don't want to use positional arguments fill PADDING_* fields

        args = dict(zip(self.__class__._field_names_(), args))
        args.update(kwds)
        super(Structure, self).__init__(**args)

    @classmethod
    def _field_names_(cls):
        if hasattr(cls, '_fields_'):
            return (f[0] for f in cls._fields_ if not f[0].startswith('PADDING'))
        else:
            return ()

    @classmethod
    def get_type(cls, field):
        for f in cls._fields_:
            if f[0] == field:
                return f[1]
        return None

    @classmethod
    def bind(cls, bound_fields):
        fields = {}
        for name, type_ in cls._fields_:
            if hasattr(type_, "restype"):
                if name in bound_fields:
                    if bound_fields[name] is None:
                        fields[name] = type_()
                    else:
                        # use a closure to capture the callback from the loop scope
                        fields[name] = (
                            type_((lambda callback: lambda *args: callback(*args))(
                                bound_fields[name]))
                        )
                    del bound_fields[name]
                else:
                    # default callback implementation (does nothing)
                    try:
                        default_ = type_(0).restype().value
                    except TypeError:
                        default_ = None
                    fields[name] = type_((
                        lambda default_: lambda *args: default_)(default_))
            else:
                # not a callback function, use default initialization
                if name in bound_fields:
                    fields[name] = bound_fields[name]
                    del bound_fields[name]
                else:
                    fields[name] = type_()
        if len(bound_fields) != 0:
            raise ValueError(
                "Cannot bind the following unknown callback(s) {}.{}".format(
                    cls.__name__, bound_fields.keys()
            ))
        return cls(**fields)


class Union(ctypes.Union, AsDictMixin):
    pass



def string_cast(char_pointer, encoding='utf-8', errors='strict'):
    value = ctypes.cast(char_pointer, ctypes.c_char_p).value
    if value is not None and encoding is not None:
        value = value.decode(encoding, errors=errors)
    return value


def char_pointer_cast(string, encoding='utf-8'):
    if encoding is not None:
        try:
            string = string.encode(encoding)
        except AttributeError:
            # In Python3, bytes has no encode attribute
            pass
    string = ctypes.c_char_p(string)
    return ctypes.cast(string, ctypes.POINTER(ctypes.c_char))



c_int128 = ctypes.c_ubyte*16
c_uint128 = c_int128
void = None
if ctypes.sizeof(ctypes.c_longdouble) == 16:
    c_long_double_t = ctypes.c_longdouble
else:
    c_long_double_t = ctypes.c_ubyte*16

class FunctionFactoryStub:
    def __getattr__(self, _):
      return ctypes.CFUNCTYPE(lambda y:y)

# libraries['FIXME_STUB'] explanation
# As you did not list (-l libraryname.so) a library that exports this function
# This is a non-working stub instead. 
# You can either re-run clan2py with -l /path/to/library.so
# Or manually fix this by comment the ctypes.CDLL loading
_libraries = {}
_libraries['FIXME_STUB'] = FunctionFactoryStub() #  ctypes.CDLL('FIXME_STUB')
# if linux, elif window, else raise error
LIB_HIP = "libamdhip64"
LIB_HIPRTC = "libhiprtc"

try:
    if "linux" in sys.platform:
        _libraries[LIB_HIP] = ctypes.CDLL('/opt/rocm/lib/libamdhip64.so')
        _libraries[LIB_HIPRTC] = ctypes.CDLL('/opt/rocm/lib/libhiprtc.so')
    elif "win" in sys.platform:
        import os 
        HIP_PATH = os.getenv("HIP_PATH", None)
        if not HIP_PATH:
            raise RuntimeError("HIP_PATH not set")
        _libraries[LIB_HIP] = ctypes.cdll.LoadLibrary("amdhip64")
        _libraries[LIB_HIPRTC] = ctypes.CDLL(os.path.join(HIP_PATH, 'bin', 'hiprtc0505.dll'))
    else:
        raise RuntimeError("Only windows/linux are supported")
except Exception as err:
    raise Exception("Error: {0}".format(err))



# values for enumeration 'hiprtcResult'
hiprtcResult__enumvalues = {
    0: 'HIPRTC_SUCCESS',
    1: 'HIPRTC_ERROR_OUT_OF_MEMORY',
    2: 'HIPRTC_ERROR_PROGRAM_CREATION_FAILURE',
    3: 'HIPRTC_ERROR_INVALID_INPUT',
    4: 'HIPRTC_ERROR_INVALID_PROGRAM',
    5: 'HIPRTC_ERROR_INVALID_OPTION',
    6: 'HIPRTC_ERROR_COMPILATION',
    7: 'HIPRTC_ERROR_BUILTIN_OPERATION_FAILURE',
    8: 'HIPRTC_ERROR_NO_NAME_EXPRESSIONS_AFTER_COMPILATION',
    9: 'HIPRTC_ERROR_NO_LOWERED_NAMES_BEFORE_COMPILATION',
    10: 'HIPRTC_ERROR_NAME_EXPRESSION_NOT_VALID',
    11: 'HIPRTC_ERROR_INTERNAL_ERROR',
    100: 'HIPRTC_ERROR_LINKING',
}
HIPRTC_SUCCESS = 0
HIPRTC_ERROR_OUT_OF_MEMORY = 1
HIPRTC_ERROR_PROGRAM_CREATION_FAILURE = 2
HIPRTC_ERROR_INVALID_INPUT = 3
HIPRTC_ERROR_INVALID_PROGRAM = 4
HIPRTC_ERROR_INVALID_OPTION = 5
HIPRTC_ERROR_COMPILATION = 6
HIPRTC_ERROR_BUILTIN_OPERATION_FAILURE = 7
HIPRTC_ERROR_NO_NAME_EXPRESSIONS_AFTER_COMPILATION = 8
HIPRTC_ERROR_NO_LOWERED_NAMES_BEFORE_COMPILATION = 9
HIPRTC_ERROR_NAME_EXPRESSION_NOT_VALID = 10
HIPRTC_ERROR_INTERNAL_ERROR = 11
HIPRTC_ERROR_LINKING = 100
hiprtcResult = ctypes.c_uint32 # enum

# values for enumeration 'hiprtcJIT_option'
hiprtcJIT_option__enumvalues = {
    0: 'HIPRTC_JIT_MAX_REGISTERS',
    1: 'HIPRTC_JIT_THREADS_PER_BLOCK',
    2: 'HIPRTC_JIT_WALL_TIME',
    3: 'HIPRTC_JIT_INFO_LOG_BUFFER',
    4: 'HIPRTC_JIT_INFO_LOG_BUFFER_SIZE_BYTES',
    5: 'HIPRTC_JIT_ERROR_LOG_BUFFER',
    6: 'HIPRTC_JIT_ERROR_LOG_BUFFER_SIZE_BYTES',
    7: 'HIPRTC_JIT_OPTIMIZATION_LEVEL',
    8: 'HIPRTC_JIT_TARGET_FROM_HIPCONTEXT',
    9: 'HIPRTC_JIT_TARGET',
    10: 'HIPRTC_JIT_FALLBACK_STRATEGY',
    11: 'HIPRTC_JIT_GENERATE_DEBUG_INFO',
    12: 'HIPRTC_JIT_LOG_VERBOSE',
    13: 'HIPRTC_JIT_GENERATE_LINE_INFO',
    14: 'HIPRTC_JIT_CACHE_MODE',
    15: 'HIPRTC_JIT_NEW_SM3X_OPT',
    16: 'HIPRTC_JIT_FAST_COMPILE',
    17: 'HIPRTC_JIT_GLOBAL_SYMBOL_NAMES',
    18: 'HIPRTC_JIT_GLOBAL_SYMBOL_ADDRESS',
    19: 'HIPRTC_JIT_GLOBAL_SYMBOL_COUNT',
    20: 'HIPRTC_JIT_LTO',
    21: 'HIPRTC_JIT_FTZ',
    22: 'HIPRTC_JIT_PREC_DIV',
    23: 'HIPRTC_JIT_PREC_SQRT',
    24: 'HIPRTC_JIT_FMA',
    25: 'HIPRTC_JIT_NUM_OPTIONS',
    10000: 'HIPRTC_JIT_IR_TO_ISA_OPT_EXT',
    10001: 'HIPRTC_JIT_IR_TO_ISA_OPT_COUNT_EXT',
}
HIPRTC_JIT_MAX_REGISTERS = 0
HIPRTC_JIT_THREADS_PER_BLOCK = 1
HIPRTC_JIT_WALL_TIME = 2
HIPRTC_JIT_INFO_LOG_BUFFER = 3
HIPRTC_JIT_INFO_LOG_BUFFER_SIZE_BYTES = 4
HIPRTC_JIT_ERROR_LOG_BUFFER = 5
HIPRTC_JIT_ERROR_LOG_BUFFER_SIZE_BYTES = 6
HIPRTC_JIT_OPTIMIZATION_LEVEL = 7
HIPRTC_JIT_TARGET_FROM_HIPCONTEXT = 8
HIPRTC_JIT_TARGET = 9
HIPRTC_JIT_FALLBACK_STRATEGY = 10
HIPRTC_JIT_GENERATE_DEBUG_INFO = 11
HIPRTC_JIT_LOG_VERBOSE = 12
HIPRTC_JIT_GENERATE_LINE_INFO = 13
HIPRTC_JIT_CACHE_MODE = 14
HIPRTC_JIT_NEW_SM3X_OPT = 15
HIPRTC_JIT_FAST_COMPILE = 16
HIPRTC_JIT_GLOBAL_SYMBOL_NAMES = 17
HIPRTC_JIT_GLOBAL_SYMBOL_ADDRESS = 18
HIPRTC_JIT_GLOBAL_SYMBOL_COUNT = 19
HIPRTC_JIT_LTO = 20
HIPRTC_JIT_FTZ = 21
HIPRTC_JIT_PREC_DIV = 22
HIPRTC_JIT_PREC_SQRT = 23
HIPRTC_JIT_FMA = 24
HIPRTC_JIT_NUM_OPTIONS = 25
HIPRTC_JIT_IR_TO_ISA_OPT_EXT = 10000
HIPRTC_JIT_IR_TO_ISA_OPT_COUNT_EXT = 10001
hiprtcJIT_option = ctypes.c_uint32 # enum

# values for enumeration 'hiprtcJITInputType'
hiprtcJITInputType__enumvalues = {
    0: 'HIPRTC_JIT_INPUT_CUBIN',
    1: 'HIPRTC_JIT_INPUT_PTX',
    2: 'HIPRTC_JIT_INPUT_FATBINARY',
    3: 'HIPRTC_JIT_INPUT_OBJECT',
    4: 'HIPRTC_JIT_INPUT_LIBRARY',
    5: 'HIPRTC_JIT_INPUT_NVVM',
    6: 'HIPRTC_JIT_NUM_LEGACY_INPUT_TYPES',
    100: 'HIPRTC_JIT_INPUT_LLVM_BITCODE',
    101: 'HIPRTC_JIT_INPUT_LLVM_BUNDLED_BITCODE',
    102: 'HIPRTC_JIT_INPUT_LLVM_ARCHIVES_OF_BUNDLED_BITCODE',
    9: 'HIPRTC_JIT_NUM_INPUT_TYPES',
}
HIPRTC_JIT_INPUT_CUBIN = 0
HIPRTC_JIT_INPUT_PTX = 1
HIPRTC_JIT_INPUT_FATBINARY = 2
HIPRTC_JIT_INPUT_OBJECT = 3
HIPRTC_JIT_INPUT_LIBRARY = 4
HIPRTC_JIT_INPUT_NVVM = 5
HIPRTC_JIT_NUM_LEGACY_INPUT_TYPES = 6
HIPRTC_JIT_INPUT_LLVM_BITCODE = 100
HIPRTC_JIT_INPUT_LLVM_BUNDLED_BITCODE = 101
HIPRTC_JIT_INPUT_LLVM_ARCHIVES_OF_BUNDLED_BITCODE = 102
HIPRTC_JIT_NUM_INPUT_TYPES = 9
hiprtcJITInputType = ctypes.c_uint32 # enum
class struct_ihiprtcLinkState(Structure):
    pass

hiprtcLinkState = ctypes.POINTER(struct_ihiprtcLinkState)
try:
    hiprtcGetErrorString = _libraries[LIB_HIPRTC].hiprtcGetErrorString
    hiprtcGetErrorString.restype = ctypes.POINTER(ctypes.c_char)
    hiprtcGetErrorString.argtypes = [hiprtcResult]
except AttributeError:
    pass
try:
    hiprtcVersion = _libraries[LIB_HIPRTC].hiprtcVersion
    hiprtcVersion.restype = hiprtcResult
    hiprtcVersion.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
class struct__hiprtcProgram(Structure):
    pass

hiprtcProgram = ctypes.POINTER(struct__hiprtcProgram)
try:
    hiprtcAddNameExpression = _libraries[LIB_HIPRTC].hiprtcAddNameExpression
    hiprtcAddNameExpression.restype = hiprtcResult
    hiprtcAddNameExpression.argtypes = [hiprtcProgram, ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    hiprtcCompileProgram = _libraries[LIB_HIPRTC].hiprtcCompileProgram
    hiprtcCompileProgram.restype = hiprtcResult
    hiprtcCompileProgram.argtypes = [hiprtcProgram, ctypes.c_int32, ctypes.POINTER(ctypes.POINTER(ctypes.c_char))]
except AttributeError:
    pass
try:
    hiprtcCreateProgram = _libraries[LIB_HIPRTC].hiprtcCreateProgram
    hiprtcCreateProgram.restype = hiprtcResult
    hiprtcCreateProgram.argtypes = [ctypes.POINTER(ctypes.POINTER(struct__hiprtcProgram)), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char), ctypes.c_int32, ctypes.POINTER(ctypes.POINTER(ctypes.c_char)), ctypes.POINTER(ctypes.POINTER(ctypes.c_char))]
except AttributeError:
    pass
try:
    hiprtcDestroyProgram = _libraries[LIB_HIPRTC].hiprtcDestroyProgram
    hiprtcDestroyProgram.restype = hiprtcResult
    hiprtcDestroyProgram.argtypes = [ctypes.POINTER(ctypes.POINTER(struct__hiprtcProgram))]
except AttributeError:
    pass
try:
    hiprtcGetLoweredName = _libraries[LIB_HIPRTC].hiprtcGetLoweredName
    hiprtcGetLoweredName.restype = hiprtcResult
    hiprtcGetLoweredName.argtypes = [hiprtcProgram, ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.POINTER(ctypes.c_char))]
except AttributeError:
    pass
try:
    hiprtcGetProgramLog = _libraries[LIB_HIPRTC].hiprtcGetProgramLog
    hiprtcGetProgramLog.restype = hiprtcResult
    hiprtcGetProgramLog.argtypes = [hiprtcProgram, ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    hiprtcGetProgramLogSize = _libraries[LIB_HIPRTC].hiprtcGetProgramLogSize
    hiprtcGetProgramLogSize.restype = hiprtcResult
    hiprtcGetProgramLogSize.argtypes = [hiprtcProgram, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    hiprtcGetCode = _libraries[LIB_HIPRTC].hiprtcGetCode
    hiprtcGetCode.restype = hiprtcResult
    hiprtcGetCode.argtypes = [hiprtcProgram, ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    hiprtcGetCodeSize = _libraries[LIB_HIPRTC].hiprtcGetCodeSize
    hiprtcGetCodeSize.restype = hiprtcResult
    hiprtcGetCodeSize.argtypes = [hiprtcProgram, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    hiprtcGetBitcode = _libraries[LIB_HIPRTC].hiprtcGetBitcode
    hiprtcGetBitcode.restype = hiprtcResult
    hiprtcGetBitcode.argtypes = [hiprtcProgram, ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    hiprtcGetBitcodeSize = _libraries[LIB_HIPRTC].hiprtcGetBitcodeSize
    hiprtcGetBitcodeSize.restype = hiprtcResult
    hiprtcGetBitcodeSize.argtypes = [hiprtcProgram, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    hiprtcLinkCreate = _libraries[LIB_HIPRTC].hiprtcLinkCreate
    hiprtcLinkCreate.restype = hiprtcResult
    hiprtcLinkCreate.argtypes = [ctypes.c_uint32, ctypes.POINTER(hiprtcJIT_option), ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(ctypes.POINTER(struct_ihiprtcLinkState))]
except AttributeError:
    pass
try:
    hiprtcLinkAddFile = _libraries[LIB_HIPRTC].hiprtcLinkAddFile
    hiprtcLinkAddFile.restype = hiprtcResult
    hiprtcLinkAddFile.argtypes = [hiprtcLinkState, hiprtcJITInputType, ctypes.POINTER(ctypes.c_char), ctypes.c_uint32, ctypes.POINTER(hiprtcJIT_option), ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
size_t = ctypes.c_uint64
try:
    hiprtcLinkAddData = _libraries[LIB_HIPRTC].hiprtcLinkAddData
    hiprtcLinkAddData.restype = hiprtcResult
    hiprtcLinkAddData.argtypes = [hiprtcLinkState, hiprtcJITInputType, ctypes.POINTER(None), size_t, ctypes.POINTER(ctypes.c_char), ctypes.c_uint32, ctypes.POINTER(hiprtcJIT_option), ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    hiprtcLinkComplete = _libraries[LIB_HIPRTC].hiprtcLinkComplete
    hiprtcLinkComplete.restype = hiprtcResult
    hiprtcLinkComplete.argtypes = [hiprtcLinkState, ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    hiprtcLinkDestroy = _libraries[LIB_HIPRTC].hiprtcLinkDestroy
    hiprtcLinkDestroy.restype = hiprtcResult
    hiprtcLinkDestroy.argtypes = [hiprtcLinkState]
except AttributeError:
    pass

# values for enumeration 'c__Ea_HIP_SUCCESS'
c__Ea_HIP_SUCCESS__enumvalues = {
    0: 'HIP_SUCCESS',
    1: 'HIP_ERROR_INVALID_VALUE',
    2: 'HIP_ERROR_NOT_INITIALIZED',
    3: 'HIP_ERROR_LAUNCH_OUT_OF_RESOURCES',
}
HIP_SUCCESS = 0
HIP_ERROR_INVALID_VALUE = 1
HIP_ERROR_NOT_INITIALIZED = 2
HIP_ERROR_LAUNCH_OUT_OF_RESOURCES = 3
c__Ea_HIP_SUCCESS = ctypes.c_uint32 # enum
class struct_c__SA_hipDeviceArch_t(Structure):
    pass

struct_c__SA_hipDeviceArch_t._pack_ = 1 # source:False
struct_c__SA_hipDeviceArch_t._fields_ = [
    ('hasGlobalInt32Atomics', ctypes.c_uint32, 1),
    ('hasGlobalFloatAtomicExch', ctypes.c_uint32, 1),
    ('hasSharedInt32Atomics', ctypes.c_uint32, 1),
    ('hasSharedFloatAtomicExch', ctypes.c_uint32, 1),
    ('hasFloatAtomicAdd', ctypes.c_uint32, 1),
    ('hasGlobalInt64Atomics', ctypes.c_uint32, 1),
    ('hasSharedInt64Atomics', ctypes.c_uint32, 1),
    ('hasDoubles', ctypes.c_uint32, 1),
    ('hasWarpVote', ctypes.c_uint32, 1),
    ('hasWarpBallot', ctypes.c_uint32, 1),
    ('hasWarpShuffle', ctypes.c_uint32, 1),
    ('hasFunnelShift', ctypes.c_uint32, 1),
    ('hasThreadFenceSystem', ctypes.c_uint32, 1),
    ('hasSyncThreadsExt', ctypes.c_uint32, 1),
    ('hasSurfaceFuncs', ctypes.c_uint32, 1),
    ('has3dGrid', ctypes.c_uint32, 1),
    ('hasDynamicParallelism', ctypes.c_uint32, 1),
    ('PADDING_0', ctypes.c_uint16, 15),
]

hipDeviceArch_t = struct_c__SA_hipDeviceArch_t
class struct_hipUUID_t(Structure):
    pass

struct_hipUUID_t._pack_ = 1 # source:False
struct_hipUUID_t._fields_ = [
    ('bytes', ctypes.c_char * 16),
]

hipUUID = struct_hipUUID_t
class struct_hipDeviceProp_t(Structure):
    pass

struct_hipDeviceProp_t._pack_ = 1 # source:False
struct_hipDeviceProp_t._fields_ = [
    ('name', ctypes.c_char * 256),
    ('totalGlobalMem', ctypes.c_uint64),
    ('sharedMemPerBlock', ctypes.c_uint64),
    ('regsPerBlock', ctypes.c_int32),
    ('warpSize', ctypes.c_int32),
    ('maxThreadsPerBlock', ctypes.c_int32),
    ('maxThreadsDim', ctypes.c_int32 * 3),
    ('maxGridSize', ctypes.c_int32 * 3),
    ('clockRate', ctypes.c_int32),
    ('memoryClockRate', ctypes.c_int32),
    ('memoryBusWidth', ctypes.c_int32),
    ('totalConstMem', ctypes.c_uint64),
    ('major', ctypes.c_int32),
    ('minor', ctypes.c_int32),
    ('multiProcessorCount', ctypes.c_int32),
    ('l2CacheSize', ctypes.c_int32),
    ('maxThreadsPerMultiProcessor', ctypes.c_int32),
    ('computeMode', ctypes.c_int32),
    ('clockInstructionRate', ctypes.c_int32),
    ('arch', hipDeviceArch_t),
    ('concurrentKernels', ctypes.c_int32),
    ('pciDomainID', ctypes.c_int32),
    ('pciBusID', ctypes.c_int32),
    ('pciDeviceID', ctypes.c_int32),
    ('maxSharedMemoryPerMultiProcessor', ctypes.c_uint64),
    ('isMultiGpuBoard', ctypes.c_int32),
    ('canMapHostMemory', ctypes.c_int32),
    ('gcnArch', ctypes.c_int32),
    ('gcnArchName', ctypes.c_char * 256),
    ('integrated', ctypes.c_int32),
    ('cooperativeLaunch', ctypes.c_int32),
    ('cooperativeMultiDeviceLaunch', ctypes.c_int32),
    ('maxTexture1DLinear', ctypes.c_int32),
    ('maxTexture1D', ctypes.c_int32),
    ('maxTexture2D', ctypes.c_int32 * 2),
    ('maxTexture3D', ctypes.c_int32 * 3),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('hdpMemFlushCntl', ctypes.POINTER(ctypes.c_uint32)),
    ('hdpRegFlushCntl', ctypes.POINTER(ctypes.c_uint32)),
    ('memPitch', ctypes.c_uint64),
    ('textureAlignment', ctypes.c_uint64),
    ('texturePitchAlignment', ctypes.c_uint64),
    ('kernelExecTimeoutEnabled', ctypes.c_int32),
    ('ECCEnabled', ctypes.c_int32),
    ('tccDriver', ctypes.c_int32),
    ('cooperativeMultiDeviceUnmatchedFunc', ctypes.c_int32),
    ('cooperativeMultiDeviceUnmatchedGridDim', ctypes.c_int32),
    ('cooperativeMultiDeviceUnmatchedBlockDim', ctypes.c_int32),
    ('cooperativeMultiDeviceUnmatchedSharedMem', ctypes.c_int32),
    ('isLargeBar', ctypes.c_int32),
    ('asicRevision', ctypes.c_int32),
    ('managedMemory', ctypes.c_int32),
    ('directManagedMemAccessFromHost', ctypes.c_int32),
    ('concurrentManagedAccess', ctypes.c_int32),
    ('pageableMemoryAccess', ctypes.c_int32),
    ('pageableMemoryAccessUsesHostPageTables', ctypes.c_int32),
]

hipDeviceProp_t = struct_hipDeviceProp_t

# values for enumeration 'hipMemoryType'
hipMemoryType__enumvalues = {
    0: 'hipMemoryTypeHost',
    1: 'hipMemoryTypeDevice',
    2: 'hipMemoryTypeArray',
    3: 'hipMemoryTypeUnified',
    4: 'hipMemoryTypeManaged',
}
hipMemoryTypeHost = 0
hipMemoryTypeDevice = 1
hipMemoryTypeArray = 2
hipMemoryTypeUnified = 3
hipMemoryTypeManaged = 4
hipMemoryType = ctypes.c_uint32 # enum
class struct_hipPointerAttribute_t(Structure):
    pass

class union_hipPointerAttribute_t_0(Union):
    _pack_ = 1 # source:False
    _fields_ = [
    ('memoryType', hipMemoryType),
    ('type', hipMemoryType),
     ]

struct_hipPointerAttribute_t._pack_ = 1 # source:False
struct_hipPointerAttribute_t._anonymous_ = ('_0',)
struct_hipPointerAttribute_t._fields_ = [
    ('_0', union_hipPointerAttribute_t_0),
    ('device', ctypes.c_int32),
    ('devicePointer', ctypes.POINTER(None)),
    ('hostPointer', ctypes.POINTER(None)),
    ('isManaged', ctypes.c_int32),
    ('allocationFlags', ctypes.c_uint32),
]

hipPointerAttribute_t = struct_hipPointerAttribute_t

# values for enumeration 'hipError_t'
hipError_t__enumvalues = {
    0: 'hipSuccess',
    1: 'hipErrorInvalidValue',
    2: 'hipErrorOutOfMemory',
    2: 'hipErrorMemoryAllocation',
    3: 'hipErrorNotInitialized',
    3: 'hipErrorInitializationError',
    4: 'hipErrorDeinitialized',
    5: 'hipErrorProfilerDisabled',
    6: 'hipErrorProfilerNotInitialized',
    7: 'hipErrorProfilerAlreadyStarted',
    8: 'hipErrorProfilerAlreadyStopped',
    9: 'hipErrorInvalidConfiguration',
    12: 'hipErrorInvalidPitchValue',
    13: 'hipErrorInvalidSymbol',
    17: 'hipErrorInvalidDevicePointer',
    21: 'hipErrorInvalidMemcpyDirection',
    35: 'hipErrorInsufficientDriver',
    52: 'hipErrorMissingConfiguration',
    53: 'hipErrorPriorLaunchFailure',
    98: 'hipErrorInvalidDeviceFunction',
    100: 'hipErrorNoDevice',
    101: 'hipErrorInvalidDevice',
    200: 'hipErrorInvalidImage',
    201: 'hipErrorInvalidContext',
    202: 'hipErrorContextAlreadyCurrent',
    205: 'hipErrorMapFailed',
    205: 'hipErrorMapBufferObjectFailed',
    206: 'hipErrorUnmapFailed',
    207: 'hipErrorArrayIsMapped',
    208: 'hipErrorAlreadyMapped',
    209: 'hipErrorNoBinaryForGpu',
    210: 'hipErrorAlreadyAcquired',
    211: 'hipErrorNotMapped',
    212: 'hipErrorNotMappedAsArray',
    213: 'hipErrorNotMappedAsPointer',
    214: 'hipErrorECCNotCorrectable',
    215: 'hipErrorUnsupportedLimit',
    216: 'hipErrorContextAlreadyInUse',
    217: 'hipErrorPeerAccessUnsupported',
    218: 'hipErrorInvalidKernelFile',
    219: 'hipErrorInvalidGraphicsContext',
    300: 'hipErrorInvalidSource',
    301: 'hipErrorFileNotFound',
    302: 'hipErrorSharedObjectSymbolNotFound',
    303: 'hipErrorSharedObjectInitFailed',
    304: 'hipErrorOperatingSystem',
    400: 'hipErrorInvalidHandle',
    400: 'hipErrorInvalidResourceHandle',
    401: 'hipErrorIllegalState',
    500: 'hipErrorNotFound',
    600: 'hipErrorNotReady',
    700: 'hipErrorIllegalAddress',
    701: 'hipErrorLaunchOutOfResources',
    702: 'hipErrorLaunchTimeOut',
    704: 'hipErrorPeerAccessAlreadyEnabled',
    705: 'hipErrorPeerAccessNotEnabled',
    708: 'hipErrorSetOnActiveProcess',
    709: 'hipErrorContextIsDestroyed',
    710: 'hipErrorAssert',
    712: 'hipErrorHostMemoryAlreadyRegistered',
    713: 'hipErrorHostMemoryNotRegistered',
    719: 'hipErrorLaunchFailure',
    720: 'hipErrorCooperativeLaunchTooLarge',
    801: 'hipErrorNotSupported',
    900: 'hipErrorStreamCaptureUnsupported',
    901: 'hipErrorStreamCaptureInvalidated',
    902: 'hipErrorStreamCaptureMerge',
    903: 'hipErrorStreamCaptureUnmatched',
    904: 'hipErrorStreamCaptureUnjoined',
    905: 'hipErrorStreamCaptureIsolation',
    906: 'hipErrorStreamCaptureImplicit',
    907: 'hipErrorCapturedEvent',
    908: 'hipErrorStreamCaptureWrongThread',
    910: 'hipErrorGraphExecUpdateFailure',
    999: 'hipErrorUnknown',
    1052: 'hipErrorRuntimeMemory',
    1053: 'hipErrorRuntimeOther',
    1054: 'hipErrorTbd',
}
hipSuccess = 0
hipErrorInvalidValue = 1
hipErrorOutOfMemory = 2
hipErrorMemoryAllocation = 2
hipErrorNotInitialized = 3
hipErrorInitializationError = 3
hipErrorDeinitialized = 4
hipErrorProfilerDisabled = 5
hipErrorProfilerNotInitialized = 6
hipErrorProfilerAlreadyStarted = 7
hipErrorProfilerAlreadyStopped = 8
hipErrorInvalidConfiguration = 9
hipErrorInvalidPitchValue = 12
hipErrorInvalidSymbol = 13
hipErrorInvalidDevicePointer = 17
hipErrorInvalidMemcpyDirection = 21
hipErrorInsufficientDriver = 35
hipErrorMissingConfiguration = 52
hipErrorPriorLaunchFailure = 53
hipErrorInvalidDeviceFunction = 98
hipErrorNoDevice = 100
hipErrorInvalidDevice = 101
hipErrorInvalidImage = 200
hipErrorInvalidContext = 201
hipErrorContextAlreadyCurrent = 202
hipErrorMapFailed = 205
hipErrorMapBufferObjectFailed = 205
hipErrorUnmapFailed = 206
hipErrorArrayIsMapped = 207
hipErrorAlreadyMapped = 208
hipErrorNoBinaryForGpu = 209
hipErrorAlreadyAcquired = 210
hipErrorNotMapped = 211
hipErrorNotMappedAsArray = 212
hipErrorNotMappedAsPointer = 213
hipErrorECCNotCorrectable = 214
hipErrorUnsupportedLimit = 215
hipErrorContextAlreadyInUse = 216
hipErrorPeerAccessUnsupported = 217
hipErrorInvalidKernelFile = 218
hipErrorInvalidGraphicsContext = 219
hipErrorInvalidSource = 300
hipErrorFileNotFound = 301
hipErrorSharedObjectSymbolNotFound = 302
hipErrorSharedObjectInitFailed = 303
hipErrorOperatingSystem = 304
hipErrorInvalidHandle = 400
hipErrorInvalidResourceHandle = 400
hipErrorIllegalState = 401
hipErrorNotFound = 500
hipErrorNotReady = 600
hipErrorIllegalAddress = 700
hipErrorLaunchOutOfResources = 701
hipErrorLaunchTimeOut = 702
hipErrorPeerAccessAlreadyEnabled = 704
hipErrorPeerAccessNotEnabled = 705
hipErrorSetOnActiveProcess = 708
hipErrorContextIsDestroyed = 709
hipErrorAssert = 710
hipErrorHostMemoryAlreadyRegistered = 712
hipErrorHostMemoryNotRegistered = 713
hipErrorLaunchFailure = 719
hipErrorCooperativeLaunchTooLarge = 720
hipErrorNotSupported = 801
hipErrorStreamCaptureUnsupported = 900
hipErrorStreamCaptureInvalidated = 901
hipErrorStreamCaptureMerge = 902
hipErrorStreamCaptureUnmatched = 903
hipErrorStreamCaptureUnjoined = 904
hipErrorStreamCaptureIsolation = 905
hipErrorStreamCaptureImplicit = 906
hipErrorCapturedEvent = 907
hipErrorStreamCaptureWrongThread = 908
hipErrorGraphExecUpdateFailure = 910
hipErrorUnknown = 999
hipErrorRuntimeMemory = 1052
hipErrorRuntimeOther = 1053
hipErrorTbd = 1054
hipError_t = ctypes.c_uint32 # enum

# values for enumeration 'hipDeviceAttribute_t'
hipDeviceAttribute_t__enumvalues = {
    0: 'hipDeviceAttributeCudaCompatibleBegin',
    0: 'hipDeviceAttributeEccEnabled',
    1: 'hipDeviceAttributeAccessPolicyMaxWindowSize',
    2: 'hipDeviceAttributeAsyncEngineCount',
    3: 'hipDeviceAttributeCanMapHostMemory',
    4: 'hipDeviceAttributeCanUseHostPointerForRegisteredMem',
    5: 'hipDeviceAttributeClockRate',
    6: 'hipDeviceAttributeComputeMode',
    7: 'hipDeviceAttributeComputePreemptionSupported',
    8: 'hipDeviceAttributeConcurrentKernels',
    9: 'hipDeviceAttributeConcurrentManagedAccess',
    10: 'hipDeviceAttributeCooperativeLaunch',
    11: 'hipDeviceAttributeCooperativeMultiDeviceLaunch',
    12: 'hipDeviceAttributeDeviceOverlap',
    13: 'hipDeviceAttributeDirectManagedMemAccessFromHost',
    14: 'hipDeviceAttributeGlobalL1CacheSupported',
    15: 'hipDeviceAttributeHostNativeAtomicSupported',
    16: 'hipDeviceAttributeIntegrated',
    17: 'hipDeviceAttributeIsMultiGpuBoard',
    18: 'hipDeviceAttributeKernelExecTimeout',
    19: 'hipDeviceAttributeL2CacheSize',
    20: 'hipDeviceAttributeLocalL1CacheSupported',
    21: 'hipDeviceAttributeLuid',
    22: 'hipDeviceAttributeLuidDeviceNodeMask',
    23: 'hipDeviceAttributeComputeCapabilityMajor',
    24: 'hipDeviceAttributeManagedMemory',
    25: 'hipDeviceAttributeMaxBlocksPerMultiProcessor',
    26: 'hipDeviceAttributeMaxBlockDimX',
    27: 'hipDeviceAttributeMaxBlockDimY',
    28: 'hipDeviceAttributeMaxBlockDimZ',
    29: 'hipDeviceAttributeMaxGridDimX',
    30: 'hipDeviceAttributeMaxGridDimY',
    31: 'hipDeviceAttributeMaxGridDimZ',
    32: 'hipDeviceAttributeMaxSurface1D',
    33: 'hipDeviceAttributeMaxSurface1DLayered',
    34: 'hipDeviceAttributeMaxSurface2D',
    35: 'hipDeviceAttributeMaxSurface2DLayered',
    36: 'hipDeviceAttributeMaxSurface3D',
    37: 'hipDeviceAttributeMaxSurfaceCubemap',
    38: 'hipDeviceAttributeMaxSurfaceCubemapLayered',
    39: 'hipDeviceAttributeMaxTexture1DWidth',
    40: 'hipDeviceAttributeMaxTexture1DLayered',
    41: 'hipDeviceAttributeMaxTexture1DLinear',
    42: 'hipDeviceAttributeMaxTexture1DMipmap',
    43: 'hipDeviceAttributeMaxTexture2DWidth',
    44: 'hipDeviceAttributeMaxTexture2DHeight',
    45: 'hipDeviceAttributeMaxTexture2DGather',
    46: 'hipDeviceAttributeMaxTexture2DLayered',
    47: 'hipDeviceAttributeMaxTexture2DLinear',
    48: 'hipDeviceAttributeMaxTexture2DMipmap',
    49: 'hipDeviceAttributeMaxTexture3DWidth',
    50: 'hipDeviceAttributeMaxTexture3DHeight',
    51: 'hipDeviceAttributeMaxTexture3DDepth',
    52: 'hipDeviceAttributeMaxTexture3DAlt',
    53: 'hipDeviceAttributeMaxTextureCubemap',
    54: 'hipDeviceAttributeMaxTextureCubemapLayered',
    55: 'hipDeviceAttributeMaxThreadsDim',
    56: 'hipDeviceAttributeMaxThreadsPerBlock',
    57: 'hipDeviceAttributeMaxThreadsPerMultiProcessor',
    58: 'hipDeviceAttributeMaxPitch',
    59: 'hipDeviceAttributeMemoryBusWidth',
    60: 'hipDeviceAttributeMemoryClockRate',
    61: 'hipDeviceAttributeComputeCapabilityMinor',
    62: 'hipDeviceAttributeMultiGpuBoardGroupID',
    63: 'hipDeviceAttributeMultiprocessorCount',
    64: 'hipDeviceAttributeName',
    65: 'hipDeviceAttributePageableMemoryAccess',
    66: 'hipDeviceAttributePageableMemoryAccessUsesHostPageTables',
    67: 'hipDeviceAttributePciBusId',
    68: 'hipDeviceAttributePciDeviceId',
    69: 'hipDeviceAttributePciDomainID',
    70: 'hipDeviceAttributePersistingL2CacheMaxSize',
    71: 'hipDeviceAttributeMaxRegistersPerBlock',
    72: 'hipDeviceAttributeMaxRegistersPerMultiprocessor',
    73: 'hipDeviceAttributeReservedSharedMemPerBlock',
    74: 'hipDeviceAttributeMaxSharedMemoryPerBlock',
    75: 'hipDeviceAttributeSharedMemPerBlockOptin',
    76: 'hipDeviceAttributeSharedMemPerMultiprocessor',
    77: 'hipDeviceAttributeSingleToDoublePrecisionPerfRatio',
    78: 'hipDeviceAttributeStreamPrioritiesSupported',
    79: 'hipDeviceAttributeSurfaceAlignment',
    80: 'hipDeviceAttributeTccDriver',
    81: 'hipDeviceAttributeTextureAlignment',
    82: 'hipDeviceAttributeTexturePitchAlignment',
    83: 'hipDeviceAttributeTotalConstantMemory',
    84: 'hipDeviceAttributeTotalGlobalMem',
    85: 'hipDeviceAttributeUnifiedAddressing',
    86: 'hipDeviceAttributeUuid',
    87: 'hipDeviceAttributeWarpSize',
    88: 'hipDeviceAttributeMemoryPoolsSupported',
    89: 'hipDeviceAttributeVirtualMemoryManagementSupported',
    9999: 'hipDeviceAttributeCudaCompatibleEnd',
    10000: 'hipDeviceAttributeAmdSpecificBegin',
    10000: 'hipDeviceAttributeClockInstructionRate',
    10001: 'hipDeviceAttributeArch',
    10002: 'hipDeviceAttributeMaxSharedMemoryPerMultiprocessor',
    10003: 'hipDeviceAttributeGcnArch',
    10004: 'hipDeviceAttributeGcnArchName',
    10005: 'hipDeviceAttributeHdpMemFlushCntl',
    10006: 'hipDeviceAttributeHdpRegFlushCntl',
    10007: 'hipDeviceAttributeCooperativeMultiDeviceUnmatchedFunc',
    10008: 'hipDeviceAttributeCooperativeMultiDeviceUnmatchedGridDim',
    10009: 'hipDeviceAttributeCooperativeMultiDeviceUnmatchedBlockDim',
    10010: 'hipDeviceAttributeCooperativeMultiDeviceUnmatchedSharedMem',
    10011: 'hipDeviceAttributeIsLargeBar',
    10012: 'hipDeviceAttributeAsicRevision',
    10013: 'hipDeviceAttributeCanUseStreamWaitValue',
    10014: 'hipDeviceAttributeImageSupport',
    10015: 'hipDeviceAttributePhysicalMultiProcessorCount',
    10016: 'hipDeviceAttributeFineGrainSupport',
    10017: 'hipDeviceAttributeWallClockRate',
    19999: 'hipDeviceAttributeAmdSpecificEnd',
    20000: 'hipDeviceAttributeVendorSpecificBegin',
}
hipDeviceAttributeCudaCompatibleBegin = 0
hipDeviceAttributeEccEnabled = 0
hipDeviceAttributeAccessPolicyMaxWindowSize = 1
hipDeviceAttributeAsyncEngineCount = 2
hipDeviceAttributeCanMapHostMemory = 3
hipDeviceAttributeCanUseHostPointerForRegisteredMem = 4
hipDeviceAttributeClockRate = 5
hipDeviceAttributeComputeMode = 6
hipDeviceAttributeComputePreemptionSupported = 7
hipDeviceAttributeConcurrentKernels = 8
hipDeviceAttributeConcurrentManagedAccess = 9
hipDeviceAttributeCooperativeLaunch = 10
hipDeviceAttributeCooperativeMultiDeviceLaunch = 11
hipDeviceAttributeDeviceOverlap = 12
hipDeviceAttributeDirectManagedMemAccessFromHost = 13
hipDeviceAttributeGlobalL1CacheSupported = 14
hipDeviceAttributeHostNativeAtomicSupported = 15
hipDeviceAttributeIntegrated = 16
hipDeviceAttributeIsMultiGpuBoard = 17
hipDeviceAttributeKernelExecTimeout = 18
hipDeviceAttributeL2CacheSize = 19
hipDeviceAttributeLocalL1CacheSupported = 20
hipDeviceAttributeLuid = 21
hipDeviceAttributeLuidDeviceNodeMask = 22
hipDeviceAttributeComputeCapabilityMajor = 23
hipDeviceAttributeManagedMemory = 24
hipDeviceAttributeMaxBlocksPerMultiProcessor = 25
hipDeviceAttributeMaxBlockDimX = 26
hipDeviceAttributeMaxBlockDimY = 27
hipDeviceAttributeMaxBlockDimZ = 28
hipDeviceAttributeMaxGridDimX = 29
hipDeviceAttributeMaxGridDimY = 30
hipDeviceAttributeMaxGridDimZ = 31
hipDeviceAttributeMaxSurface1D = 32
hipDeviceAttributeMaxSurface1DLayered = 33
hipDeviceAttributeMaxSurface2D = 34
hipDeviceAttributeMaxSurface2DLayered = 35
hipDeviceAttributeMaxSurface3D = 36
hipDeviceAttributeMaxSurfaceCubemap = 37
hipDeviceAttributeMaxSurfaceCubemapLayered = 38
hipDeviceAttributeMaxTexture1DWidth = 39
hipDeviceAttributeMaxTexture1DLayered = 40
hipDeviceAttributeMaxTexture1DLinear = 41
hipDeviceAttributeMaxTexture1DMipmap = 42
hipDeviceAttributeMaxTexture2DWidth = 43
hipDeviceAttributeMaxTexture2DHeight = 44
hipDeviceAttributeMaxTexture2DGather = 45
hipDeviceAttributeMaxTexture2DLayered = 46
hipDeviceAttributeMaxTexture2DLinear = 47
hipDeviceAttributeMaxTexture2DMipmap = 48
hipDeviceAttributeMaxTexture3DWidth = 49
hipDeviceAttributeMaxTexture3DHeight = 50
hipDeviceAttributeMaxTexture3DDepth = 51
hipDeviceAttributeMaxTexture3DAlt = 52
hipDeviceAttributeMaxTextureCubemap = 53
hipDeviceAttributeMaxTextureCubemapLayered = 54
hipDeviceAttributeMaxThreadsDim = 55
hipDeviceAttributeMaxThreadsPerBlock = 56
hipDeviceAttributeMaxThreadsPerMultiProcessor = 57
hipDeviceAttributeMaxPitch = 58
hipDeviceAttributeMemoryBusWidth = 59
hipDeviceAttributeMemoryClockRate = 60
hipDeviceAttributeComputeCapabilityMinor = 61
hipDeviceAttributeMultiGpuBoardGroupID = 62
hipDeviceAttributeMultiprocessorCount = 63
hipDeviceAttributeName = 64
hipDeviceAttributePageableMemoryAccess = 65
hipDeviceAttributePageableMemoryAccessUsesHostPageTables = 66
hipDeviceAttributePciBusId = 67
hipDeviceAttributePciDeviceId = 68
hipDeviceAttributePciDomainID = 69
hipDeviceAttributePersistingL2CacheMaxSize = 70
hipDeviceAttributeMaxRegistersPerBlock = 71
hipDeviceAttributeMaxRegistersPerMultiprocessor = 72
hipDeviceAttributeReservedSharedMemPerBlock = 73
hipDeviceAttributeMaxSharedMemoryPerBlock = 74
hipDeviceAttributeSharedMemPerBlockOptin = 75
hipDeviceAttributeSharedMemPerMultiprocessor = 76
hipDeviceAttributeSingleToDoublePrecisionPerfRatio = 77
hipDeviceAttributeStreamPrioritiesSupported = 78
hipDeviceAttributeSurfaceAlignment = 79
hipDeviceAttributeTccDriver = 80
hipDeviceAttributeTextureAlignment = 81
hipDeviceAttributeTexturePitchAlignment = 82
hipDeviceAttributeTotalConstantMemory = 83
hipDeviceAttributeTotalGlobalMem = 84
hipDeviceAttributeUnifiedAddressing = 85
hipDeviceAttributeUuid = 86
hipDeviceAttributeWarpSize = 87
hipDeviceAttributeMemoryPoolsSupported = 88
hipDeviceAttributeVirtualMemoryManagementSupported = 89
hipDeviceAttributeCudaCompatibleEnd = 9999
hipDeviceAttributeAmdSpecificBegin = 10000
hipDeviceAttributeClockInstructionRate = 10000
hipDeviceAttributeArch = 10001
hipDeviceAttributeMaxSharedMemoryPerMultiprocessor = 10002
hipDeviceAttributeGcnArch = 10003
hipDeviceAttributeGcnArchName = 10004
hipDeviceAttributeHdpMemFlushCntl = 10005
hipDeviceAttributeHdpRegFlushCntl = 10006
hipDeviceAttributeCooperativeMultiDeviceUnmatchedFunc = 10007
hipDeviceAttributeCooperativeMultiDeviceUnmatchedGridDim = 10008
hipDeviceAttributeCooperativeMultiDeviceUnmatchedBlockDim = 10009
hipDeviceAttributeCooperativeMultiDeviceUnmatchedSharedMem = 10010
hipDeviceAttributeIsLargeBar = 10011
hipDeviceAttributeAsicRevision = 10012
hipDeviceAttributeCanUseStreamWaitValue = 10013
hipDeviceAttributeImageSupport = 10014
hipDeviceAttributePhysicalMultiProcessorCount = 10015
hipDeviceAttributeFineGrainSupport = 10016
hipDeviceAttributeWallClockRate = 10017
hipDeviceAttributeAmdSpecificEnd = 19999
hipDeviceAttributeVendorSpecificBegin = 20000
hipDeviceAttribute_t = ctypes.c_uint32 # enum

# values for enumeration 'hipComputeMode'
hipComputeMode__enumvalues = {
    0: 'hipComputeModeDefault',
    1: 'hipComputeModeExclusive',
    2: 'hipComputeModeProhibited',
    3: 'hipComputeModeExclusiveProcess',
}
hipComputeModeDefault = 0
hipComputeModeExclusive = 1
hipComputeModeProhibited = 2
hipComputeModeExclusiveProcess = 3
hipComputeMode = ctypes.c_uint32 # enum
hipDeviceptr_t = ctypes.POINTER(None)

# values for enumeration 'hipChannelFormatKind'
hipChannelFormatKind__enumvalues = {
    0: 'hipChannelFormatKindSigned',
    1: 'hipChannelFormatKindUnsigned',
    2: 'hipChannelFormatKindFloat',
    3: 'hipChannelFormatKindNone',
}
hipChannelFormatKindSigned = 0
hipChannelFormatKindUnsigned = 1
hipChannelFormatKindFloat = 2
hipChannelFormatKindNone = 3
hipChannelFormatKind = ctypes.c_uint32 # enum
class struct_hipChannelFormatDesc(Structure):
    pass

struct_hipChannelFormatDesc._pack_ = 1 # source:False
struct_hipChannelFormatDesc._fields_ = [
    ('x', ctypes.c_int32),
    ('y', ctypes.c_int32),
    ('z', ctypes.c_int32),
    ('w', ctypes.c_int32),
    ('f', hipChannelFormatKind),
]

hipChannelFormatDesc = struct_hipChannelFormatDesc

# values for enumeration 'hipArray_Format'
hipArray_Format__enumvalues = {
    1: 'HIP_AD_FORMAT_UNSIGNED_INT8',
    2: 'HIP_AD_FORMAT_UNSIGNED_INT16',
    3: 'HIP_AD_FORMAT_UNSIGNED_INT32',
    8: 'HIP_AD_FORMAT_SIGNED_INT8',
    9: 'HIP_AD_FORMAT_SIGNED_INT16',
    10: 'HIP_AD_FORMAT_SIGNED_INT32',
    16: 'HIP_AD_FORMAT_HALF',
    32: 'HIP_AD_FORMAT_FLOAT',
}
HIP_AD_FORMAT_UNSIGNED_INT8 = 1
HIP_AD_FORMAT_UNSIGNED_INT16 = 2
HIP_AD_FORMAT_UNSIGNED_INT32 = 3
HIP_AD_FORMAT_SIGNED_INT8 = 8
HIP_AD_FORMAT_SIGNED_INT16 = 9
HIP_AD_FORMAT_SIGNED_INT32 = 10
HIP_AD_FORMAT_HALF = 16
HIP_AD_FORMAT_FLOAT = 32
hipArray_Format = ctypes.c_uint32 # enum
class struct_HIP_ARRAY_DESCRIPTOR(Structure):
    pass

struct_HIP_ARRAY_DESCRIPTOR._pack_ = 1 # source:False
struct_HIP_ARRAY_DESCRIPTOR._fields_ = [
    ('Width', ctypes.c_uint64),
    ('Height', ctypes.c_uint64),
    ('Format', hipArray_Format),
    ('NumChannels', ctypes.c_uint32),
]

HIP_ARRAY_DESCRIPTOR = struct_HIP_ARRAY_DESCRIPTOR
class struct_HIP_ARRAY3D_DESCRIPTOR(Structure):
    pass

struct_HIP_ARRAY3D_DESCRIPTOR._pack_ = 1 # source:False
struct_HIP_ARRAY3D_DESCRIPTOR._fields_ = [
    ('Width', ctypes.c_uint64),
    ('Height', ctypes.c_uint64),
    ('Depth', ctypes.c_uint64),
    ('Format', hipArray_Format),
    ('NumChannels', ctypes.c_uint32),
    ('Flags', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

HIP_ARRAY3D_DESCRIPTOR = struct_HIP_ARRAY3D_DESCRIPTOR
class struct_hipArray(Structure):
    pass

struct_hipArray._pack_ = 1 # source:False
struct_hipArray._fields_ = [
    ('data', ctypes.POINTER(None)),
    ('desc', struct_hipChannelFormatDesc),
    ('type', ctypes.c_uint32),
    ('width', ctypes.c_uint32),
    ('height', ctypes.c_uint32),
    ('depth', ctypes.c_uint32),
    ('Format', hipArray_Format),
    ('NumChannels', ctypes.c_uint32),
    ('isDrv', ctypes.c_bool),
    ('PADDING_0', ctypes.c_ubyte * 3),
    ('textureType', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
]

hipArray = struct_hipArray
class struct_hip_Memcpy2D(Structure):
    pass

struct_hip_Memcpy2D._pack_ = 1 # source:False
struct_hip_Memcpy2D._fields_ = [
    ('srcXInBytes', ctypes.c_uint64),
    ('srcY', ctypes.c_uint64),
    ('srcMemoryType', hipMemoryType),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('srcHost', ctypes.POINTER(None)),
    ('srcDevice', ctypes.POINTER(None)),
    ('srcArray', ctypes.POINTER(struct_hipArray)),
    ('srcPitch', ctypes.c_uint64),
    ('dstXInBytes', ctypes.c_uint64),
    ('dstY', ctypes.c_uint64),
    ('dstMemoryType', hipMemoryType),
    ('PADDING_1', ctypes.c_ubyte * 4),
    ('dstHost', ctypes.POINTER(None)),
    ('dstDevice', ctypes.POINTER(None)),
    ('dstArray', ctypes.POINTER(struct_hipArray)),
    ('dstPitch', ctypes.c_uint64),
    ('WidthInBytes', ctypes.c_uint64),
    ('Height', ctypes.c_uint64),
]

hip_Memcpy2D = struct_hip_Memcpy2D
hipArray_t = ctypes.POINTER(struct_hipArray)
hiparray = ctypes.POINTER(struct_hipArray)
hipArray_const_t = ctypes.POINTER(struct_hipArray)
class struct_hipMipmappedArray(Structure):
    pass

struct_hipMipmappedArray._pack_ = 1 # source:False
struct_hipMipmappedArray._fields_ = [
    ('data', ctypes.POINTER(None)),
    ('desc', struct_hipChannelFormatDesc),
    ('type', ctypes.c_uint32),
    ('width', ctypes.c_uint32),
    ('height', ctypes.c_uint32),
    ('depth', ctypes.c_uint32),
    ('min_mipmap_level', ctypes.c_uint32),
    ('max_mipmap_level', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('format', hipArray_Format),
    ('num_channels', ctypes.c_uint32),
]

hipMipmappedArray = struct_hipMipmappedArray
hipMipmappedArray_t = ctypes.POINTER(struct_hipMipmappedArray)
hipmipmappedArray = ctypes.POINTER(struct_hipMipmappedArray)
hipMipmappedArray_const_t = ctypes.POINTER(struct_hipMipmappedArray)

# values for enumeration 'hipResourceType'
hipResourceType__enumvalues = {
    0: 'hipResourceTypeArray',
    1: 'hipResourceTypeMipmappedArray',
    2: 'hipResourceTypeLinear',
    3: 'hipResourceTypePitch2D',
}
hipResourceTypeArray = 0
hipResourceTypeMipmappedArray = 1
hipResourceTypeLinear = 2
hipResourceTypePitch2D = 3
hipResourceType = ctypes.c_uint32 # enum

# values for enumeration 'HIPresourcetype_enum'
HIPresourcetype_enum__enumvalues = {
    0: 'HIP_RESOURCE_TYPE_ARRAY',
    1: 'HIP_RESOURCE_TYPE_MIPMAPPED_ARRAY',
    2: 'HIP_RESOURCE_TYPE_LINEAR',
    3: 'HIP_RESOURCE_TYPE_PITCH2D',
}
HIP_RESOURCE_TYPE_ARRAY = 0
HIP_RESOURCE_TYPE_MIPMAPPED_ARRAY = 1
HIP_RESOURCE_TYPE_LINEAR = 2
HIP_RESOURCE_TYPE_PITCH2D = 3
HIPresourcetype_enum = ctypes.c_uint32 # enum
HIPresourcetype = HIPresourcetype_enum
HIPresourcetype__enumvalues = HIPresourcetype_enum__enumvalues
hipResourcetype = HIPresourcetype_enum
hipResourcetype__enumvalues = HIPresourcetype_enum__enumvalues

# values for enumeration 'HIPaddress_mode_enum'
HIPaddress_mode_enum__enumvalues = {
    0: 'HIP_TR_ADDRESS_MODE_WRAP',
    1: 'HIP_TR_ADDRESS_MODE_CLAMP',
    2: 'HIP_TR_ADDRESS_MODE_MIRROR',
    3: 'HIP_TR_ADDRESS_MODE_BORDER',
}
HIP_TR_ADDRESS_MODE_WRAP = 0
HIP_TR_ADDRESS_MODE_CLAMP = 1
HIP_TR_ADDRESS_MODE_MIRROR = 2
HIP_TR_ADDRESS_MODE_BORDER = 3
HIPaddress_mode_enum = ctypes.c_uint32 # enum
HIPaddress_mode = HIPaddress_mode_enum
HIPaddress_mode__enumvalues = HIPaddress_mode_enum__enumvalues

# values for enumeration 'HIPfilter_mode_enum'
HIPfilter_mode_enum__enumvalues = {
    0: 'HIP_TR_FILTER_MODE_POINT',
    1: 'HIP_TR_FILTER_MODE_LINEAR',
}
HIP_TR_FILTER_MODE_POINT = 0
HIP_TR_FILTER_MODE_LINEAR = 1
HIPfilter_mode_enum = ctypes.c_uint32 # enum
HIPfilter_mode = HIPfilter_mode_enum
HIPfilter_mode__enumvalues = HIPfilter_mode_enum__enumvalues
class struct_HIP_TEXTURE_DESC_st(Structure):
    pass

struct_HIP_TEXTURE_DESC_st._pack_ = 1 # source:False
struct_HIP_TEXTURE_DESC_st._fields_ = [
    ('addressMode', HIPaddress_mode_enum * 3),
    ('filterMode', HIPfilter_mode),
    ('flags', ctypes.c_uint32),
    ('maxAnisotropy', ctypes.c_uint32),
    ('mipmapFilterMode', HIPfilter_mode),
    ('mipmapLevelBias', ctypes.c_float),
    ('minMipmapLevelClamp', ctypes.c_float),
    ('maxMipmapLevelClamp', ctypes.c_float),
    ('borderColor', ctypes.c_float * 4),
    ('reserved', ctypes.c_int32 * 12),
]

HIP_TEXTURE_DESC = struct_HIP_TEXTURE_DESC_st

# values for enumeration 'hipResourceViewFormat'
hipResourceViewFormat__enumvalues = {
    0: 'hipResViewFormatNone',
    1: 'hipResViewFormatUnsignedChar1',
    2: 'hipResViewFormatUnsignedChar2',
    3: 'hipResViewFormatUnsignedChar4',
    4: 'hipResViewFormatSignedChar1',
    5: 'hipResViewFormatSignedChar2',
    6: 'hipResViewFormatSignedChar4',
    7: 'hipResViewFormatUnsignedShort1',
    8: 'hipResViewFormatUnsignedShort2',
    9: 'hipResViewFormatUnsignedShort4',
    10: 'hipResViewFormatSignedShort1',
    11: 'hipResViewFormatSignedShort2',
    12: 'hipResViewFormatSignedShort4',
    13: 'hipResViewFormatUnsignedInt1',
    14: 'hipResViewFormatUnsignedInt2',
    15: 'hipResViewFormatUnsignedInt4',
    16: 'hipResViewFormatSignedInt1',
    17: 'hipResViewFormatSignedInt2',
    18: 'hipResViewFormatSignedInt4',
    19: 'hipResViewFormatHalf1',
    20: 'hipResViewFormatHalf2',
    21: 'hipResViewFormatHalf4',
    22: 'hipResViewFormatFloat1',
    23: 'hipResViewFormatFloat2',
    24: 'hipResViewFormatFloat4',
    25: 'hipResViewFormatUnsignedBlockCompressed1',
    26: 'hipResViewFormatUnsignedBlockCompressed2',
    27: 'hipResViewFormatUnsignedBlockCompressed3',
    28: 'hipResViewFormatUnsignedBlockCompressed4',
    29: 'hipResViewFormatSignedBlockCompressed4',
    30: 'hipResViewFormatUnsignedBlockCompressed5',
    31: 'hipResViewFormatSignedBlockCompressed5',
    32: 'hipResViewFormatUnsignedBlockCompressed6H',
    33: 'hipResViewFormatSignedBlockCompressed6H',
    34: 'hipResViewFormatUnsignedBlockCompressed7',
}
hipResViewFormatNone = 0
hipResViewFormatUnsignedChar1 = 1
hipResViewFormatUnsignedChar2 = 2
hipResViewFormatUnsignedChar4 = 3
hipResViewFormatSignedChar1 = 4
hipResViewFormatSignedChar2 = 5
hipResViewFormatSignedChar4 = 6
hipResViewFormatUnsignedShort1 = 7
hipResViewFormatUnsignedShort2 = 8
hipResViewFormatUnsignedShort4 = 9
hipResViewFormatSignedShort1 = 10
hipResViewFormatSignedShort2 = 11
hipResViewFormatSignedShort4 = 12
hipResViewFormatUnsignedInt1 = 13
hipResViewFormatUnsignedInt2 = 14
hipResViewFormatUnsignedInt4 = 15
hipResViewFormatSignedInt1 = 16
hipResViewFormatSignedInt2 = 17
hipResViewFormatSignedInt4 = 18
hipResViewFormatHalf1 = 19
hipResViewFormatHalf2 = 20
hipResViewFormatHalf4 = 21
hipResViewFormatFloat1 = 22
hipResViewFormatFloat2 = 23
hipResViewFormatFloat4 = 24
hipResViewFormatUnsignedBlockCompressed1 = 25
hipResViewFormatUnsignedBlockCompressed2 = 26
hipResViewFormatUnsignedBlockCompressed3 = 27
hipResViewFormatUnsignedBlockCompressed4 = 28
hipResViewFormatSignedBlockCompressed4 = 29
hipResViewFormatUnsignedBlockCompressed5 = 30
hipResViewFormatSignedBlockCompressed5 = 31
hipResViewFormatUnsignedBlockCompressed6H = 32
hipResViewFormatSignedBlockCompressed6H = 33
hipResViewFormatUnsignedBlockCompressed7 = 34
hipResourceViewFormat = ctypes.c_uint32 # enum

# values for enumeration 'HIPresourceViewFormat_enum'
HIPresourceViewFormat_enum__enumvalues = {
    0: 'HIP_RES_VIEW_FORMAT_NONE',
    1: 'HIP_RES_VIEW_FORMAT_UINT_1X8',
    2: 'HIP_RES_VIEW_FORMAT_UINT_2X8',
    3: 'HIP_RES_VIEW_FORMAT_UINT_4X8',
    4: 'HIP_RES_VIEW_FORMAT_SINT_1X8',
    5: 'HIP_RES_VIEW_FORMAT_SINT_2X8',
    6: 'HIP_RES_VIEW_FORMAT_SINT_4X8',
    7: 'HIP_RES_VIEW_FORMAT_UINT_1X16',
    8: 'HIP_RES_VIEW_FORMAT_UINT_2X16',
    9: 'HIP_RES_VIEW_FORMAT_UINT_4X16',
    10: 'HIP_RES_VIEW_FORMAT_SINT_1X16',
    11: 'HIP_RES_VIEW_FORMAT_SINT_2X16',
    12: 'HIP_RES_VIEW_FORMAT_SINT_4X16',
    13: 'HIP_RES_VIEW_FORMAT_UINT_1X32',
    14: 'HIP_RES_VIEW_FORMAT_UINT_2X32',
    15: 'HIP_RES_VIEW_FORMAT_UINT_4X32',
    16: 'HIP_RES_VIEW_FORMAT_SINT_1X32',
    17: 'HIP_RES_VIEW_FORMAT_SINT_2X32',
    18: 'HIP_RES_VIEW_FORMAT_SINT_4X32',
    19: 'HIP_RES_VIEW_FORMAT_FLOAT_1X16',
    20: 'HIP_RES_VIEW_FORMAT_FLOAT_2X16',
    21: 'HIP_RES_VIEW_FORMAT_FLOAT_4X16',
    22: 'HIP_RES_VIEW_FORMAT_FLOAT_1X32',
    23: 'HIP_RES_VIEW_FORMAT_FLOAT_2X32',
    24: 'HIP_RES_VIEW_FORMAT_FLOAT_4X32',
    25: 'HIP_RES_VIEW_FORMAT_UNSIGNED_BC1',
    26: 'HIP_RES_VIEW_FORMAT_UNSIGNED_BC2',
    27: 'HIP_RES_VIEW_FORMAT_UNSIGNED_BC3',
    28: 'HIP_RES_VIEW_FORMAT_UNSIGNED_BC4',
    29: 'HIP_RES_VIEW_FORMAT_SIGNED_BC4',
    30: 'HIP_RES_VIEW_FORMAT_UNSIGNED_BC5',
    31: 'HIP_RES_VIEW_FORMAT_SIGNED_BC5',
    32: 'HIP_RES_VIEW_FORMAT_UNSIGNED_BC6H',
    33: 'HIP_RES_VIEW_FORMAT_SIGNED_BC6H',
    34: 'HIP_RES_VIEW_FORMAT_UNSIGNED_BC7',
}
HIP_RES_VIEW_FORMAT_NONE = 0
HIP_RES_VIEW_FORMAT_UINT_1X8 = 1
HIP_RES_VIEW_FORMAT_UINT_2X8 = 2
HIP_RES_VIEW_FORMAT_UINT_4X8 = 3
HIP_RES_VIEW_FORMAT_SINT_1X8 = 4
HIP_RES_VIEW_FORMAT_SINT_2X8 = 5
HIP_RES_VIEW_FORMAT_SINT_4X8 = 6
HIP_RES_VIEW_FORMAT_UINT_1X16 = 7
HIP_RES_VIEW_FORMAT_UINT_2X16 = 8
HIP_RES_VIEW_FORMAT_UINT_4X16 = 9
HIP_RES_VIEW_FORMAT_SINT_1X16 = 10
HIP_RES_VIEW_FORMAT_SINT_2X16 = 11
HIP_RES_VIEW_FORMAT_SINT_4X16 = 12
HIP_RES_VIEW_FORMAT_UINT_1X32 = 13
HIP_RES_VIEW_FORMAT_UINT_2X32 = 14
HIP_RES_VIEW_FORMAT_UINT_4X32 = 15
HIP_RES_VIEW_FORMAT_SINT_1X32 = 16
HIP_RES_VIEW_FORMAT_SINT_2X32 = 17
HIP_RES_VIEW_FORMAT_SINT_4X32 = 18
HIP_RES_VIEW_FORMAT_FLOAT_1X16 = 19
HIP_RES_VIEW_FORMAT_FLOAT_2X16 = 20
HIP_RES_VIEW_FORMAT_FLOAT_4X16 = 21
HIP_RES_VIEW_FORMAT_FLOAT_1X32 = 22
HIP_RES_VIEW_FORMAT_FLOAT_2X32 = 23
HIP_RES_VIEW_FORMAT_FLOAT_4X32 = 24
HIP_RES_VIEW_FORMAT_UNSIGNED_BC1 = 25
HIP_RES_VIEW_FORMAT_UNSIGNED_BC2 = 26
HIP_RES_VIEW_FORMAT_UNSIGNED_BC3 = 27
HIP_RES_VIEW_FORMAT_UNSIGNED_BC4 = 28
HIP_RES_VIEW_FORMAT_SIGNED_BC4 = 29
HIP_RES_VIEW_FORMAT_UNSIGNED_BC5 = 30
HIP_RES_VIEW_FORMAT_SIGNED_BC5 = 31
HIP_RES_VIEW_FORMAT_UNSIGNED_BC6H = 32
HIP_RES_VIEW_FORMAT_SIGNED_BC6H = 33
HIP_RES_VIEW_FORMAT_UNSIGNED_BC7 = 34
HIPresourceViewFormat_enum = ctypes.c_uint32 # enum
HIPresourceViewFormat = HIPresourceViewFormat_enum
HIPresourceViewFormat__enumvalues = HIPresourceViewFormat_enum__enumvalues
class struct_hipResourceDesc(Structure):
    pass

class union_hipResourceDesc_res(Union):
    pass

class struct_hipResourceDesc_0_array(Structure):
    pass

struct_hipResourceDesc_0_array._pack_ = 1 # source:False
struct_hipResourceDesc_0_array._fields_ = [
    ('array', ctypes.POINTER(struct_hipArray)),
]

class struct_hipResourceDesc_0_mipmap(Structure):
    pass

struct_hipResourceDesc_0_mipmap._pack_ = 1 # source:False
struct_hipResourceDesc_0_mipmap._fields_ = [
    ('mipmap', ctypes.POINTER(struct_hipMipmappedArray)),
]

class struct_hipResourceDesc_0_linear(Structure):
    pass

struct_hipResourceDesc_0_linear._pack_ = 1 # source:False
struct_hipResourceDesc_0_linear._fields_ = [
    ('devPtr', ctypes.POINTER(None)),
    ('desc', struct_hipChannelFormatDesc),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('sizeInBytes', ctypes.c_uint64),
]

class struct_hipResourceDesc_0_pitch2D(Structure):
    pass

struct_hipResourceDesc_0_pitch2D._pack_ = 1 # source:False
struct_hipResourceDesc_0_pitch2D._fields_ = [
    ('devPtr', ctypes.POINTER(None)),
    ('desc', struct_hipChannelFormatDesc),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('width', ctypes.c_uint64),
    ('height', ctypes.c_uint64),
    ('pitchInBytes', ctypes.c_uint64),
]

union_hipResourceDesc_res._pack_ = 1 # source:False
union_hipResourceDesc_res._fields_ = [
    ('array', struct_hipResourceDesc_0_array),
    ('mipmap', struct_hipResourceDesc_0_mipmap),
    ('linear', struct_hipResourceDesc_0_linear),
    ('pitch2D', struct_hipResourceDesc_0_pitch2D),
]

struct_hipResourceDesc._pack_ = 1 # source:False
struct_hipResourceDesc._fields_ = [
    ('resType', hipResourceType),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('res', union_hipResourceDesc_res),
]

hipResourceDesc = struct_hipResourceDesc
class struct_HIP_RESOURCE_DESC_st(Structure):
    pass

class union_HIP_RESOURCE_DESC_st_res(Union):
    pass

class struct_HIP_RESOURCE_DESC_st_0_array(Structure):
    pass

struct_HIP_RESOURCE_DESC_st_0_array._pack_ = 1 # source:False
struct_HIP_RESOURCE_DESC_st_0_array._fields_ = [
    ('hArray', ctypes.POINTER(struct_hipArray)),
]

class struct_HIP_RESOURCE_DESC_st_0_mipmap(Structure):
    pass

struct_HIP_RESOURCE_DESC_st_0_mipmap._pack_ = 1 # source:False
struct_HIP_RESOURCE_DESC_st_0_mipmap._fields_ = [
    ('hMipmappedArray', ctypes.POINTER(struct_hipMipmappedArray)),
]

class struct_HIP_RESOURCE_DESC_st_0_linear(Structure):
    pass

struct_HIP_RESOURCE_DESC_st_0_linear._pack_ = 1 # source:False
struct_HIP_RESOURCE_DESC_st_0_linear._fields_ = [
    ('devPtr', ctypes.POINTER(None)),
    ('format', hipArray_Format),
    ('numChannels', ctypes.c_uint32),
    ('sizeInBytes', ctypes.c_uint64),
]

class struct_HIP_RESOURCE_DESC_st_0_pitch2D(Structure):
    pass

struct_HIP_RESOURCE_DESC_st_0_pitch2D._pack_ = 1 # source:False
struct_HIP_RESOURCE_DESC_st_0_pitch2D._fields_ = [
    ('devPtr', ctypes.POINTER(None)),
    ('format', hipArray_Format),
    ('numChannels', ctypes.c_uint32),
    ('width', ctypes.c_uint64),
    ('height', ctypes.c_uint64),
    ('pitchInBytes', ctypes.c_uint64),
]

class struct_HIP_RESOURCE_DESC_st_0_reserved(Structure):
    pass

struct_HIP_RESOURCE_DESC_st_0_reserved._pack_ = 1 # source:False
struct_HIP_RESOURCE_DESC_st_0_reserved._fields_ = [
    ('reserved', ctypes.c_int32 * 32),
]

union_HIP_RESOURCE_DESC_st_res._pack_ = 1 # source:False
union_HIP_RESOURCE_DESC_st_res._fields_ = [
    ('array', struct_HIP_RESOURCE_DESC_st_0_array),
    ('mipmap', struct_HIP_RESOURCE_DESC_st_0_mipmap),
    ('linear', struct_HIP_RESOURCE_DESC_st_0_linear),
    ('pitch2D', struct_HIP_RESOURCE_DESC_st_0_pitch2D),
    ('reserved', struct_HIP_RESOURCE_DESC_st_0_reserved),
]

struct_HIP_RESOURCE_DESC_st._pack_ = 1 # source:False
struct_HIP_RESOURCE_DESC_st._fields_ = [
    ('resType', HIPresourcetype),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('res', union_HIP_RESOURCE_DESC_st_res),
    ('flags', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

HIP_RESOURCE_DESC = struct_HIP_RESOURCE_DESC_st
class struct_hipResourceViewDesc(Structure):
    pass

struct_hipResourceViewDesc._pack_ = 1 # source:False
struct_hipResourceViewDesc._fields_ = [
    ('format', hipResourceViewFormat),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('width', ctypes.c_uint64),
    ('height', ctypes.c_uint64),
    ('depth', ctypes.c_uint64),
    ('firstMipmapLevel', ctypes.c_uint32),
    ('lastMipmapLevel', ctypes.c_uint32),
    ('firstLayer', ctypes.c_uint32),
    ('lastLayer', ctypes.c_uint32),
]

class struct_HIP_RESOURCE_VIEW_DESC_st(Structure):
    pass

struct_HIP_RESOURCE_VIEW_DESC_st._pack_ = 1 # source:False
struct_HIP_RESOURCE_VIEW_DESC_st._fields_ = [
    ('format', HIPresourceViewFormat),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('width', ctypes.c_uint64),
    ('height', ctypes.c_uint64),
    ('depth', ctypes.c_uint64),
    ('firstMipmapLevel', ctypes.c_uint32),
    ('lastMipmapLevel', ctypes.c_uint32),
    ('firstLayer', ctypes.c_uint32),
    ('lastLayer', ctypes.c_uint32),
    ('reserved', ctypes.c_uint32 * 16),
]

HIP_RESOURCE_VIEW_DESC = struct_HIP_RESOURCE_VIEW_DESC_st

# values for enumeration 'hipMemcpyKind'
hipMemcpyKind__enumvalues = {
    0: 'hipMemcpyHostToHost',
    1: 'hipMemcpyHostToDevice',
    2: 'hipMemcpyDeviceToHost',
    3: 'hipMemcpyDeviceToDevice',
    4: 'hipMemcpyDefault',
}
hipMemcpyHostToHost = 0
hipMemcpyHostToDevice = 1
hipMemcpyDeviceToHost = 2
hipMemcpyDeviceToDevice = 3
hipMemcpyDefault = 4
hipMemcpyKind = ctypes.c_uint32 # enum
class struct_hipPitchedPtr(Structure):
    pass

struct_hipPitchedPtr._pack_ = 1 # source:False
struct_hipPitchedPtr._fields_ = [
    ('ptr', ctypes.POINTER(None)),
    ('pitch', ctypes.c_uint64),
    ('xsize', ctypes.c_uint64),
    ('ysize', ctypes.c_uint64),
]

hipPitchedPtr = struct_hipPitchedPtr
class struct_hipExtent(Structure):
    pass

struct_hipExtent._pack_ = 1 # source:False
struct_hipExtent._fields_ = [
    ('width', ctypes.c_uint64),
    ('height', ctypes.c_uint64),
    ('depth', ctypes.c_uint64),
]

hipExtent = struct_hipExtent
class struct_hipPos(Structure):
    pass

struct_hipPos._pack_ = 1 # source:False
struct_hipPos._fields_ = [
    ('x', ctypes.c_uint64),
    ('y', ctypes.c_uint64),
    ('z', ctypes.c_uint64),
]

hipPos = struct_hipPos
class struct_hipMemcpy3DParms(Structure):
    pass

struct_hipMemcpy3DParms._pack_ = 1 # source:False
struct_hipMemcpy3DParms._fields_ = [
    ('srcArray', ctypes.POINTER(struct_hipArray)),
    ('srcPos', struct_hipPos),
    ('srcPtr', struct_hipPitchedPtr),
    ('dstArray', ctypes.POINTER(struct_hipArray)),
    ('dstPos', struct_hipPos),
    ('dstPtr', struct_hipPitchedPtr),
    ('extent', struct_hipExtent),
    ('kind', hipMemcpyKind),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

hipMemcpy3DParms = struct_hipMemcpy3DParms
class struct_HIP_MEMCPY3D(Structure):
    pass

struct_HIP_MEMCPY3D._pack_ = 1 # source:False
struct_HIP_MEMCPY3D._fields_ = [
    ('srcXInBytes', ctypes.c_uint32),
    ('srcY', ctypes.c_uint32),
    ('srcZ', ctypes.c_uint32),
    ('srcLOD', ctypes.c_uint32),
    ('srcMemoryType', hipMemoryType),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('srcHost', ctypes.POINTER(None)),
    ('srcDevice', ctypes.POINTER(None)),
    ('srcArray', ctypes.POINTER(struct_hipArray)),
    ('srcPitch', ctypes.c_uint32),
    ('srcHeight', ctypes.c_uint32),
    ('dstXInBytes', ctypes.c_uint32),
    ('dstY', ctypes.c_uint32),
    ('dstZ', ctypes.c_uint32),
    ('dstLOD', ctypes.c_uint32),
    ('dstMemoryType', hipMemoryType),
    ('PADDING_1', ctypes.c_ubyte * 4),
    ('dstHost', ctypes.POINTER(None)),
    ('dstDevice', ctypes.POINTER(None)),
    ('dstArray', ctypes.POINTER(struct_hipArray)),
    ('dstPitch', ctypes.c_uint32),
    ('dstHeight', ctypes.c_uint32),
    ('WidthInBytes', ctypes.c_uint32),
    ('Height', ctypes.c_uint32),
    ('Depth', ctypes.c_uint32),
    ('PADDING_2', ctypes.c_ubyte * 4),
]

HIP_MEMCPY3D = struct_HIP_MEMCPY3D
try:
    make_hipPitchedPtr = _libraries['FIXME_STUB'].make_hipPitchedPtr
    make_hipPitchedPtr.restype = struct_hipPitchedPtr
    make_hipPitchedPtr.argtypes = [ctypes.POINTER(None), size_t, size_t, size_t]
except AttributeError:
    pass
try:
    make_hipPos = _libraries['FIXME_STUB'].make_hipPos
    make_hipPos.restype = struct_hipPos
    make_hipPos.argtypes = [size_t, size_t, size_t]
except AttributeError:
    pass
try:
    make_hipExtent = _libraries['FIXME_STUB'].make_hipExtent
    make_hipExtent.restype = struct_hipExtent
    make_hipExtent.argtypes = [size_t, size_t, size_t]
except AttributeError:
    pass

# values for enumeration 'hipFunction_attribute'
hipFunction_attribute__enumvalues = {
    0: 'HIP_FUNC_ATTRIBUTE_MAX_THREADS_PER_BLOCK',
    1: 'HIP_FUNC_ATTRIBUTE_SHARED_SIZE_BYTES',
    2: 'HIP_FUNC_ATTRIBUTE_CONST_SIZE_BYTES',
    3: 'HIP_FUNC_ATTRIBUTE_LOCAL_SIZE_BYTES',
    4: 'HIP_FUNC_ATTRIBUTE_NUM_REGS',
    5: 'HIP_FUNC_ATTRIBUTE_PTX_VERSION',
    6: 'HIP_FUNC_ATTRIBUTE_BINARY_VERSION',
    7: 'HIP_FUNC_ATTRIBUTE_CACHE_MODE_CA',
    8: 'HIP_FUNC_ATTRIBUTE_MAX_DYNAMIC_SHARED_SIZE_BYTES',
    9: 'HIP_FUNC_ATTRIBUTE_PREFERRED_SHARED_MEMORY_CARVEOUT',
    10: 'HIP_FUNC_ATTRIBUTE_MAX',
}
HIP_FUNC_ATTRIBUTE_MAX_THREADS_PER_BLOCK = 0
HIP_FUNC_ATTRIBUTE_SHARED_SIZE_BYTES = 1
HIP_FUNC_ATTRIBUTE_CONST_SIZE_BYTES = 2
HIP_FUNC_ATTRIBUTE_LOCAL_SIZE_BYTES = 3
HIP_FUNC_ATTRIBUTE_NUM_REGS = 4
HIP_FUNC_ATTRIBUTE_PTX_VERSION = 5
HIP_FUNC_ATTRIBUTE_BINARY_VERSION = 6
HIP_FUNC_ATTRIBUTE_CACHE_MODE_CA = 7
HIP_FUNC_ATTRIBUTE_MAX_DYNAMIC_SHARED_SIZE_BYTES = 8
HIP_FUNC_ATTRIBUTE_PREFERRED_SHARED_MEMORY_CARVEOUT = 9
HIP_FUNC_ATTRIBUTE_MAX = 10
hipFunction_attribute = ctypes.c_uint32 # enum

# values for enumeration 'hipPointer_attribute'
hipPointer_attribute__enumvalues = {
    1: 'HIP_POINTER_ATTRIBUTE_CONTEXT',
    2: 'HIP_POINTER_ATTRIBUTE_MEMORY_TYPE',
    3: 'HIP_POINTER_ATTRIBUTE_DEVICE_POINTER',
    4: 'HIP_POINTER_ATTRIBUTE_HOST_POINTER',
    5: 'HIP_POINTER_ATTRIBUTE_P2P_TOKENS',
    6: 'HIP_POINTER_ATTRIBUTE_SYNC_MEMOPS',
    7: 'HIP_POINTER_ATTRIBUTE_BUFFER_ID',
    8: 'HIP_POINTER_ATTRIBUTE_IS_MANAGED',
    9: 'HIP_POINTER_ATTRIBUTE_DEVICE_ORDINAL',
    10: 'HIP_POINTER_ATTRIBUTE_IS_LEGACY_HIP_IPC_CAPABLE',
    11: 'HIP_POINTER_ATTRIBUTE_RANGE_START_ADDR',
    12: 'HIP_POINTER_ATTRIBUTE_RANGE_SIZE',
    13: 'HIP_POINTER_ATTRIBUTE_MAPPED',
    14: 'HIP_POINTER_ATTRIBUTE_ALLOWED_HANDLE_TYPES',
    15: 'HIP_POINTER_ATTRIBUTE_IS_GPU_DIRECT_RDMA_CAPABLE',
    16: 'HIP_POINTER_ATTRIBUTE_ACCESS_FLAGS',
    17: 'HIP_POINTER_ATTRIBUTE_MEMPOOL_HANDLE',
}
HIP_POINTER_ATTRIBUTE_CONTEXT = 1
HIP_POINTER_ATTRIBUTE_MEMORY_TYPE = 2
HIP_POINTER_ATTRIBUTE_DEVICE_POINTER = 3
HIP_POINTER_ATTRIBUTE_HOST_POINTER = 4
HIP_POINTER_ATTRIBUTE_P2P_TOKENS = 5
HIP_POINTER_ATTRIBUTE_SYNC_MEMOPS = 6
HIP_POINTER_ATTRIBUTE_BUFFER_ID = 7
HIP_POINTER_ATTRIBUTE_IS_MANAGED = 8
HIP_POINTER_ATTRIBUTE_DEVICE_ORDINAL = 9
HIP_POINTER_ATTRIBUTE_IS_LEGACY_HIP_IPC_CAPABLE = 10
HIP_POINTER_ATTRIBUTE_RANGE_START_ADDR = 11
HIP_POINTER_ATTRIBUTE_RANGE_SIZE = 12
HIP_POINTER_ATTRIBUTE_MAPPED = 13
HIP_POINTER_ATTRIBUTE_ALLOWED_HANDLE_TYPES = 14
HIP_POINTER_ATTRIBUTE_IS_GPU_DIRECT_RDMA_CAPABLE = 15
HIP_POINTER_ATTRIBUTE_ACCESS_FLAGS = 16
HIP_POINTER_ATTRIBUTE_MEMPOOL_HANDLE = 17
hipPointer_attribute = ctypes.c_uint32 # enum
class struct_ihipCtx_t(Structure):
    pass

hipCtx_t = ctypes.POINTER(struct_ihipCtx_t)
hipDevice_t = ctypes.c_int32

# values for enumeration 'hipDeviceP2PAttr'
hipDeviceP2PAttr__enumvalues = {
    0: 'hipDevP2PAttrPerformanceRank',
    1: 'hipDevP2PAttrAccessSupported',
    2: 'hipDevP2PAttrNativeAtomicSupported',
    3: 'hipDevP2PAttrHipArrayAccessSupported',
}
hipDevP2PAttrPerformanceRank = 0
hipDevP2PAttrAccessSupported = 1
hipDevP2PAttrNativeAtomicSupported = 2
hipDevP2PAttrHipArrayAccessSupported = 3
hipDeviceP2PAttr = ctypes.c_uint32 # enum
class struct_ihipStream_t(Structure):
    pass

hipStream_t = ctypes.POINTER(struct_ihipStream_t)
class struct_hipIpcMemHandle_st(Structure):
    pass

struct_hipIpcMemHandle_st._pack_ = 1 # source:False
struct_hipIpcMemHandle_st._fields_ = [
    ('reserved', ctypes.c_char * 64),
]

hipIpcMemHandle_t = struct_hipIpcMemHandle_st
class struct_hipIpcEventHandle_st(Structure):
    pass

struct_hipIpcEventHandle_st._pack_ = 1 # source:False
struct_hipIpcEventHandle_st._fields_ = [
    ('reserved', ctypes.c_char * 64),
]

hipIpcEventHandle_t = struct_hipIpcEventHandle_st
class struct_ihipModule_t(Structure):
    pass

hipModule_t = ctypes.POINTER(struct_ihipModule_t)
class struct_ihipModuleSymbol_t(Structure):
    pass

hipFunction_t = ctypes.POINTER(struct_ihipModuleSymbol_t)
class struct_ihipMemPoolHandle_t(Structure):
    pass

hipMemPool_t = ctypes.POINTER(struct_ihipMemPoolHandle_t)
class struct_hipFuncAttributes(Structure):
    pass

struct_hipFuncAttributes._pack_ = 1 # source:False
struct_hipFuncAttributes._fields_ = [
    ('binaryVersion', ctypes.c_int32),
    ('cacheModeCA', ctypes.c_int32),
    ('constSizeBytes', ctypes.c_uint64),
    ('localSizeBytes', ctypes.c_uint64),
    ('maxDynamicSharedSizeBytes', ctypes.c_int32),
    ('maxThreadsPerBlock', ctypes.c_int32),
    ('numRegs', ctypes.c_int32),
    ('preferredShmemCarveout', ctypes.c_int32),
    ('ptxVersion', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('sharedSizeBytes', ctypes.c_uint64),
]

hipFuncAttributes = struct_hipFuncAttributes
class struct_ihipEvent_t(Structure):
    pass

hipEvent_t = ctypes.POINTER(struct_ihipEvent_t)

# values for enumeration 'hipLimit_t'
hipLimit_t__enumvalues = {
    0: 'hipLimitStackSize',
    1: 'hipLimitPrintfFifoSize',
    2: 'hipLimitMallocHeapSize',
    3: 'hipLimitRange',
}
hipLimitStackSize = 0
hipLimitPrintfFifoSize = 1
hipLimitMallocHeapSize = 2
hipLimitRange = 3
hipLimit_t = ctypes.c_uint32 # enum

# values for enumeration 'hipMemoryAdvise'
hipMemoryAdvise__enumvalues = {
    1: 'hipMemAdviseSetReadMostly',
    2: 'hipMemAdviseUnsetReadMostly',
    3: 'hipMemAdviseSetPreferredLocation',
    4: 'hipMemAdviseUnsetPreferredLocation',
    5: 'hipMemAdviseSetAccessedBy',
    6: 'hipMemAdviseUnsetAccessedBy',
    100: 'hipMemAdviseSetCoarseGrain',
    101: 'hipMemAdviseUnsetCoarseGrain',
}
hipMemAdviseSetReadMostly = 1
hipMemAdviseUnsetReadMostly = 2
hipMemAdviseSetPreferredLocation = 3
hipMemAdviseUnsetPreferredLocation = 4
hipMemAdviseSetAccessedBy = 5
hipMemAdviseUnsetAccessedBy = 6
hipMemAdviseSetCoarseGrain = 100
hipMemAdviseUnsetCoarseGrain = 101
hipMemoryAdvise = ctypes.c_uint32 # enum

# values for enumeration 'hipMemRangeCoherencyMode'
hipMemRangeCoherencyMode__enumvalues = {
    0: 'hipMemRangeCoherencyModeFineGrain',
    1: 'hipMemRangeCoherencyModeCoarseGrain',
    2: 'hipMemRangeCoherencyModeIndeterminate',
}
hipMemRangeCoherencyModeFineGrain = 0
hipMemRangeCoherencyModeCoarseGrain = 1
hipMemRangeCoherencyModeIndeterminate = 2
hipMemRangeCoherencyMode = ctypes.c_uint32 # enum

# values for enumeration 'hipMemRangeAttribute'
hipMemRangeAttribute__enumvalues = {
    1: 'hipMemRangeAttributeReadMostly',
    2: 'hipMemRangeAttributePreferredLocation',
    3: 'hipMemRangeAttributeAccessedBy',
    4: 'hipMemRangeAttributeLastPrefetchLocation',
    100: 'hipMemRangeAttributeCoherencyMode',
}
hipMemRangeAttributeReadMostly = 1
hipMemRangeAttributePreferredLocation = 2
hipMemRangeAttributeAccessedBy = 3
hipMemRangeAttributeLastPrefetchLocation = 4
hipMemRangeAttributeCoherencyMode = 100
hipMemRangeAttribute = ctypes.c_uint32 # enum

# values for enumeration 'hipMemPoolAttr'
hipMemPoolAttr__enumvalues = {
    1: 'hipMemPoolReuseFollowEventDependencies',
    2: 'hipMemPoolReuseAllowOpportunistic',
    3: 'hipMemPoolReuseAllowInternalDependencies',
    4: 'hipMemPoolAttrReleaseThreshold',
    5: 'hipMemPoolAttrReservedMemCurrent',
    6: 'hipMemPoolAttrReservedMemHigh',
    7: 'hipMemPoolAttrUsedMemCurrent',
    8: 'hipMemPoolAttrUsedMemHigh',
}
hipMemPoolReuseFollowEventDependencies = 1
hipMemPoolReuseAllowOpportunistic = 2
hipMemPoolReuseAllowInternalDependencies = 3
hipMemPoolAttrReleaseThreshold = 4
hipMemPoolAttrReservedMemCurrent = 5
hipMemPoolAttrReservedMemHigh = 6
hipMemPoolAttrUsedMemCurrent = 7
hipMemPoolAttrUsedMemHigh = 8
hipMemPoolAttr = ctypes.c_uint32 # enum

# values for enumeration 'hipMemLocationType'
hipMemLocationType__enumvalues = {
    0: 'hipMemLocationTypeInvalid',
    1: 'hipMemLocationTypeDevice',
}
hipMemLocationTypeInvalid = 0
hipMemLocationTypeDevice = 1
hipMemLocationType = ctypes.c_uint32 # enum
class struct_hipMemLocation(Structure):
    pass

struct_hipMemLocation._pack_ = 1 # source:False
struct_hipMemLocation._fields_ = [
    ('type', hipMemLocationType),
    ('id', ctypes.c_int32),
]

hipMemLocation = struct_hipMemLocation

# values for enumeration 'hipMemAccessFlags'
hipMemAccessFlags__enumvalues = {
    0: 'hipMemAccessFlagsProtNone',
    1: 'hipMemAccessFlagsProtRead',
    3: 'hipMemAccessFlagsProtReadWrite',
}
hipMemAccessFlagsProtNone = 0
hipMemAccessFlagsProtRead = 1
hipMemAccessFlagsProtReadWrite = 3
hipMemAccessFlags = ctypes.c_uint32 # enum
class struct_hipMemAccessDesc(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('location', hipMemLocation),
    ('flags', hipMemAccessFlags),
     ]

hipMemAccessDesc = struct_hipMemAccessDesc

# values for enumeration 'hipMemAllocationType'
hipMemAllocationType__enumvalues = {
    0: 'hipMemAllocationTypeInvalid',
    1: 'hipMemAllocationTypePinned',
    2147483647: 'hipMemAllocationTypeMax',
}
hipMemAllocationTypeInvalid = 0
hipMemAllocationTypePinned = 1
hipMemAllocationTypeMax = 2147483647
hipMemAllocationType = ctypes.c_uint32 # enum

# values for enumeration 'hipMemAllocationHandleType'
hipMemAllocationHandleType__enumvalues = {
    0: 'hipMemHandleTypeNone',
    1: 'hipMemHandleTypePosixFileDescriptor',
    2: 'hipMemHandleTypeWin32',
    4: 'hipMemHandleTypeWin32Kmt',
}
hipMemHandleTypeNone = 0
hipMemHandleTypePosixFileDescriptor = 1
hipMemHandleTypeWin32 = 2
hipMemHandleTypeWin32Kmt = 4
hipMemAllocationHandleType = ctypes.c_uint32 # enum
class struct_hipMemPoolProps(Structure):
    pass

struct_hipMemPoolProps._pack_ = 1 # source:False
struct_hipMemPoolProps._fields_ = [
    ('allocType', hipMemAllocationType),
    ('handleTypes', hipMemAllocationHandleType),
    ('location', hipMemLocation),
    ('win32SecurityAttributes', ctypes.POINTER(None)),
    ('reserved', ctypes.c_ubyte * 64),
]

hipMemPoolProps = struct_hipMemPoolProps
class struct_hipMemPoolPtrExportData(Structure):
    pass

struct_hipMemPoolPtrExportData._pack_ = 1 # source:False
struct_hipMemPoolPtrExportData._fields_ = [
    ('reserved', ctypes.c_ubyte * 64),
]

hipMemPoolPtrExportData = struct_hipMemPoolPtrExportData

# values for enumeration 'hipJitOption'
hipJitOption__enumvalues = {
    0: 'hipJitOptionMaxRegisters',
    1: 'hipJitOptionThreadsPerBlock',
    2: 'hipJitOptionWallTime',
    3: 'hipJitOptionInfoLogBuffer',
    4: 'hipJitOptionInfoLogBufferSizeBytes',
    5: 'hipJitOptionErrorLogBuffer',
    6: 'hipJitOptionErrorLogBufferSizeBytes',
    7: 'hipJitOptionOptimizationLevel',
    8: 'hipJitOptionTargetFromContext',
    9: 'hipJitOptionTarget',
    10: 'hipJitOptionFallbackStrategy',
    11: 'hipJitOptionGenerateDebugInfo',
    12: 'hipJitOptionLogVerbose',
    13: 'hipJitOptionGenerateLineInfo',
    14: 'hipJitOptionCacheMode',
    15: 'hipJitOptionSm3xOpt',
    16: 'hipJitOptionFastCompile',
    17: 'hipJitOptionNumOptions',
}
hipJitOptionMaxRegisters = 0
hipJitOptionThreadsPerBlock = 1
hipJitOptionWallTime = 2
hipJitOptionInfoLogBuffer = 3
hipJitOptionInfoLogBufferSizeBytes = 4
hipJitOptionErrorLogBuffer = 5
hipJitOptionErrorLogBufferSizeBytes = 6
hipJitOptionOptimizationLevel = 7
hipJitOptionTargetFromContext = 8
hipJitOptionTarget = 9
hipJitOptionFallbackStrategy = 10
hipJitOptionGenerateDebugInfo = 11
hipJitOptionLogVerbose = 12
hipJitOptionGenerateLineInfo = 13
hipJitOptionCacheMode = 14
hipJitOptionSm3xOpt = 15
hipJitOptionFastCompile = 16
hipJitOptionNumOptions = 17
hipJitOption = ctypes.c_uint32 # enum

# values for enumeration 'hipFuncAttribute'
hipFuncAttribute__enumvalues = {
    8: 'hipFuncAttributeMaxDynamicSharedMemorySize',
    9: 'hipFuncAttributePreferredSharedMemoryCarveout',
    10: 'hipFuncAttributeMax',
}
hipFuncAttributeMaxDynamicSharedMemorySize = 8
hipFuncAttributePreferredSharedMemoryCarveout = 9
hipFuncAttributeMax = 10
hipFuncAttribute = ctypes.c_uint32 # enum

# values for enumeration 'hipFuncCache_t'
hipFuncCache_t__enumvalues = {
    0: 'hipFuncCachePreferNone',
    1: 'hipFuncCachePreferShared',
    2: 'hipFuncCachePreferL1',
    3: 'hipFuncCachePreferEqual',
}
hipFuncCachePreferNone = 0
hipFuncCachePreferShared = 1
hipFuncCachePreferL1 = 2
hipFuncCachePreferEqual = 3
hipFuncCache_t = ctypes.c_uint32 # enum

# values for enumeration 'hipSharedMemConfig'
hipSharedMemConfig__enumvalues = {
    0: 'hipSharedMemBankSizeDefault',
    1: 'hipSharedMemBankSizeFourByte',
    2: 'hipSharedMemBankSizeEightByte',
}
hipSharedMemBankSizeDefault = 0
hipSharedMemBankSizeFourByte = 1
hipSharedMemBankSizeEightByte = 2
hipSharedMemConfig = ctypes.c_uint32 # enum
class struct_dim3(Structure):
    pass

struct_dim3._pack_ = 1 # source:False
struct_dim3._fields_ = [
    ('x', ctypes.c_uint32),
    ('y', ctypes.c_uint32),
    ('z', ctypes.c_uint32),
]

dim3 = struct_dim3
class struct_hipLaunchParams_t(Structure):
    pass

struct_hipLaunchParams_t._pack_ = 1 # source:False
struct_hipLaunchParams_t._fields_ = [
    ('func', ctypes.POINTER(None)),
    ('gridDim', dim3),
    ('blockDim', dim3),
    ('args', ctypes.POINTER(ctypes.POINTER(None))),
    ('sharedMem', ctypes.c_uint64),
    ('stream', ctypes.POINTER(struct_ihipStream_t)),
]

hipLaunchParams = struct_hipLaunchParams_t
class struct_hipFunctionLaunchParams_t(Structure):
    pass

struct_hipFunctionLaunchParams_t._pack_ = 1 # source:False
struct_hipFunctionLaunchParams_t._fields_ = [
    ('function', ctypes.POINTER(struct_ihipModuleSymbol_t)),
    ('gridDimX', ctypes.c_uint32),
    ('gridDimY', ctypes.c_uint32),
    ('gridDimZ', ctypes.c_uint32),
    ('blockDimX', ctypes.c_uint32),
    ('blockDimY', ctypes.c_uint32),
    ('blockDimZ', ctypes.c_uint32),
    ('sharedMemBytes', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('hStream', ctypes.POINTER(struct_ihipStream_t)),
    ('kernelParams', ctypes.POINTER(ctypes.POINTER(None))),
]

hipFunctionLaunchParams = struct_hipFunctionLaunchParams_t

# values for enumeration 'hipExternalMemoryHandleType_enum'
hipExternalMemoryHandleType_enum__enumvalues = {
    1: 'hipExternalMemoryHandleTypeOpaqueFd',
    2: 'hipExternalMemoryHandleTypeOpaqueWin32',
    3: 'hipExternalMemoryHandleTypeOpaqueWin32Kmt',
    4: 'hipExternalMemoryHandleTypeD3D12Heap',
    5: 'hipExternalMemoryHandleTypeD3D12Resource',
    6: 'hipExternalMemoryHandleTypeD3D11Resource',
    7: 'hipExternalMemoryHandleTypeD3D11ResourceKmt',
}
hipExternalMemoryHandleTypeOpaqueFd = 1
hipExternalMemoryHandleTypeOpaqueWin32 = 2
hipExternalMemoryHandleTypeOpaqueWin32Kmt = 3
hipExternalMemoryHandleTypeD3D12Heap = 4
hipExternalMemoryHandleTypeD3D12Resource = 5
hipExternalMemoryHandleTypeD3D11Resource = 6
hipExternalMemoryHandleTypeD3D11ResourceKmt = 7
hipExternalMemoryHandleType_enum = ctypes.c_uint32 # enum
hipExternalMemoryHandleType = hipExternalMemoryHandleType_enum
hipExternalMemoryHandleType__enumvalues = hipExternalMemoryHandleType_enum__enumvalues
class struct_hipExternalMemoryHandleDesc_st(Structure):
    pass

class union_hipExternalMemoryHandleDesc_st_handle(Union):
    pass

class struct_hipExternalMemoryHandleDesc_st_0_win32(Structure):
    pass

struct_hipExternalMemoryHandleDesc_st_0_win32._pack_ = 1 # source:False
struct_hipExternalMemoryHandleDesc_st_0_win32._fields_ = [
    ('handle', ctypes.POINTER(None)),
    ('name', ctypes.POINTER(None)),
]

union_hipExternalMemoryHandleDesc_st_handle._pack_ = 1 # source:False
union_hipExternalMemoryHandleDesc_st_handle._fields_ = [
    ('fd', ctypes.c_int32),
    ('win32', struct_hipExternalMemoryHandleDesc_st_0_win32),
]

struct_hipExternalMemoryHandleDesc_st._pack_ = 1 # source:False
struct_hipExternalMemoryHandleDesc_st._fields_ = [
    ('type', hipExternalMemoryHandleType),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('handle', union_hipExternalMemoryHandleDesc_st_handle),
    ('size', ctypes.c_uint64),
    ('flags', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

hipExternalMemoryHandleDesc = struct_hipExternalMemoryHandleDesc_st
class struct_hipExternalMemoryBufferDesc_st(Structure):
    pass

struct_hipExternalMemoryBufferDesc_st._pack_ = 1 # source:False
struct_hipExternalMemoryBufferDesc_st._fields_ = [
    ('offset', ctypes.c_uint64),
    ('size', ctypes.c_uint64),
    ('flags', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

hipExternalMemoryBufferDesc = struct_hipExternalMemoryBufferDesc_st
hipExternalMemory_t = ctypes.POINTER(None)

# values for enumeration 'hipExternalSemaphoreHandleType_enum'
hipExternalSemaphoreHandleType_enum__enumvalues = {
    1: 'hipExternalSemaphoreHandleTypeOpaqueFd',
    2: 'hipExternalSemaphoreHandleTypeOpaqueWin32',
    3: 'hipExternalSemaphoreHandleTypeOpaqueWin32Kmt',
    4: 'hipExternalSemaphoreHandleTypeD3D12Fence',
}
hipExternalSemaphoreHandleTypeOpaqueFd = 1
hipExternalSemaphoreHandleTypeOpaqueWin32 = 2
hipExternalSemaphoreHandleTypeOpaqueWin32Kmt = 3
hipExternalSemaphoreHandleTypeD3D12Fence = 4
hipExternalSemaphoreHandleType_enum = ctypes.c_uint32 # enum
hipExternalSemaphoreHandleType = hipExternalSemaphoreHandleType_enum
hipExternalSemaphoreHandleType__enumvalues = hipExternalSemaphoreHandleType_enum__enumvalues
class struct_hipExternalSemaphoreHandleDesc_st(Structure):
    pass

class union_hipExternalSemaphoreHandleDesc_st_handle(Union):
    pass

class struct_hipExternalSemaphoreHandleDesc_st_0_win32(Structure):
    pass

struct_hipExternalSemaphoreHandleDesc_st_0_win32._pack_ = 1 # source:False
struct_hipExternalSemaphoreHandleDesc_st_0_win32._fields_ = [
    ('handle', ctypes.POINTER(None)),
    ('name', ctypes.POINTER(None)),
]

union_hipExternalSemaphoreHandleDesc_st_handle._pack_ = 1 # source:False
union_hipExternalSemaphoreHandleDesc_st_handle._fields_ = [
    ('fd', ctypes.c_int32),
    ('win32', struct_hipExternalSemaphoreHandleDesc_st_0_win32),
]

struct_hipExternalSemaphoreHandleDesc_st._pack_ = 1 # source:False
struct_hipExternalSemaphoreHandleDesc_st._fields_ = [
    ('type', hipExternalSemaphoreHandleType),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('handle', union_hipExternalSemaphoreHandleDesc_st_handle),
    ('flags', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

hipExternalSemaphoreHandleDesc = struct_hipExternalSemaphoreHandleDesc_st
hipExternalSemaphore_t = ctypes.POINTER(None)
class struct_hipExternalSemaphoreSignalParams_st(Structure):
    pass

class struct_hipExternalSemaphoreSignalParams_st_params(Structure):
    pass

class struct_hipExternalSemaphoreSignalParams_st_0_fence(Structure):
    pass

struct_hipExternalSemaphoreSignalParams_st_0_fence._pack_ = 1 # source:False
struct_hipExternalSemaphoreSignalParams_st_0_fence._fields_ = [
    ('value', ctypes.c_uint64),
]

class struct_hipExternalSemaphoreSignalParams_st_0_keyedMutex(Structure):
    pass

struct_hipExternalSemaphoreSignalParams_st_0_keyedMutex._pack_ = 1 # source:False
struct_hipExternalSemaphoreSignalParams_st_0_keyedMutex._fields_ = [
    ('key', ctypes.c_uint64),
]

struct_hipExternalSemaphoreSignalParams_st_params._pack_ = 1 # source:False
struct_hipExternalSemaphoreSignalParams_st_params._fields_ = [
    ('fence', struct_hipExternalSemaphoreSignalParams_st_0_fence),
    ('keyedMutex', struct_hipExternalSemaphoreSignalParams_st_0_keyedMutex),
    ('reserved', ctypes.c_uint32 * 12),
]

struct_hipExternalSemaphoreSignalParams_st._pack_ = 1 # source:False
struct_hipExternalSemaphoreSignalParams_st._fields_ = [
    ('params', struct_hipExternalSemaphoreSignalParams_st_params),
    ('flags', ctypes.c_uint32),
    ('reserved', ctypes.c_uint32 * 16),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

hipExternalSemaphoreSignalParams = struct_hipExternalSemaphoreSignalParams_st
class struct_hipExternalSemaphoreWaitParams_st(Structure):
    pass

class struct_hipExternalSemaphoreWaitParams_st_params(Structure):
    pass

class struct_hipExternalSemaphoreWaitParams_st_0_fence(Structure):
    pass

struct_hipExternalSemaphoreWaitParams_st_0_fence._pack_ = 1 # source:False
struct_hipExternalSemaphoreWaitParams_st_0_fence._fields_ = [
    ('value', ctypes.c_uint64),
]

class struct_hipExternalSemaphoreWaitParams_st_0_keyedMutex(Structure):
    pass

struct_hipExternalSemaphoreWaitParams_st_0_keyedMutex._pack_ = 1 # source:False
struct_hipExternalSemaphoreWaitParams_st_0_keyedMutex._fields_ = [
    ('key', ctypes.c_uint64),
    ('timeoutMs', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

struct_hipExternalSemaphoreWaitParams_st_params._pack_ = 1 # source:False
struct_hipExternalSemaphoreWaitParams_st_params._fields_ = [
    ('fence', struct_hipExternalSemaphoreWaitParams_st_0_fence),
    ('keyedMutex', struct_hipExternalSemaphoreWaitParams_st_0_keyedMutex),
    ('reserved', ctypes.c_uint32 * 10),
]

struct_hipExternalSemaphoreWaitParams_st._pack_ = 1 # source:False
struct_hipExternalSemaphoreWaitParams_st._fields_ = [
    ('params', struct_hipExternalSemaphoreWaitParams_st_params),
    ('flags', ctypes.c_uint32),
    ('reserved', ctypes.c_uint32 * 16),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

hipExternalSemaphoreWaitParams = struct_hipExternalSemaphoreWaitParams_st
try:
    __hipGetPCH = _libraries[LIB_HIP].__hipGetPCH
    __hipGetPCH.restype = None
    __hipGetPCH.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_char)), ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass

# values for enumeration 'hipGLDeviceList'
hipGLDeviceList__enumvalues = {
    1: 'hipGLDeviceListAll',
    2: 'hipGLDeviceListCurrentFrame',
    3: 'hipGLDeviceListNextFrame',
}
hipGLDeviceListAll = 1
hipGLDeviceListCurrentFrame = 2
hipGLDeviceListNextFrame = 3
hipGLDeviceList = ctypes.c_uint32 # enum

# values for enumeration 'hipGraphicsRegisterFlags'
hipGraphicsRegisterFlags__enumvalues = {
    0: 'hipGraphicsRegisterFlagsNone',
    1: 'hipGraphicsRegisterFlagsReadOnly',
    2: 'hipGraphicsRegisterFlagsWriteDiscard',
    4: 'hipGraphicsRegisterFlagsSurfaceLoadStore',
    8: 'hipGraphicsRegisterFlagsTextureGather',
}
hipGraphicsRegisterFlagsNone = 0
hipGraphicsRegisterFlagsReadOnly = 1
hipGraphicsRegisterFlagsWriteDiscard = 2
hipGraphicsRegisterFlagsSurfaceLoadStore = 4
hipGraphicsRegisterFlagsTextureGather = 8
hipGraphicsRegisterFlags = ctypes.c_uint32 # enum
class struct__hipGraphicsResource(Structure):
    pass

hipGraphicsResource = struct__hipGraphicsResource
hipGraphicsResource_t = ctypes.POINTER(struct__hipGraphicsResource)
class struct_ihipGraph(Structure):
    pass

hipGraph_t = ctypes.POINTER(struct_ihipGraph)
class struct_hipGraphNode(Structure):
    pass

hipGraphNode_t = ctypes.POINTER(struct_hipGraphNode)
class struct_hipGraphExec(Structure):
    pass

hipGraphExec_t = ctypes.POINTER(struct_hipGraphExec)
class struct_hipUserObject(Structure):
    pass

hipUserObject_t = ctypes.POINTER(struct_hipUserObject)

# values for enumeration 'hipGraphNodeType'
hipGraphNodeType__enumvalues = {
    0: 'hipGraphNodeTypeKernel',
    1: 'hipGraphNodeTypeMemcpy',
    2: 'hipGraphNodeTypeMemset',
    3: 'hipGraphNodeTypeHost',
    4: 'hipGraphNodeTypeGraph',
    5: 'hipGraphNodeTypeEmpty',
    6: 'hipGraphNodeTypeWaitEvent',
    7: 'hipGraphNodeTypeEventRecord',
    8: 'hipGraphNodeTypeExtSemaphoreSignal',
    9: 'hipGraphNodeTypeExtSemaphoreWait',
    10: 'hipGraphNodeTypeMemAlloc',
    11: 'hipGraphNodeTypeMemFree',
    12: 'hipGraphNodeTypeMemcpyFromSymbol',
    13: 'hipGraphNodeTypeMemcpyToSymbol',
    14: 'hipGraphNodeTypeCount',
}
hipGraphNodeTypeKernel = 0
hipGraphNodeTypeMemcpy = 1
hipGraphNodeTypeMemset = 2
hipGraphNodeTypeHost = 3
hipGraphNodeTypeGraph = 4
hipGraphNodeTypeEmpty = 5
hipGraphNodeTypeWaitEvent = 6
hipGraphNodeTypeEventRecord = 7
hipGraphNodeTypeExtSemaphoreSignal = 8
hipGraphNodeTypeExtSemaphoreWait = 9
hipGraphNodeTypeMemAlloc = 10
hipGraphNodeTypeMemFree = 11
hipGraphNodeTypeMemcpyFromSymbol = 12
hipGraphNodeTypeMemcpyToSymbol = 13
hipGraphNodeTypeCount = 14
hipGraphNodeType = ctypes.c_uint32 # enum
hipHostFn_t = ctypes.CFUNCTYPE(None, ctypes.POINTER(None))
class struct_hipHostNodeParams(Structure):
    pass

struct_hipHostNodeParams._pack_ = 1 # source:False
struct_hipHostNodeParams._fields_ = [
    ('fn', ctypes.CFUNCTYPE(None, ctypes.POINTER(None))),
    ('userData', ctypes.POINTER(None)),
]

hipHostNodeParams = struct_hipHostNodeParams
class struct_hipKernelNodeParams(Structure):
    pass

struct_hipKernelNodeParams._pack_ = 1 # source:False
struct_hipKernelNodeParams._fields_ = [
    ('blockDim', dim3),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('extra', ctypes.POINTER(ctypes.POINTER(None))),
    ('func', ctypes.POINTER(None)),
    ('gridDim', dim3),
    ('PADDING_1', ctypes.c_ubyte * 4),
    ('kernelParams', ctypes.POINTER(ctypes.POINTER(None))),
    ('sharedMemBytes', ctypes.c_uint32),
    ('PADDING_2', ctypes.c_ubyte * 4),
]

hipKernelNodeParams = struct_hipKernelNodeParams
class struct_hipMemsetParams(Structure):
    pass

struct_hipMemsetParams._pack_ = 1 # source:False
struct_hipMemsetParams._fields_ = [
    ('dst', ctypes.POINTER(None)),
    ('elementSize', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('height', ctypes.c_uint64),
    ('pitch', ctypes.c_uint64),
    ('value', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
    ('width', ctypes.c_uint64),
]

hipMemsetParams = struct_hipMemsetParams
class struct_hipMemAllocNodeParams(Structure):
    pass

struct_hipMemAllocNodeParams._pack_ = 1 # source:False
struct_hipMemAllocNodeParams._fields_ = [
    ('poolProps', hipMemPoolProps),
    ('accessDescs', ctypes.POINTER(struct_hipMemAccessDesc)),
    ('accessDescCount', ctypes.c_uint64),
    ('bytesize', ctypes.c_uint64),
    ('dptr', ctypes.POINTER(None)),
]

hipMemAllocNodeParams = struct_hipMemAllocNodeParams

# values for enumeration 'hipKernelNodeAttrID'
hipKernelNodeAttrID__enumvalues = {
    1: 'hipKernelNodeAttributeAccessPolicyWindow',
    2: 'hipKernelNodeAttributeCooperative',
}
hipKernelNodeAttributeAccessPolicyWindow = 1
hipKernelNodeAttributeCooperative = 2
hipKernelNodeAttrID = ctypes.c_uint32 # enum

# values for enumeration 'hipAccessProperty'
hipAccessProperty__enumvalues = {
    0: 'hipAccessPropertyNormal',
    1: 'hipAccessPropertyStreaming',
    2: 'hipAccessPropertyPersisting',
}
hipAccessPropertyNormal = 0
hipAccessPropertyStreaming = 1
hipAccessPropertyPersisting = 2
hipAccessProperty = ctypes.c_uint32 # enum
class struct_hipAccessPolicyWindow(Structure):
    pass

struct_hipAccessPolicyWindow._pack_ = 1 # source:False
struct_hipAccessPolicyWindow._fields_ = [
    ('base_ptr', ctypes.POINTER(None)),
    ('hitProp', hipAccessProperty),
    ('hitRatio', ctypes.c_float),
    ('missProp', hipAccessProperty),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('num_bytes', ctypes.c_uint64),
]

hipAccessPolicyWindow = struct_hipAccessPolicyWindow
class union_hipKernelNodeAttrValue(Union):
    pass

union_hipKernelNodeAttrValue._pack_ = 1 # source:False
union_hipKernelNodeAttrValue._fields_ = [
    ('accessPolicyWindow', hipAccessPolicyWindow),
    ('cooperative', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 28),
]

hipKernelNodeAttrValue = union_hipKernelNodeAttrValue

# values for enumeration 'hipGraphExecUpdateResult'
hipGraphExecUpdateResult__enumvalues = {
    0: 'hipGraphExecUpdateSuccess',
    1: 'hipGraphExecUpdateError',
    2: 'hipGraphExecUpdateErrorTopologyChanged',
    3: 'hipGraphExecUpdateErrorNodeTypeChanged',
    4: 'hipGraphExecUpdateErrorFunctionChanged',
    5: 'hipGraphExecUpdateErrorParametersChanged',
    6: 'hipGraphExecUpdateErrorNotSupported',
    7: 'hipGraphExecUpdateErrorUnsupportedFunctionChange',
}
hipGraphExecUpdateSuccess = 0
hipGraphExecUpdateError = 1
hipGraphExecUpdateErrorTopologyChanged = 2
hipGraphExecUpdateErrorNodeTypeChanged = 3
hipGraphExecUpdateErrorFunctionChanged = 4
hipGraphExecUpdateErrorParametersChanged = 5
hipGraphExecUpdateErrorNotSupported = 6
hipGraphExecUpdateErrorUnsupportedFunctionChange = 7
hipGraphExecUpdateResult = ctypes.c_uint32 # enum

# values for enumeration 'hipStreamCaptureMode'
hipStreamCaptureMode__enumvalues = {
    0: 'hipStreamCaptureModeGlobal',
    1: 'hipStreamCaptureModeThreadLocal',
    2: 'hipStreamCaptureModeRelaxed',
}
hipStreamCaptureModeGlobal = 0
hipStreamCaptureModeThreadLocal = 1
hipStreamCaptureModeRelaxed = 2
hipStreamCaptureMode = ctypes.c_uint32 # enum

# values for enumeration 'hipStreamCaptureStatus'
hipStreamCaptureStatus__enumvalues = {
    0: 'hipStreamCaptureStatusNone',
    1: 'hipStreamCaptureStatusActive',
    2: 'hipStreamCaptureStatusInvalidated',
}
hipStreamCaptureStatusNone = 0
hipStreamCaptureStatusActive = 1
hipStreamCaptureStatusInvalidated = 2
hipStreamCaptureStatus = ctypes.c_uint32 # enum

# values for enumeration 'hipStreamUpdateCaptureDependenciesFlags'
hipStreamUpdateCaptureDependenciesFlags__enumvalues = {
    0: 'hipStreamAddCaptureDependencies',
    1: 'hipStreamSetCaptureDependencies',
}
hipStreamAddCaptureDependencies = 0
hipStreamSetCaptureDependencies = 1
hipStreamUpdateCaptureDependenciesFlags = ctypes.c_uint32 # enum

# values for enumeration 'hipGraphMemAttributeType'
hipGraphMemAttributeType__enumvalues = {
    0: 'hipGraphMemAttrUsedMemCurrent',
    1: 'hipGraphMemAttrUsedMemHigh',
    2: 'hipGraphMemAttrReservedMemCurrent',
    3: 'hipGraphMemAttrReservedMemHigh',
}
hipGraphMemAttrUsedMemCurrent = 0
hipGraphMemAttrUsedMemHigh = 1
hipGraphMemAttrReservedMemCurrent = 2
hipGraphMemAttrReservedMemHigh = 3
hipGraphMemAttributeType = ctypes.c_uint32 # enum

# values for enumeration 'hipUserObjectFlags'
hipUserObjectFlags__enumvalues = {
    1: 'hipUserObjectNoDestructorSync',
}
hipUserObjectNoDestructorSync = 1
hipUserObjectFlags = ctypes.c_uint32 # enum

# values for enumeration 'hipUserObjectRetainFlags'
hipUserObjectRetainFlags__enumvalues = {
    1: 'hipGraphUserObjectMove',
}
hipGraphUserObjectMove = 1
hipUserObjectRetainFlags = ctypes.c_uint32 # enum

# values for enumeration 'hipGraphInstantiateFlags'
hipGraphInstantiateFlags__enumvalues = {
    1: 'hipGraphInstantiateFlagAutoFreeOnLaunch',
    2: 'hipGraphInstantiateFlagUpload',
    4: 'hipGraphInstantiateFlagDeviceLaunch',
    8: 'hipGraphInstantiateFlagUseNodePriority',
}
hipGraphInstantiateFlagAutoFreeOnLaunch = 1
hipGraphInstantiateFlagUpload = 2
hipGraphInstantiateFlagDeviceLaunch = 4
hipGraphInstantiateFlagUseNodePriority = 8
hipGraphInstantiateFlags = ctypes.c_uint32 # enum

# values for enumeration 'hipGraphDebugDotFlags'
hipGraphDebugDotFlags__enumvalues = {
    1: 'hipGraphDebugDotFlagsVerbose',
    4: 'hipGraphDebugDotFlagsKernelNodeParams',
    8: 'hipGraphDebugDotFlagsMemcpyNodeParams',
    16: 'hipGraphDebugDotFlagsMemsetNodeParams',
    32: 'hipGraphDebugDotFlagsHostNodeParams',
    64: 'hipGraphDebugDotFlagsEventNodeParams',
    128: 'hipGraphDebugDotFlagsExtSemasSignalNodeParams',
    256: 'hipGraphDebugDotFlagsExtSemasWaitNodeParams',
    512: 'hipGraphDebugDotFlagsKernelNodeAttributes',
    1024: 'hipGraphDebugDotFlagsHandles',
}
hipGraphDebugDotFlagsVerbose = 1
hipGraphDebugDotFlagsKernelNodeParams = 4
hipGraphDebugDotFlagsMemcpyNodeParams = 8
hipGraphDebugDotFlagsMemsetNodeParams = 16
hipGraphDebugDotFlagsHostNodeParams = 32
hipGraphDebugDotFlagsEventNodeParams = 64
hipGraphDebugDotFlagsExtSemasSignalNodeParams = 128
hipGraphDebugDotFlagsExtSemasWaitNodeParams = 256
hipGraphDebugDotFlagsKernelNodeAttributes = 512
hipGraphDebugDotFlagsHandles = 1024
hipGraphDebugDotFlags = ctypes.c_uint32 # enum
class struct_hipMemAllocationProp(Structure):
    pass

class struct_hipMemAllocationProp_allocFlags(Structure):
    pass

struct_hipMemAllocationProp_allocFlags._pack_ = 1 # source:False
struct_hipMemAllocationProp_allocFlags._fields_ = [
    ('compressionType', ctypes.c_ubyte),
    ('gpuDirectRDMACapable', ctypes.c_ubyte),
    ('usage', ctypes.c_uint16),
]

struct_hipMemAllocationProp._pack_ = 1 # source:False
struct_hipMemAllocationProp._fields_ = [
    ('type', hipMemAllocationType),
    ('requestedHandleType', hipMemAllocationHandleType),
    ('location', hipMemLocation),
    ('win32HandleMetaData', ctypes.POINTER(None)),
    ('allocFlags', struct_hipMemAllocationProp_allocFlags),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

hipMemAllocationProp = struct_hipMemAllocationProp
class struct_hipExternalSemaphoreSignalNodeParams(Structure):
    pass

struct_hipExternalSemaphoreSignalNodeParams._pack_ = 1 # source:False
struct_hipExternalSemaphoreSignalNodeParams._fields_ = [
    ('extSemArray', ctypes.POINTER(ctypes.POINTER(None))),
    ('paramsArray', ctypes.POINTER(struct_hipExternalSemaphoreSignalParams_st)),
    ('numExtSems', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

hipExternalSemaphoreSignalNodeParams = struct_hipExternalSemaphoreSignalNodeParams
class struct_hipExternalSemaphoreWaitNodeParams(Structure):
    pass

struct_hipExternalSemaphoreWaitNodeParams._pack_ = 1 # source:False
struct_hipExternalSemaphoreWaitNodeParams._fields_ = [
    ('extSemArray', ctypes.POINTER(ctypes.POINTER(None))),
    ('paramsArray', ctypes.POINTER(struct_hipExternalSemaphoreWaitParams_st)),
    ('numExtSems', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

hipExternalSemaphoreWaitNodeParams = struct_hipExternalSemaphoreWaitNodeParams
class struct_ihipMemGenericAllocationHandle(Structure):
    pass

hipMemGenericAllocationHandle_t = ctypes.POINTER(struct_ihipMemGenericAllocationHandle)

# values for enumeration 'hipMemAllocationGranularity_flags'
hipMemAllocationGranularity_flags__enumvalues = {
    0: 'hipMemAllocationGranularityMinimum',
    1: 'hipMemAllocationGranularityRecommended',
}
hipMemAllocationGranularityMinimum = 0
hipMemAllocationGranularityRecommended = 1
hipMemAllocationGranularity_flags = ctypes.c_uint32 # enum

# values for enumeration 'hipMemHandleType'
hipMemHandleType__enumvalues = {
    0: 'hipMemHandleTypeGeneric',
}
hipMemHandleTypeGeneric = 0
hipMemHandleType = ctypes.c_uint32 # enum

# values for enumeration 'hipMemOperationType'
hipMemOperationType__enumvalues = {
    1: 'hipMemOperationTypeMap',
    2: 'hipMemOperationTypeUnmap',
}
hipMemOperationTypeMap = 1
hipMemOperationTypeUnmap = 2
hipMemOperationType = ctypes.c_uint32 # enum

# values for enumeration 'hipArraySparseSubresourceType'
hipArraySparseSubresourceType__enumvalues = {
    0: 'hipArraySparseSubresourceTypeSparseLevel',
    1: 'hipArraySparseSubresourceTypeMiptail',
}
hipArraySparseSubresourceTypeSparseLevel = 0
hipArraySparseSubresourceTypeMiptail = 1
hipArraySparseSubresourceType = ctypes.c_uint32 # enum
class struct_hipArrayMapInfo(Structure):
    pass

class union_hipArrayMapInfo_resource(Union):
    pass

union_hipArrayMapInfo_resource._pack_ = 1 # source:False
union_hipArrayMapInfo_resource._fields_ = [
    ('mipmap', hipMipmappedArray),
    ('array', ctypes.POINTER(struct_hipArray)),
    ('PADDING_0', ctypes.c_ubyte * 56),
]

class union_hipArrayMapInfo_subresource(Union):
    pass

class struct_hipArrayMapInfo_1_sparseLevel(Structure):
    pass

struct_hipArrayMapInfo_1_sparseLevel._pack_ = 1 # source:False
struct_hipArrayMapInfo_1_sparseLevel._fields_ = [
    ('level', ctypes.c_uint32),
    ('layer', ctypes.c_uint32),
    ('offsetX', ctypes.c_uint32),
    ('offsetY', ctypes.c_uint32),
    ('offsetZ', ctypes.c_uint32),
    ('extentWidth', ctypes.c_uint32),
    ('extentHeight', ctypes.c_uint32),
    ('extentDepth', ctypes.c_uint32),
]

class struct_hipArrayMapInfo_1_miptail(Structure):
    pass

struct_hipArrayMapInfo_1_miptail._pack_ = 1 # source:False
struct_hipArrayMapInfo_1_miptail._fields_ = [
    ('layer', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('offset', ctypes.c_uint64),
    ('size', ctypes.c_uint64),
]

union_hipArrayMapInfo_subresource._pack_ = 1 # source:False
union_hipArrayMapInfo_subresource._fields_ = [
    ('sparseLevel', struct_hipArrayMapInfo_1_sparseLevel),
    ('miptail', struct_hipArrayMapInfo_1_miptail),
    ('PADDING_0', ctypes.c_ubyte * 8),
]

class union_hipArrayMapInfo_memHandle(Union):
    pass

union_hipArrayMapInfo_memHandle._pack_ = 1 # source:False
union_hipArrayMapInfo_memHandle._fields_ = [
    ('memHandle', ctypes.POINTER(struct_ihipMemGenericAllocationHandle)),
]

struct_hipArrayMapInfo._pack_ = 1 # source:False
struct_hipArrayMapInfo._fields_ = [
    ('resourceType', hipResourceType),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('resource', union_hipArrayMapInfo_resource),
    ('subresourceType', hipArraySparseSubresourceType),
    ('PADDING_1', ctypes.c_ubyte * 4),
    ('subresource', union_hipArrayMapInfo_subresource),
    ('memOperationType', hipMemOperationType),
    ('memHandleType', hipMemHandleType),
    ('memHandle', union_hipArrayMapInfo_memHandle),
    ('offset', ctypes.c_uint64),
    ('deviceBitMask', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('reserved', ctypes.c_uint32 * 2),
]

hipArrayMapInfo = struct_hipArrayMapInfo
try:
    hipInit = _libraries[LIB_HIP].hipInit
    hipInit.restype = hipError_t
    hipInit.argtypes = [ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipDriverGetVersion = _libraries[LIB_HIP].hipDriverGetVersion
    hipDriverGetVersion.restype = hipError_t
    hipDriverGetVersion.argtypes = [ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
try:
    hipRuntimeGetVersion = _libraries[LIB_HIP].hipRuntimeGetVersion
    hipRuntimeGetVersion.restype = hipError_t
    hipRuntimeGetVersion.argtypes = [ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
try:
    hipDeviceGet = _libraries[LIB_HIP].hipDeviceGet
    hipDeviceGet.restype = hipError_t
    hipDeviceGet.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]
except AttributeError:
    pass
try:
    hipDeviceComputeCapability = _libraries[LIB_HIP].hipDeviceComputeCapability
    hipDeviceComputeCapability.restype = hipError_t
    hipDeviceComputeCapability.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32), hipDevice_t]
except AttributeError:
    pass
try:
    hipDeviceGetName = _libraries[LIB_HIP].hipDeviceGetName
    hipDeviceGetName.restype = hipError_t
    hipDeviceGetName.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_int32, hipDevice_t]
except AttributeError:
    pass
try:
    hipDeviceGetUuid = _libraries[LIB_HIP].hipDeviceGetUuid
    hipDeviceGetUuid.restype = hipError_t
    hipDeviceGetUuid.argtypes = [ctypes.POINTER(struct_hipUUID_t), hipDevice_t]
except AttributeError:
    pass
try:
    hipDeviceGetP2PAttribute = _libraries[LIB_HIP].hipDeviceGetP2PAttribute
    hipDeviceGetP2PAttribute.restype = hipError_t
    hipDeviceGetP2PAttribute.argtypes = [ctypes.POINTER(ctypes.c_int32), hipDeviceP2PAttr, ctypes.c_int32, ctypes.c_int32]
except AttributeError:
    pass
try:
    hipDeviceGetPCIBusId = _libraries[LIB_HIP].hipDeviceGetPCIBusId
    hipDeviceGetPCIBusId.restype = hipError_t
    hipDeviceGetPCIBusId.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_int32, ctypes.c_int32]
except AttributeError:
    pass
try:
    hipDeviceGetByPCIBusId = _libraries[LIB_HIP].hipDeviceGetByPCIBusId
    hipDeviceGetByPCIBusId.restype = hipError_t
    hipDeviceGetByPCIBusId.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    hipDeviceTotalMem = _libraries[LIB_HIP].hipDeviceTotalMem
    hipDeviceTotalMem.restype = hipError_t
    hipDeviceTotalMem.argtypes = [ctypes.POINTER(ctypes.c_uint64), hipDevice_t]
except AttributeError:
    pass
try:
    hipDeviceSynchronize = _libraries[LIB_HIP].hipDeviceSynchronize
    hipDeviceSynchronize.restype = hipError_t
    hipDeviceSynchronize.argtypes = []
except AttributeError:
    pass
try:
    hipDeviceReset = _libraries[LIB_HIP].hipDeviceReset
    hipDeviceReset.restype = hipError_t
    hipDeviceReset.argtypes = []
except AttributeError:
    pass
try:
    hipSetDevice = _libraries[LIB_HIP].hipSetDevice
    hipSetDevice.restype = hipError_t
    hipSetDevice.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    hipGetDevice = _libraries[LIB_HIP].hipGetDevice
    hipGetDevice.restype = hipError_t
    hipGetDevice.argtypes = [ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
try:
    hipGetDeviceCount = _libraries[LIB_HIP].hipGetDeviceCount
    hipGetDeviceCount.restype = hipError_t
    hipGetDeviceCount.argtypes = [ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
try:
    hipDeviceGetAttribute = _libraries[LIB_HIP].hipDeviceGetAttribute
    hipDeviceGetAttribute.restype = hipError_t
    hipDeviceGetAttribute.argtypes = [ctypes.POINTER(ctypes.c_int32), hipDeviceAttribute_t, ctypes.c_int32]
except AttributeError:
    pass
try:
    hipDeviceGetDefaultMemPool = _libraries[LIB_HIP].hipDeviceGetDefaultMemPool
    hipDeviceGetDefaultMemPool.restype = hipError_t
    hipDeviceGetDefaultMemPool.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipMemPoolHandle_t)), ctypes.c_int32]
except AttributeError:
    pass
try:
    hipDeviceSetMemPool = _libraries[LIB_HIP].hipDeviceSetMemPool
    hipDeviceSetMemPool.restype = hipError_t
    hipDeviceSetMemPool.argtypes = [ctypes.c_int32, hipMemPool_t]
except AttributeError:
    pass
try:
    hipDeviceGetMemPool = _libraries[LIB_HIP].hipDeviceGetMemPool
    hipDeviceGetMemPool.restype = hipError_t
    hipDeviceGetMemPool.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipMemPoolHandle_t)), ctypes.c_int32]
except AttributeError:
    pass
try:
    hipGetDeviceProperties = _libraries[LIB_HIP].hipGetDeviceProperties
    hipGetDeviceProperties.restype = hipError_t
    hipGetDeviceProperties.argtypes = [ctypes.POINTER(struct_hipDeviceProp_t), ctypes.c_int32]
except AttributeError:
    pass
try:
    hipDeviceSetCacheConfig = _libraries[LIB_HIP].hipDeviceSetCacheConfig
    hipDeviceSetCacheConfig.restype = hipError_t
    hipDeviceSetCacheConfig.argtypes = [hipFuncCache_t]
except AttributeError:
    pass
try:
    hipDeviceGetCacheConfig = _libraries[LIB_HIP].hipDeviceGetCacheConfig
    hipDeviceGetCacheConfig.restype = hipError_t
    hipDeviceGetCacheConfig.argtypes = [ctypes.POINTER(hipFuncCache_t)]
except AttributeError:
    pass
try:
    hipDeviceGetLimit = _libraries[LIB_HIP].hipDeviceGetLimit
    hipDeviceGetLimit.restype = hipError_t
    hipDeviceGetLimit.argtypes = [ctypes.POINTER(ctypes.c_uint64), hipLimit_t]
except AttributeError:
    pass
try:
    hipDeviceSetLimit = _libraries[LIB_HIP].hipDeviceSetLimit
    hipDeviceSetLimit.restype = hipError_t
    hipDeviceSetLimit.argtypes = [hipLimit_t, size_t]
except AttributeError:
    pass
try:
    hipDeviceGetSharedMemConfig = _libraries[LIB_HIP].hipDeviceGetSharedMemConfig
    hipDeviceGetSharedMemConfig.restype = hipError_t
    hipDeviceGetSharedMemConfig.argtypes = [ctypes.POINTER(hipSharedMemConfig)]
except AttributeError:
    pass
try:
    hipGetDeviceFlags = _libraries[LIB_HIP].hipGetDeviceFlags
    hipGetDeviceFlags.restype = hipError_t
    hipGetDeviceFlags.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    hipDeviceSetSharedMemConfig = _libraries[LIB_HIP].hipDeviceSetSharedMemConfig
    hipDeviceSetSharedMemConfig.restype = hipError_t
    hipDeviceSetSharedMemConfig.argtypes = [hipSharedMemConfig]
except AttributeError:
    pass
try:
    hipSetDeviceFlags = _libraries[LIB_HIP].hipSetDeviceFlags
    hipSetDeviceFlags.restype = hipError_t
    hipSetDeviceFlags.argtypes = [ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipChooseDevice = _libraries[LIB_HIP].hipChooseDevice
    hipChooseDevice.restype = hipError_t
    hipChooseDevice.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(struct_hipDeviceProp_t)]
except AttributeError:
    pass
try:
    hipExtGetLinkTypeAndHopCount = _libraries[LIB_HIP].hipExtGetLinkTypeAndHopCount
    hipExtGetLinkTypeAndHopCount.restype = hipError_t
    hipExtGetLinkTypeAndHopCount.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    hipIpcGetMemHandle = _libraries[LIB_HIP].hipIpcGetMemHandle
    hipIpcGetMemHandle.restype = hipError_t
    hipIpcGetMemHandle.argtypes = [ctypes.POINTER(struct_hipIpcMemHandle_st), ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipIpcOpenMemHandle = _libraries[LIB_HIP].hipIpcOpenMemHandle
    hipIpcOpenMemHandle.restype = hipError_t
    hipIpcOpenMemHandle.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), hipIpcMemHandle_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipIpcCloseMemHandle = _libraries[LIB_HIP].hipIpcCloseMemHandle
    hipIpcCloseMemHandle.restype = hipError_t
    hipIpcCloseMemHandle.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipIpcGetEventHandle = _libraries[LIB_HIP].hipIpcGetEventHandle
    hipIpcGetEventHandle.restype = hipError_t
    hipIpcGetEventHandle.argtypes = [ctypes.POINTER(struct_hipIpcEventHandle_st), hipEvent_t]
except AttributeError:
    pass
try:
    hipIpcOpenEventHandle = _libraries[LIB_HIP].hipIpcOpenEventHandle
    hipIpcOpenEventHandle.restype = hipError_t
    hipIpcOpenEventHandle.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipEvent_t)), hipIpcEventHandle_t]
except AttributeError:
    pass
try:
    hipFuncSetAttribute = _libraries[LIB_HIP].hipFuncSetAttribute
    hipFuncSetAttribute.restype = hipError_t
    hipFuncSetAttribute.argtypes = [ctypes.POINTER(None), hipFuncAttribute, ctypes.c_int32]
except AttributeError:
    pass
try:
    hipFuncSetCacheConfig = _libraries[LIB_HIP].hipFuncSetCacheConfig
    hipFuncSetCacheConfig.restype = hipError_t
    hipFuncSetCacheConfig.argtypes = [ctypes.POINTER(None), hipFuncCache_t]
except AttributeError:
    pass
try:
    hipFuncSetSharedMemConfig = _libraries[LIB_HIP].hipFuncSetSharedMemConfig
    hipFuncSetSharedMemConfig.restype = hipError_t
    hipFuncSetSharedMemConfig.argtypes = [ctypes.POINTER(None), hipSharedMemConfig]
except AttributeError:
    pass
try:
    hipGetLastError = _libraries[LIB_HIP].hipGetLastError
    hipGetLastError.restype = hipError_t
    hipGetLastError.argtypes = []
except AttributeError:
    pass
try:
    hipPeekAtLastError = _libraries[LIB_HIP].hipPeekAtLastError
    hipPeekAtLastError.restype = hipError_t
    hipPeekAtLastError.argtypes = []
except AttributeError:
    pass
try:
    hipGetErrorName = _libraries[LIB_HIP].hipGetErrorName
    hipGetErrorName.restype = ctypes.POINTER(ctypes.c_char)
    hipGetErrorName.argtypes = [hipError_t]
except AttributeError:
    pass
try:
    hipGetErrorString = _libraries[LIB_HIP].hipGetErrorString
    hipGetErrorString.restype = ctypes.POINTER(ctypes.c_char)
    hipGetErrorString.argtypes = [hipError_t]
except AttributeError:
    pass
try:
    hipDrvGetErrorName = _libraries[LIB_HIP].hipDrvGetErrorName
    hipDrvGetErrorName.restype = hipError_t
    hipDrvGetErrorName.argtypes = [hipError_t, ctypes.POINTER(ctypes.POINTER(ctypes.c_char))]
except AttributeError:
    pass
try:
    hipDrvGetErrorString = _libraries[LIB_HIP].hipDrvGetErrorString
    hipDrvGetErrorString.restype = hipError_t
    hipDrvGetErrorString.argtypes = [hipError_t, ctypes.POINTER(ctypes.POINTER(ctypes.c_char))]
except AttributeError:
    pass
try:
    hipStreamCreate = _libraries[LIB_HIP].hipStreamCreate
    hipStreamCreate.restype = hipError_t
    hipStreamCreate.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipStream_t))]
except AttributeError:
    pass
try:
    hipStreamCreateWithFlags = _libraries[LIB_HIP].hipStreamCreateWithFlags
    hipStreamCreateWithFlags.restype = hipError_t
    hipStreamCreateWithFlags.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipStream_t)), ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipStreamCreateWithPriority = _libraries[LIB_HIP].hipStreamCreateWithPriority
    hipStreamCreateWithPriority.restype = hipError_t
    hipStreamCreateWithPriority.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipStream_t)), ctypes.c_uint32, ctypes.c_int32]
except AttributeError:
    pass
try:
    hipDeviceGetStreamPriorityRange = _libraries[LIB_HIP].hipDeviceGetStreamPriorityRange
    hipDeviceGetStreamPriorityRange.restype = hipError_t
    hipDeviceGetStreamPriorityRange.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
try:
    hipStreamDestroy = _libraries[LIB_HIP].hipStreamDestroy
    hipStreamDestroy.restype = hipError_t
    hipStreamDestroy.argtypes = [hipStream_t]
except AttributeError:
    pass
try:
    hipStreamQuery = _libraries[LIB_HIP].hipStreamQuery
    hipStreamQuery.restype = hipError_t
    hipStreamQuery.argtypes = [hipStream_t]
except AttributeError:
    pass
try:
    hipStreamSynchronize = _libraries[LIB_HIP].hipStreamSynchronize
    hipStreamSynchronize.restype = hipError_t
    hipStreamSynchronize.argtypes = [hipStream_t]
except AttributeError:
    pass
try:
    hipStreamWaitEvent = _libraries[LIB_HIP].hipStreamWaitEvent
    hipStreamWaitEvent.restype = hipError_t
    hipStreamWaitEvent.argtypes = [hipStream_t, hipEvent_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipStreamGetFlags = _libraries[LIB_HIP].hipStreamGetFlags
    hipStreamGetFlags.restype = hipError_t
    hipStreamGetFlags.argtypes = [hipStream_t, ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    hipStreamGetPriority = _libraries[LIB_HIP].hipStreamGetPriority
    hipStreamGetPriority.restype = hipError_t
    hipStreamGetPriority.argtypes = [hipStream_t, ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
try:
    hipStreamGetDevice = _libraries[LIB_HIP].hipStreamGetDevice
    hipStreamGetDevice.restype = hipError_t
    hipStreamGetDevice.argtypes = [hipStream_t, ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
uint32_t = ctypes.c_uint32
try:
    hipExtStreamCreateWithCUMask = _libraries[LIB_HIP].hipExtStreamCreateWithCUMask
    hipExtStreamCreateWithCUMask.restype = hipError_t
    hipExtStreamCreateWithCUMask.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipStream_t)), uint32_t, ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    hipExtStreamGetCUMask = _libraries[LIB_HIP].hipExtStreamGetCUMask
    hipExtStreamGetCUMask.restype = hipError_t
    hipExtStreamGetCUMask.argtypes = [hipStream_t, uint32_t, ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
hipStreamCallback_t = ctypes.CFUNCTYPE(None, ctypes.POINTER(struct_ihipStream_t), hipError_t, ctypes.POINTER(None))
try:
    hipStreamAddCallback = _libraries[LIB_HIP].hipStreamAddCallback
    hipStreamAddCallback.restype = hipError_t
    hipStreamAddCallback.argtypes = [hipStream_t, hipStreamCallback_t, ctypes.POINTER(None), ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipStreamWaitValue32 = _libraries[LIB_HIP].hipStreamWaitValue32
    hipStreamWaitValue32.restype = hipError_t
    hipStreamWaitValue32.argtypes = [hipStream_t, ctypes.POINTER(None), uint32_t, ctypes.c_uint32, uint32_t]
except AttributeError:
    pass
uint64_t = ctypes.c_uint64
try:
    hipStreamWaitValue64 = _libraries[LIB_HIP].hipStreamWaitValue64
    hipStreamWaitValue64.restype = hipError_t
    hipStreamWaitValue64.argtypes = [hipStream_t, ctypes.POINTER(None), uint64_t, ctypes.c_uint32, uint64_t]
except AttributeError:
    pass
try:
    hipStreamWriteValue32 = _libraries[LIB_HIP].hipStreamWriteValue32
    hipStreamWriteValue32.restype = hipError_t
    hipStreamWriteValue32.argtypes = [hipStream_t, ctypes.POINTER(None), uint32_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipStreamWriteValue64 = _libraries[LIB_HIP].hipStreamWriteValue64
    hipStreamWriteValue64.restype = hipError_t
    hipStreamWriteValue64.argtypes = [hipStream_t, ctypes.POINTER(None), uint64_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipEventCreateWithFlags = _libraries[LIB_HIP].hipEventCreateWithFlags
    hipEventCreateWithFlags.restype = hipError_t
    hipEventCreateWithFlags.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipEvent_t)), ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipEventCreate = _libraries[LIB_HIP].hipEventCreate
    hipEventCreate.restype = hipError_t
    hipEventCreate.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipEvent_t))]
except AttributeError:
    pass
try:
    hipEventRecord = _libraries[LIB_HIP].hipEventRecord
    hipEventRecord.restype = hipError_t
    hipEventRecord.argtypes = [hipEvent_t, hipStream_t]
except AttributeError:
    pass
try:
    hipEventDestroy = _libraries[LIB_HIP].hipEventDestroy
    hipEventDestroy.restype = hipError_t
    hipEventDestroy.argtypes = [hipEvent_t]
except AttributeError:
    pass
try:
    hipEventSynchronize = _libraries[LIB_HIP].hipEventSynchronize
    hipEventSynchronize.restype = hipError_t
    hipEventSynchronize.argtypes = [hipEvent_t]
except AttributeError:
    pass
try:
    hipEventElapsedTime = _libraries[LIB_HIP].hipEventElapsedTime
    hipEventElapsedTime.restype = hipError_t
    hipEventElapsedTime.argtypes = [ctypes.POINTER(ctypes.c_float), hipEvent_t, hipEvent_t]
except AttributeError:
    pass
try:
    hipEventQuery = _libraries[LIB_HIP].hipEventQuery
    hipEventQuery.restype = hipError_t
    hipEventQuery.argtypes = [hipEvent_t]
except AttributeError:
    pass
try:
    hipPointerSetAttribute = _libraries[LIB_HIP].hipPointerSetAttribute
    hipPointerSetAttribute.restype = hipError_t
    hipPointerSetAttribute.argtypes = [ctypes.POINTER(None), hipPointer_attribute, hipDeviceptr_t]
except AttributeError:
    pass
try:
    hipPointerGetAttributes = _libraries[LIB_HIP].hipPointerGetAttributes
    hipPointerGetAttributes.restype = hipError_t
    hipPointerGetAttributes.argtypes = [ctypes.POINTER(struct_hipPointerAttribute_t), ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipPointerGetAttribute = _libraries[LIB_HIP].hipPointerGetAttribute
    hipPointerGetAttribute.restype = hipError_t
    hipPointerGetAttribute.argtypes = [ctypes.POINTER(None), hipPointer_attribute, hipDeviceptr_t]
except AttributeError:
    pass
try:
    hipDrvPointerGetAttributes = _libraries[LIB_HIP].hipDrvPointerGetAttributes
    hipDrvPointerGetAttributes.restype = hipError_t
    hipDrvPointerGetAttributes.argtypes = [ctypes.c_uint32, ctypes.POINTER(hipPointer_attribute), ctypes.POINTER(ctypes.POINTER(None)), hipDeviceptr_t]
except AttributeError:
    pass
try:
    hipImportExternalSemaphore = _libraries[LIB_HIP].hipImportExternalSemaphore
    hipImportExternalSemaphore.restype = hipError_t
    hipImportExternalSemaphore.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(struct_hipExternalSemaphoreHandleDesc_st)]
except AttributeError:
    pass
try:
    hipSignalExternalSemaphoresAsync = _libraries[LIB_HIP].hipSignalExternalSemaphoresAsync
    hipSignalExternalSemaphoresAsync.restype = hipError_t
    hipSignalExternalSemaphoresAsync.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(struct_hipExternalSemaphoreSignalParams_st), ctypes.c_uint32, hipStream_t]
except AttributeError:
    pass
try:
    hipWaitExternalSemaphoresAsync = _libraries[LIB_HIP].hipWaitExternalSemaphoresAsync
    hipWaitExternalSemaphoresAsync.restype = hipError_t
    hipWaitExternalSemaphoresAsync.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(struct_hipExternalSemaphoreWaitParams_st), ctypes.c_uint32, hipStream_t]
except AttributeError:
    pass
try:
    hipDestroyExternalSemaphore = _libraries[LIB_HIP].hipDestroyExternalSemaphore
    hipDestroyExternalSemaphore.restype = hipError_t
    hipDestroyExternalSemaphore.argtypes = [hipExternalSemaphore_t]
except AttributeError:
    pass
try:
    hipImportExternalMemory = _libraries[LIB_HIP].hipImportExternalMemory
    hipImportExternalMemory.restype = hipError_t
    hipImportExternalMemory.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(struct_hipExternalMemoryHandleDesc_st)]
except AttributeError:
    pass
try:
    hipExternalMemoryGetMappedBuffer = _libraries[LIB_HIP].hipExternalMemoryGetMappedBuffer
    hipExternalMemoryGetMappedBuffer.restype = hipError_t
    hipExternalMemoryGetMappedBuffer.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), hipExternalMemory_t, ctypes.POINTER(struct_hipExternalMemoryBufferDesc_st)]
except AttributeError:
    pass
try:
    hipDestroyExternalMemory = _libraries[LIB_HIP].hipDestroyExternalMemory
    hipDestroyExternalMemory.restype = hipError_t
    hipDestroyExternalMemory.argtypes = [hipExternalMemory_t]
except AttributeError:
    pass
try:
    hipMalloc = _libraries[LIB_HIP].hipMalloc
    hipMalloc.restype = hipError_t
    hipMalloc.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), size_t]
except AttributeError:
    pass
try:
    hipExtMallocWithFlags = _libraries[LIB_HIP].hipExtMallocWithFlags
    hipExtMallocWithFlags.restype = hipError_t
    hipExtMallocWithFlags.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), size_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipMallocHost = _libraries[LIB_HIP].hipMallocHost
    hipMallocHost.restype = hipError_t
    hipMallocHost.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), size_t]
except AttributeError:
    pass
try:
    hipMemAllocHost = _libraries[LIB_HIP].hipMemAllocHost
    hipMemAllocHost.restype = hipError_t
    hipMemAllocHost.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), size_t]
except AttributeError:
    pass
try:
    hipHostMalloc = _libraries[LIB_HIP].hipHostMalloc
    hipHostMalloc.restype = hipError_t
    hipHostMalloc.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), size_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipMallocManaged = _libraries[LIB_HIP].hipMallocManaged
    hipMallocManaged.restype = hipError_t
    hipMallocManaged.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), size_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipMemPrefetchAsync = _libraries[LIB_HIP].hipMemPrefetchAsync
    hipMemPrefetchAsync.restype = hipError_t
    hipMemPrefetchAsync.argtypes = [ctypes.POINTER(None), size_t, ctypes.c_int32, hipStream_t]
except AttributeError:
    pass
try:
    hipMemAdvise = _libraries[LIB_HIP].hipMemAdvise
    hipMemAdvise.restype = hipError_t
    hipMemAdvise.argtypes = [ctypes.POINTER(None), size_t, hipMemoryAdvise, ctypes.c_int32]
except AttributeError:
    pass
try:
    hipMemRangeGetAttribute = _libraries[LIB_HIP].hipMemRangeGetAttribute
    hipMemRangeGetAttribute.restype = hipError_t
    hipMemRangeGetAttribute.argtypes = [ctypes.POINTER(None), size_t, hipMemRangeAttribute, ctypes.POINTER(None), size_t]
except AttributeError:
    pass
try:
    hipMemRangeGetAttributes = _libraries[LIB_HIP].hipMemRangeGetAttributes
    hipMemRangeGetAttributes.restype = hipError_t
    hipMemRangeGetAttributes.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(hipMemRangeAttribute), size_t, ctypes.POINTER(None), size_t]
except AttributeError:
    pass
try:
    hipStreamAttachMemAsync = _libraries[LIB_HIP].hipStreamAttachMemAsync
    hipStreamAttachMemAsync.restype = hipError_t
    hipStreamAttachMemAsync.argtypes = [hipStream_t, ctypes.POINTER(None), size_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipMallocAsync = _libraries[LIB_HIP].hipMallocAsync
    hipMallocAsync.restype = hipError_t
    hipMallocAsync.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), size_t, hipStream_t]
except AttributeError:
    pass
try:
    hipFreeAsync = _libraries[LIB_HIP].hipFreeAsync
    hipFreeAsync.restype = hipError_t
    hipFreeAsync.argtypes = [ctypes.POINTER(None), hipStream_t]
except AttributeError:
    pass
try:
    hipMemPoolTrimTo = _libraries[LIB_HIP].hipMemPoolTrimTo
    hipMemPoolTrimTo.restype = hipError_t
    hipMemPoolTrimTo.argtypes = [hipMemPool_t, size_t]
except AttributeError:
    pass
try:
    hipMemPoolSetAttribute = _libraries[LIB_HIP].hipMemPoolSetAttribute
    hipMemPoolSetAttribute.restype = hipError_t
    hipMemPoolSetAttribute.argtypes = [hipMemPool_t, hipMemPoolAttr, ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipMemPoolGetAttribute = _libraries[LIB_HIP].hipMemPoolGetAttribute
    hipMemPoolGetAttribute.restype = hipError_t
    hipMemPoolGetAttribute.argtypes = [hipMemPool_t, hipMemPoolAttr, ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipMemPoolSetAccess = _libraries[LIB_HIP].hipMemPoolSetAccess
    hipMemPoolSetAccess.restype = hipError_t
    hipMemPoolSetAccess.argtypes = [hipMemPool_t, ctypes.POINTER(struct_hipMemAccessDesc), size_t]
except AttributeError:
    pass
try:
    hipMemPoolGetAccess = _libraries[LIB_HIP].hipMemPoolGetAccess
    hipMemPoolGetAccess.restype = hipError_t
    hipMemPoolGetAccess.argtypes = [ctypes.POINTER(hipMemAccessFlags), hipMemPool_t, ctypes.POINTER(struct_hipMemLocation)]
except AttributeError:
    pass
try:
    hipMemPoolCreate = _libraries[LIB_HIP].hipMemPoolCreate
    hipMemPoolCreate.restype = hipError_t
    hipMemPoolCreate.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipMemPoolHandle_t)), ctypes.POINTER(struct_hipMemPoolProps)]
except AttributeError:
    pass
try:
    hipMemPoolDestroy = _libraries[LIB_HIP].hipMemPoolDestroy
    hipMemPoolDestroy.restype = hipError_t
    hipMemPoolDestroy.argtypes = [hipMemPool_t]
except AttributeError:
    pass
try:
    hipMallocFromPoolAsync = _libraries[LIB_HIP].hipMallocFromPoolAsync
    hipMallocFromPoolAsync.restype = hipError_t
    hipMallocFromPoolAsync.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), size_t, hipMemPool_t, hipStream_t]
except AttributeError:
    pass
try:
    hipMemPoolExportToShareableHandle = _libraries[LIB_HIP].hipMemPoolExportToShareableHandle
    hipMemPoolExportToShareableHandle.restype = hipError_t
    hipMemPoolExportToShareableHandle.argtypes = [ctypes.POINTER(None), hipMemPool_t, hipMemAllocationHandleType, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipMemPoolImportFromShareableHandle = _libraries[LIB_HIP].hipMemPoolImportFromShareableHandle
    hipMemPoolImportFromShareableHandle.restype = hipError_t
    hipMemPoolImportFromShareableHandle.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipMemPoolHandle_t)), ctypes.POINTER(None), hipMemAllocationHandleType, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipMemPoolExportPointer = _libraries[LIB_HIP].hipMemPoolExportPointer
    hipMemPoolExportPointer.restype = hipError_t
    hipMemPoolExportPointer.argtypes = [ctypes.POINTER(struct_hipMemPoolPtrExportData), ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipMemPoolImportPointer = _libraries[LIB_HIP].hipMemPoolImportPointer
    hipMemPoolImportPointer.restype = hipError_t
    hipMemPoolImportPointer.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), hipMemPool_t, ctypes.POINTER(struct_hipMemPoolPtrExportData)]
except AttributeError:
    pass
try:
    hipHostAlloc = _libraries[LIB_HIP].hipHostAlloc
    hipHostAlloc.restype = hipError_t
    hipHostAlloc.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), size_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipHostGetDevicePointer = _libraries[LIB_HIP].hipHostGetDevicePointer
    hipHostGetDevicePointer.restype = hipError_t
    hipHostGetDevicePointer.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(None), ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipHostGetFlags = _libraries[LIB_HIP].hipHostGetFlags
    hipHostGetFlags.restype = hipError_t
    hipHostGetFlags.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipHostRegister = _libraries[LIB_HIP].hipHostRegister
    hipHostRegister.restype = hipError_t
    hipHostRegister.argtypes = [ctypes.POINTER(None), size_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipHostUnregister = _libraries[LIB_HIP].hipHostUnregister
    hipHostUnregister.restype = hipError_t
    hipHostUnregister.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipMallocPitch = _libraries[LIB_HIP].hipMallocPitch
    hipMallocPitch.restype = hipError_t
    hipMallocPitch.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(ctypes.c_uint64), size_t, size_t]
except AttributeError:
    pass
try:
    hipMemAllocPitch = _libraries[LIB_HIP].hipMemAllocPitch
    hipMemAllocPitch.restype = hipError_t
    hipMemAllocPitch.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(ctypes.c_uint64), size_t, size_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipFree = _libraries[LIB_HIP].hipFree
    hipFree.restype = hipError_t
    hipFree.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipFreeHost = _libraries[LIB_HIP].hipFreeHost
    hipFreeHost.restype = hipError_t
    hipFreeHost.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipHostFree = _libraries[LIB_HIP].hipHostFree
    hipHostFree.restype = hipError_t
    hipHostFree.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipMemcpy = _libraries[LIB_HIP].hipMemcpy
    hipMemcpy.restype = hipError_t
    hipMemcpy.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), size_t, hipMemcpyKind]
except AttributeError:
    pass
try:
    hipMemcpyWithStream = _libraries[LIB_HIP].hipMemcpyWithStream
    hipMemcpyWithStream.restype = hipError_t
    hipMemcpyWithStream.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), size_t, hipMemcpyKind, hipStream_t]
except AttributeError:
    pass
try:
    hipMemcpyHtoD = _libraries[LIB_HIP].hipMemcpyHtoD
    hipMemcpyHtoD.restype = hipError_t
    hipMemcpyHtoD.argtypes = [hipDeviceptr_t, ctypes.POINTER(None), size_t]
except AttributeError:
    pass
try:
    hipMemcpyDtoH = _libraries[LIB_HIP].hipMemcpyDtoH
    hipMemcpyDtoH.restype = hipError_t
    hipMemcpyDtoH.argtypes = [ctypes.POINTER(None), hipDeviceptr_t, size_t]
except AttributeError:
    pass
try:
    hipMemcpyDtoD = _libraries[LIB_HIP].hipMemcpyDtoD
    hipMemcpyDtoD.restype = hipError_t
    hipMemcpyDtoD.argtypes = [hipDeviceptr_t, hipDeviceptr_t, size_t]
except AttributeError:
    pass
try:
    hipMemcpyHtoDAsync = _libraries[LIB_HIP].hipMemcpyHtoDAsync
    hipMemcpyHtoDAsync.restype = hipError_t
    hipMemcpyHtoDAsync.argtypes = [hipDeviceptr_t, ctypes.POINTER(None), size_t, hipStream_t]
except AttributeError:
    pass
try:
    hipMemcpyDtoHAsync = _libraries[LIB_HIP].hipMemcpyDtoHAsync
    hipMemcpyDtoHAsync.restype = hipError_t
    hipMemcpyDtoHAsync.argtypes = [ctypes.POINTER(None), hipDeviceptr_t, size_t, hipStream_t]
except AttributeError:
    pass
try:
    hipMemcpyDtoDAsync = _libraries[LIB_HIP].hipMemcpyDtoDAsync
    hipMemcpyDtoDAsync.restype = hipError_t
    hipMemcpyDtoDAsync.argtypes = [hipDeviceptr_t, hipDeviceptr_t, size_t, hipStream_t]
except AttributeError:
    pass
try:
    hipModuleGetGlobal = _libraries[LIB_HIP].hipModuleGetGlobal
    hipModuleGetGlobal.restype = hipError_t
    hipModuleGetGlobal.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(ctypes.c_uint64), hipModule_t, ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    hipGetSymbolAddress = _libraries[LIB_HIP].hipGetSymbolAddress
    hipGetSymbolAddress.restype = hipError_t
    hipGetSymbolAddress.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipGetSymbolSize = _libraries[LIB_HIP].hipGetSymbolSize
    hipGetSymbolSize.restype = hipError_t
    hipGetSymbolSize.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipMemcpyToSymbol = _libraries[LIB_HIP].hipMemcpyToSymbol
    hipMemcpyToSymbol.restype = hipError_t
    hipMemcpyToSymbol.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), size_t, size_t, hipMemcpyKind]
except AttributeError:
    pass
try:
    hipMemcpyToSymbolAsync = _libraries[LIB_HIP].hipMemcpyToSymbolAsync
    hipMemcpyToSymbolAsync.restype = hipError_t
    hipMemcpyToSymbolAsync.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), size_t, size_t, hipMemcpyKind, hipStream_t]
except AttributeError:
    pass
try:
    hipMemcpyFromSymbol = _libraries[LIB_HIP].hipMemcpyFromSymbol
    hipMemcpyFromSymbol.restype = hipError_t
    hipMemcpyFromSymbol.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), size_t, size_t, hipMemcpyKind]
except AttributeError:
    pass
try:
    hipMemcpyFromSymbolAsync = _libraries[LIB_HIP].hipMemcpyFromSymbolAsync
    hipMemcpyFromSymbolAsync.restype = hipError_t
    hipMemcpyFromSymbolAsync.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), size_t, size_t, hipMemcpyKind, hipStream_t]
except AttributeError:
    pass
try:
    hipMemcpyAsync = _libraries[LIB_HIP].hipMemcpyAsync
    hipMemcpyAsync.restype = hipError_t
    hipMemcpyAsync.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), size_t, hipMemcpyKind, hipStream_t]
except AttributeError:
    pass
try:
    hipMemset = _libraries[LIB_HIP].hipMemset
    hipMemset.restype = hipError_t
    hipMemset.argtypes = [ctypes.POINTER(None), ctypes.c_int32, size_t]
except AttributeError:
    pass
try:
    hipMemsetD8 = _libraries[LIB_HIP].hipMemsetD8
    hipMemsetD8.restype = hipError_t
    hipMemsetD8.argtypes = [hipDeviceptr_t, ctypes.c_ubyte, size_t]
except AttributeError:
    pass
try:
    hipMemsetD8Async = _libraries[LIB_HIP].hipMemsetD8Async
    hipMemsetD8Async.restype = hipError_t
    hipMemsetD8Async.argtypes = [hipDeviceptr_t, ctypes.c_ubyte, size_t, hipStream_t]
except AttributeError:
    pass
try:
    hipMemsetD16 = _libraries[LIB_HIP].hipMemsetD16
    hipMemsetD16.restype = hipError_t
    hipMemsetD16.argtypes = [hipDeviceptr_t, ctypes.c_uint16, size_t]
except AttributeError:
    pass
try:
    hipMemsetD16Async = _libraries[LIB_HIP].hipMemsetD16Async
    hipMemsetD16Async.restype = hipError_t
    hipMemsetD16Async.argtypes = [hipDeviceptr_t, ctypes.c_uint16, size_t, hipStream_t]
except AttributeError:
    pass
try:
    hipMemsetD32 = _libraries[LIB_HIP].hipMemsetD32
    hipMemsetD32.restype = hipError_t
    hipMemsetD32.argtypes = [hipDeviceptr_t, ctypes.c_int32, size_t]
except AttributeError:
    pass
try:
    hipMemsetAsync = _libraries[LIB_HIP].hipMemsetAsync
    hipMemsetAsync.restype = hipError_t
    hipMemsetAsync.argtypes = [ctypes.POINTER(None), ctypes.c_int32, size_t, hipStream_t]
except AttributeError:
    pass
try:
    hipMemsetD32Async = _libraries[LIB_HIP].hipMemsetD32Async
    hipMemsetD32Async.restype = hipError_t
    hipMemsetD32Async.argtypes = [hipDeviceptr_t, ctypes.c_int32, size_t, hipStream_t]
except AttributeError:
    pass
try:
    hipMemset2D = _libraries[LIB_HIP].hipMemset2D
    hipMemset2D.restype = hipError_t
    hipMemset2D.argtypes = [ctypes.POINTER(None), size_t, ctypes.c_int32, size_t, size_t]
except AttributeError:
    pass
try:
    hipMemset2DAsync = _libraries[LIB_HIP].hipMemset2DAsync
    hipMemset2DAsync.restype = hipError_t
    hipMemset2DAsync.argtypes = [ctypes.POINTER(None), size_t, ctypes.c_int32, size_t, size_t, hipStream_t]
except AttributeError:
    pass
try:
    hipMemset3D = _libraries[LIB_HIP].hipMemset3D
    hipMemset3D.restype = hipError_t
    hipMemset3D.argtypes = [hipPitchedPtr, ctypes.c_int32, hipExtent]
except AttributeError:
    pass
try:
    hipMemset3DAsync = _libraries[LIB_HIP].hipMemset3DAsync
    hipMemset3DAsync.restype = hipError_t
    hipMemset3DAsync.argtypes = [hipPitchedPtr, ctypes.c_int32, hipExtent, hipStream_t]
except AttributeError:
    pass
try:
    hipMemGetInfo = _libraries[LIB_HIP].hipMemGetInfo
    hipMemGetInfo.restype = hipError_t
    hipMemGetInfo.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    hipMemPtrGetInfo = _libraries[LIB_HIP].hipMemPtrGetInfo
    hipMemPtrGetInfo.restype = hipError_t
    hipMemPtrGetInfo.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    hipMallocArray = _libraries[LIB_HIP].hipMallocArray
    hipMallocArray.restype = hipError_t
    hipMallocArray.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipArray)), ctypes.POINTER(struct_hipChannelFormatDesc), size_t, size_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipArrayCreate = _libraries[LIB_HIP].hipArrayCreate
    hipArrayCreate.restype = hipError_t
    hipArrayCreate.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipArray)), ctypes.POINTER(struct_HIP_ARRAY_DESCRIPTOR)]
except AttributeError:
    pass
try:
    hipArrayDestroy = _libraries[LIB_HIP].hipArrayDestroy
    hipArrayDestroy.restype = hipError_t
    hipArrayDestroy.argtypes = [ctypes.POINTER(struct_hipArray)]
except AttributeError:
    pass
try:
    hipArray3DCreate = _libraries[LIB_HIP].hipArray3DCreate
    hipArray3DCreate.restype = hipError_t
    hipArray3DCreate.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipArray)), ctypes.POINTER(struct_HIP_ARRAY3D_DESCRIPTOR)]
except AttributeError:
    pass
try:
    hipMalloc3D = _libraries[LIB_HIP].hipMalloc3D
    hipMalloc3D.restype = hipError_t
    hipMalloc3D.argtypes = [ctypes.POINTER(struct_hipPitchedPtr), hipExtent]
except AttributeError:
    pass
try:
    hipFreeArray = _libraries[LIB_HIP].hipFreeArray
    hipFreeArray.restype = hipError_t
    hipFreeArray.argtypes = [ctypes.POINTER(struct_hipArray)]
except AttributeError:
    pass
try:
    hipMalloc3DArray = _libraries[LIB_HIP].hipMalloc3DArray
    hipMalloc3DArray.restype = hipError_t
    hipMalloc3DArray.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipArray)), ctypes.POINTER(struct_hipChannelFormatDesc), struct_hipExtent, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipArrayGetInfo = _libraries[LIB_HIP].hipArrayGetInfo
    hipArrayGetInfo.restype = hipError_t
    hipArrayGetInfo.argtypes = [ctypes.POINTER(struct_hipChannelFormatDesc), ctypes.POINTER(struct_hipExtent), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(struct_hipArray)]
except AttributeError:
    pass
try:
    hipArrayGetDescriptor = _libraries[LIB_HIP].hipArrayGetDescriptor
    hipArrayGetDescriptor.restype = hipError_t
    hipArrayGetDescriptor.argtypes = [ctypes.POINTER(struct_HIP_ARRAY_DESCRIPTOR), ctypes.POINTER(struct_hipArray)]
except AttributeError:
    pass
try:
    hipArray3DGetDescriptor = _libraries[LIB_HIP].hipArray3DGetDescriptor
    hipArray3DGetDescriptor.restype = hipError_t
    hipArray3DGetDescriptor.argtypes = [ctypes.POINTER(struct_HIP_ARRAY3D_DESCRIPTOR), ctypes.POINTER(struct_hipArray)]
except AttributeError:
    pass
try:
    hipMemcpy2D = _libraries[LIB_HIP].hipMemcpy2D
    hipMemcpy2D.restype = hipError_t
    hipMemcpy2D.argtypes = [ctypes.POINTER(None), size_t, ctypes.POINTER(None), size_t, size_t, size_t, hipMemcpyKind]
except AttributeError:
    pass
try:
    hipMemcpyParam2D = _libraries[LIB_HIP].hipMemcpyParam2D
    hipMemcpyParam2D.restype = hipError_t
    hipMemcpyParam2D.argtypes = [ctypes.POINTER(struct_hip_Memcpy2D)]
except AttributeError:
    pass
try:
    hipMemcpyParam2DAsync = _libraries[LIB_HIP].hipMemcpyParam2DAsync
    hipMemcpyParam2DAsync.restype = hipError_t
    hipMemcpyParam2DAsync.argtypes = [ctypes.POINTER(struct_hip_Memcpy2D), hipStream_t]
except AttributeError:
    pass
try:
    hipMemcpy2DAsync = _libraries[LIB_HIP].hipMemcpy2DAsync
    hipMemcpy2DAsync.restype = hipError_t
    hipMemcpy2DAsync.argtypes = [ctypes.POINTER(None), size_t, ctypes.POINTER(None), size_t, size_t, size_t, hipMemcpyKind, hipStream_t]
except AttributeError:
    pass
try:
    hipMemcpy2DToArray = _libraries[LIB_HIP].hipMemcpy2DToArray
    hipMemcpy2DToArray.restype = hipError_t
    hipMemcpy2DToArray.argtypes = [ctypes.POINTER(struct_hipArray), size_t, size_t, ctypes.POINTER(None), size_t, size_t, size_t, hipMemcpyKind]
except AttributeError:
    pass
try:
    hipMemcpy2DToArrayAsync = _libraries[LIB_HIP].hipMemcpy2DToArrayAsync
    hipMemcpy2DToArrayAsync.restype = hipError_t
    hipMemcpy2DToArrayAsync.argtypes = [ctypes.POINTER(struct_hipArray), size_t, size_t, ctypes.POINTER(None), size_t, size_t, size_t, hipMemcpyKind, hipStream_t]
except AttributeError:
    pass
try:
    hipMemcpyToArray = _libraries[LIB_HIP].hipMemcpyToArray
    hipMemcpyToArray.restype = hipError_t
    hipMemcpyToArray.argtypes = [ctypes.POINTER(struct_hipArray), size_t, size_t, ctypes.POINTER(None), size_t, hipMemcpyKind]
except AttributeError:
    pass
try:
    hipMemcpyFromArray = _libraries[LIB_HIP].hipMemcpyFromArray
    hipMemcpyFromArray.restype = hipError_t
    hipMemcpyFromArray.argtypes = [ctypes.POINTER(None), hipArray_const_t, size_t, size_t, size_t, hipMemcpyKind]
except AttributeError:
    pass
try:
    hipMemcpy2DFromArray = _libraries[LIB_HIP].hipMemcpy2DFromArray
    hipMemcpy2DFromArray.restype = hipError_t
    hipMemcpy2DFromArray.argtypes = [ctypes.POINTER(None), size_t, hipArray_const_t, size_t, size_t, size_t, size_t, hipMemcpyKind]
except AttributeError:
    pass
try:
    hipMemcpy2DFromArrayAsync = _libraries[LIB_HIP].hipMemcpy2DFromArrayAsync
    hipMemcpy2DFromArrayAsync.restype = hipError_t
    hipMemcpy2DFromArrayAsync.argtypes = [ctypes.POINTER(None), size_t, hipArray_const_t, size_t, size_t, size_t, size_t, hipMemcpyKind, hipStream_t]
except AttributeError:
    pass
try:
    hipMemcpyAtoH = _libraries[LIB_HIP].hipMemcpyAtoH
    hipMemcpyAtoH.restype = hipError_t
    hipMemcpyAtoH.argtypes = [ctypes.POINTER(None), ctypes.POINTER(struct_hipArray), size_t, size_t]
except AttributeError:
    pass
try:
    hipMemcpyHtoA = _libraries[LIB_HIP].hipMemcpyHtoA
    hipMemcpyHtoA.restype = hipError_t
    hipMemcpyHtoA.argtypes = [ctypes.POINTER(struct_hipArray), size_t, ctypes.POINTER(None), size_t]
except AttributeError:
    pass
try:
    hipMemcpy3D = _libraries[LIB_HIP].hipMemcpy3D
    hipMemcpy3D.restype = hipError_t
    hipMemcpy3D.argtypes = [ctypes.POINTER(struct_hipMemcpy3DParms)]
except AttributeError:
    pass
try:
    hipMemcpy3DAsync = _libraries[LIB_HIP].hipMemcpy3DAsync
    hipMemcpy3DAsync.restype = hipError_t
    hipMemcpy3DAsync.argtypes = [ctypes.POINTER(struct_hipMemcpy3DParms), hipStream_t]
except AttributeError:
    pass
try:
    hipDrvMemcpy3D = _libraries[LIB_HIP].hipDrvMemcpy3D
    hipDrvMemcpy3D.restype = hipError_t
    hipDrvMemcpy3D.argtypes = [ctypes.POINTER(struct_HIP_MEMCPY3D)]
except AttributeError:
    pass
try:
    hipDrvMemcpy3DAsync = _libraries[LIB_HIP].hipDrvMemcpy3DAsync
    hipDrvMemcpy3DAsync.restype = hipError_t
    hipDrvMemcpy3DAsync.argtypes = [ctypes.POINTER(struct_HIP_MEMCPY3D), hipStream_t]
except AttributeError:
    pass
try:
    hipDeviceCanAccessPeer = _libraries[LIB_HIP].hipDeviceCanAccessPeer
    hipDeviceCanAccessPeer.restype = hipError_t
    hipDeviceCanAccessPeer.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.c_int32, ctypes.c_int32]
except AttributeError:
    pass
try:
    hipDeviceEnablePeerAccess = _libraries[LIB_HIP].hipDeviceEnablePeerAccess
    hipDeviceEnablePeerAccess.restype = hipError_t
    hipDeviceEnablePeerAccess.argtypes = [ctypes.c_int32, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipDeviceDisablePeerAccess = _libraries[LIB_HIP].hipDeviceDisablePeerAccess
    hipDeviceDisablePeerAccess.restype = hipError_t
    hipDeviceDisablePeerAccess.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    hipMemGetAddressRange = _libraries[LIB_HIP].hipMemGetAddressRange
    hipMemGetAddressRange.restype = hipError_t
    hipMemGetAddressRange.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(ctypes.c_uint64), hipDeviceptr_t]
except AttributeError:
    pass
try:
    hipMemcpyPeer = _libraries[LIB_HIP].hipMemcpyPeer
    hipMemcpyPeer.restype = hipError_t
    hipMemcpyPeer.argtypes = [ctypes.POINTER(None), ctypes.c_int32, ctypes.POINTER(None), ctypes.c_int32, size_t]
except AttributeError:
    pass
try:
    hipMemcpyPeerAsync = _libraries[LIB_HIP].hipMemcpyPeerAsync
    hipMemcpyPeerAsync.restype = hipError_t
    hipMemcpyPeerAsync.argtypes = [ctypes.POINTER(None), ctypes.c_int32, ctypes.POINTER(None), ctypes.c_int32, size_t, hipStream_t]
except AttributeError:
    pass
try:
    hipCtxCreate = _libraries[LIB_HIP].hipCtxCreate
    hipCtxCreate.restype = hipError_t
    hipCtxCreate.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipCtx_t)), ctypes.c_uint32, hipDevice_t]
except AttributeError:
    pass
try:
    hipCtxDestroy = _libraries[LIB_HIP].hipCtxDestroy
    hipCtxDestroy.restype = hipError_t
    hipCtxDestroy.argtypes = [hipCtx_t]
except AttributeError:
    pass
try:
    hipCtxPopCurrent = _libraries[LIB_HIP].hipCtxPopCurrent
    hipCtxPopCurrent.restype = hipError_t
    hipCtxPopCurrent.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipCtx_t))]
except AttributeError:
    pass
try:
    hipCtxPushCurrent = _libraries[LIB_HIP].hipCtxPushCurrent
    hipCtxPushCurrent.restype = hipError_t
    hipCtxPushCurrent.argtypes = [hipCtx_t]
except AttributeError:
    pass
try:
    hipCtxSetCurrent = _libraries[LIB_HIP].hipCtxSetCurrent
    hipCtxSetCurrent.restype = hipError_t
    hipCtxSetCurrent.argtypes = [hipCtx_t]
except AttributeError:
    pass
try:
    hipCtxGetCurrent = _libraries[LIB_HIP].hipCtxGetCurrent
    hipCtxGetCurrent.restype = hipError_t
    hipCtxGetCurrent.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipCtx_t))]
except AttributeError:
    pass
try:
    hipCtxGetDevice = _libraries[LIB_HIP].hipCtxGetDevice
    hipCtxGetDevice.restype = hipError_t
    hipCtxGetDevice.argtypes = [ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
try:
    hipCtxGetApiVersion = _libraries[LIB_HIP].hipCtxGetApiVersion
    hipCtxGetApiVersion.restype = hipError_t
    hipCtxGetApiVersion.argtypes = [hipCtx_t, ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
try:
    hipCtxGetCacheConfig = _libraries[LIB_HIP].hipCtxGetCacheConfig
    hipCtxGetCacheConfig.restype = hipError_t
    hipCtxGetCacheConfig.argtypes = [ctypes.POINTER(hipFuncCache_t)]
except AttributeError:
    pass
try:
    hipCtxSetCacheConfig = _libraries[LIB_HIP].hipCtxSetCacheConfig
    hipCtxSetCacheConfig.restype = hipError_t
    hipCtxSetCacheConfig.argtypes = [hipFuncCache_t]
except AttributeError:
    pass
try:
    hipCtxSetSharedMemConfig = _libraries[LIB_HIP].hipCtxSetSharedMemConfig
    hipCtxSetSharedMemConfig.restype = hipError_t
    hipCtxSetSharedMemConfig.argtypes = [hipSharedMemConfig]
except AttributeError:
    pass
try:
    hipCtxGetSharedMemConfig = _libraries[LIB_HIP].hipCtxGetSharedMemConfig
    hipCtxGetSharedMemConfig.restype = hipError_t
    hipCtxGetSharedMemConfig.argtypes = [ctypes.POINTER(hipSharedMemConfig)]
except AttributeError:
    pass
try:
    hipCtxSynchronize = _libraries[LIB_HIP].hipCtxSynchronize
    hipCtxSynchronize.restype = hipError_t
    hipCtxSynchronize.argtypes = []
except AttributeError:
    pass
try:
    hipCtxGetFlags = _libraries[LIB_HIP].hipCtxGetFlags
    hipCtxGetFlags.restype = hipError_t
    hipCtxGetFlags.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    hipCtxEnablePeerAccess = _libraries[LIB_HIP].hipCtxEnablePeerAccess
    hipCtxEnablePeerAccess.restype = hipError_t
    hipCtxEnablePeerAccess.argtypes = [hipCtx_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipCtxDisablePeerAccess = _libraries[LIB_HIP].hipCtxDisablePeerAccess
    hipCtxDisablePeerAccess.restype = hipError_t
    hipCtxDisablePeerAccess.argtypes = [hipCtx_t]
except AttributeError:
    pass
try:
    hipDevicePrimaryCtxGetState = _libraries[LIB_HIP].hipDevicePrimaryCtxGetState
    hipDevicePrimaryCtxGetState.restype = hipError_t
    hipDevicePrimaryCtxGetState.argtypes = [hipDevice_t, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
try:
    hipDevicePrimaryCtxRelease = _libraries[LIB_HIP].hipDevicePrimaryCtxRelease
    hipDevicePrimaryCtxRelease.restype = hipError_t
    hipDevicePrimaryCtxRelease.argtypes = [hipDevice_t]
except AttributeError:
    pass
try:
    hipDevicePrimaryCtxRetain = _libraries[LIB_HIP].hipDevicePrimaryCtxRetain
    hipDevicePrimaryCtxRetain.restype = hipError_t
    hipDevicePrimaryCtxRetain.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipCtx_t)), hipDevice_t]
except AttributeError:
    pass
try:
    hipDevicePrimaryCtxReset = _libraries[LIB_HIP].hipDevicePrimaryCtxReset
    hipDevicePrimaryCtxReset.restype = hipError_t
    hipDevicePrimaryCtxReset.argtypes = [hipDevice_t]
except AttributeError:
    pass
try:
    hipDevicePrimaryCtxSetFlags = _libraries[LIB_HIP].hipDevicePrimaryCtxSetFlags
    hipDevicePrimaryCtxSetFlags.restype = hipError_t
    hipDevicePrimaryCtxSetFlags.argtypes = [hipDevice_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipModuleLoad = _libraries[LIB_HIP].hipModuleLoad
    hipModuleLoad.restype = hipError_t
    hipModuleLoad.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipModule_t)), ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    hipModuleUnload = _libraries[LIB_HIP].hipModuleUnload
    hipModuleUnload.restype = hipError_t
    hipModuleUnload.argtypes = [hipModule_t]
except AttributeError:
    pass
try:
    hipModuleGetFunction = _libraries[LIB_HIP].hipModuleGetFunction
    hipModuleGetFunction.restype = hipError_t
    hipModuleGetFunction.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipModuleSymbol_t)), hipModule_t, ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    hipFuncGetAttributes = _libraries[LIB_HIP].hipFuncGetAttributes
    hipFuncGetAttributes.restype = hipError_t
    hipFuncGetAttributes.argtypes = [ctypes.POINTER(struct_hipFuncAttributes), ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipFuncGetAttribute = _libraries[LIB_HIP].hipFuncGetAttribute
    hipFuncGetAttribute.restype = hipError_t
    hipFuncGetAttribute.argtypes = [ctypes.POINTER(ctypes.c_int32), hipFunction_attribute, hipFunction_t]
except AttributeError:
    pass
class struct_textureReference(Structure):
    pass

class struct___hip_texture(Structure):
    pass


# values for enumeration 'hipTextureReadMode'
hipTextureReadMode__enumvalues = {
    0: 'hipReadModeElementType',
    1: 'hipReadModeNormalizedFloat',
}
hipReadModeElementType = 0
hipReadModeNormalizedFloat = 1
hipTextureReadMode = ctypes.c_uint32 # enum

# values for enumeration 'hipTextureFilterMode'
hipTextureFilterMode__enumvalues = {
    0: 'hipFilterModePoint',
    1: 'hipFilterModeLinear',
}
hipFilterModePoint = 0
hipFilterModeLinear = 1
hipTextureFilterMode = ctypes.c_uint32 # enum

# values for enumeration 'hipTextureAddressMode'
hipTextureAddressMode__enumvalues = {
    0: 'hipAddressModeWrap',
    1: 'hipAddressModeClamp',
    2: 'hipAddressModeMirror',
    3: 'hipAddressModeBorder',
}
hipAddressModeWrap = 0
hipAddressModeClamp = 1
hipAddressModeMirror = 2
hipAddressModeBorder = 3
hipTextureAddressMode = ctypes.c_uint32 # enum
struct_textureReference._pack_ = 1 # source:False
struct_textureReference._fields_ = [
    ('normalized', ctypes.c_int32),
    ('readMode', hipTextureReadMode),
    ('filterMode', hipTextureFilterMode),
    ('addressMode', hipTextureAddressMode * 3),
    ('channelDesc', struct_hipChannelFormatDesc),
    ('sRGB', ctypes.c_int32),
    ('maxAnisotropy', ctypes.c_uint32),
    ('mipmapFilterMode', hipTextureFilterMode),
    ('mipmapLevelBias', ctypes.c_float),
    ('minMipmapLevelClamp', ctypes.c_float),
    ('maxMipmapLevelClamp', ctypes.c_float),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('textureObject', ctypes.POINTER(struct___hip_texture)),
    ('numChannels', ctypes.c_int32),
    ('format', hipArray_Format),
]

try:
    hipModuleGetTexRef = _libraries[LIB_HIP].hipModuleGetTexRef
    hipModuleGetTexRef.restype = hipError_t
    hipModuleGetTexRef.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_textureReference)), hipModule_t, ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    hipModuleLoadData = _libraries[LIB_HIP].hipModuleLoadData
    hipModuleLoadData.restype = hipError_t
    hipModuleLoadData.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipModule_t)), ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipModuleLoadDataEx = _libraries[LIB_HIP].hipModuleLoadDataEx
    hipModuleLoadDataEx.restype = hipError_t
    hipModuleLoadDataEx.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipModule_t)), ctypes.POINTER(None), ctypes.c_uint32, ctypes.POINTER(hipJitOption), ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    hipModuleLaunchKernel = _libraries[LIB_HIP].hipModuleLaunchKernel
    hipModuleLaunchKernel.restype = hipError_t
    hipModuleLaunchKernel.argtypes = [hipFunction_t, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, hipStream_t, ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    hipModuleLaunchCooperativeKernel = _libraries[LIB_HIP].hipModuleLaunchCooperativeKernel
    hipModuleLaunchCooperativeKernel.restype = hipError_t
    hipModuleLaunchCooperativeKernel.argtypes = [hipFunction_t, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, hipStream_t, ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    hipModuleLaunchCooperativeKernelMultiDevice = _libraries[LIB_HIP].hipModuleLaunchCooperativeKernelMultiDevice
    hipModuleLaunchCooperativeKernelMultiDevice.restype = hipError_t
    hipModuleLaunchCooperativeKernelMultiDevice.argtypes = [ctypes.POINTER(struct_hipFunctionLaunchParams_t), ctypes.c_uint32, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipLaunchCooperativeKernel = _libraries[LIB_HIP].hipLaunchCooperativeKernel
    hipLaunchCooperativeKernel.restype = hipError_t
    hipLaunchCooperativeKernel.argtypes = [ctypes.POINTER(None), dim3, dim3, ctypes.POINTER(ctypes.POINTER(None)), ctypes.c_uint32, hipStream_t]
except AttributeError:
    pass
try:
    hipLaunchCooperativeKernelMultiDevice = _libraries[LIB_HIP].hipLaunchCooperativeKernelMultiDevice
    hipLaunchCooperativeKernelMultiDevice.restype = hipError_t
    hipLaunchCooperativeKernelMultiDevice.argtypes = [ctypes.POINTER(struct_hipLaunchParams_t), ctypes.c_int32, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipExtLaunchMultiKernelMultiDevice = _libraries[LIB_HIP].hipExtLaunchMultiKernelMultiDevice
    hipExtLaunchMultiKernelMultiDevice.restype = hipError_t
    hipExtLaunchMultiKernelMultiDevice.argtypes = [ctypes.POINTER(struct_hipLaunchParams_t), ctypes.c_int32, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipModuleOccupancyMaxPotentialBlockSize = _libraries[LIB_HIP].hipModuleOccupancyMaxPotentialBlockSize
    hipModuleOccupancyMaxPotentialBlockSize.restype = hipError_t
    hipModuleOccupancyMaxPotentialBlockSize.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32), hipFunction_t, size_t, ctypes.c_int32]
except AttributeError:
    pass
try:
    hipModuleOccupancyMaxPotentialBlockSizeWithFlags = _libraries[LIB_HIP].hipModuleOccupancyMaxPotentialBlockSizeWithFlags
    hipModuleOccupancyMaxPotentialBlockSizeWithFlags.restype = hipError_t
    hipModuleOccupancyMaxPotentialBlockSizeWithFlags.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32), hipFunction_t, size_t, ctypes.c_int32, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipModuleOccupancyMaxActiveBlocksPerMultiprocessor = _libraries[LIB_HIP].hipModuleOccupancyMaxActiveBlocksPerMultiprocessor
    hipModuleOccupancyMaxActiveBlocksPerMultiprocessor.restype = hipError_t
    hipModuleOccupancyMaxActiveBlocksPerMultiprocessor.argtypes = [ctypes.POINTER(ctypes.c_int32), hipFunction_t, ctypes.c_int32, size_t]
except AttributeError:
    pass
try:
    hipModuleOccupancyMaxActiveBlocksPerMultiprocessorWithFlags = _libraries[LIB_HIP].hipModuleOccupancyMaxActiveBlocksPerMultiprocessorWithFlags
    hipModuleOccupancyMaxActiveBlocksPerMultiprocessorWithFlags.restype = hipError_t
    hipModuleOccupancyMaxActiveBlocksPerMultiprocessorWithFlags.argtypes = [ctypes.POINTER(ctypes.c_int32), hipFunction_t, ctypes.c_int32, size_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipOccupancyMaxActiveBlocksPerMultiprocessor = _libraries[LIB_HIP].hipOccupancyMaxActiveBlocksPerMultiprocessor
    hipOccupancyMaxActiveBlocksPerMultiprocessor.restype = hipError_t
    hipOccupancyMaxActiveBlocksPerMultiprocessor.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(None), ctypes.c_int32, size_t]
except AttributeError:
    pass
try:
    hipOccupancyMaxActiveBlocksPerMultiprocessorWithFlags = _libraries[LIB_HIP].hipOccupancyMaxActiveBlocksPerMultiprocessorWithFlags
    hipOccupancyMaxActiveBlocksPerMultiprocessorWithFlags.restype = hipError_t
    hipOccupancyMaxActiveBlocksPerMultiprocessorWithFlags.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(None), ctypes.c_int32, size_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipOccupancyMaxPotentialBlockSize = _libraries[LIB_HIP].hipOccupancyMaxPotentialBlockSize
    hipOccupancyMaxPotentialBlockSize.restype = hipError_t
    hipOccupancyMaxPotentialBlockSize.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(None), size_t, ctypes.c_int32]
except AttributeError:
    pass
try:
    hipProfilerStart = _libraries[LIB_HIP].hipProfilerStart
    hipProfilerStart.restype = hipError_t
    hipProfilerStart.argtypes = []
except AttributeError:
    pass
try:
    hipProfilerStop = _libraries[LIB_HIP].hipProfilerStop
    hipProfilerStop.restype = hipError_t
    hipProfilerStop.argtypes = []
except AttributeError:
    pass
try:
    hipConfigureCall = _libraries[LIB_HIP].hipConfigureCall
    hipConfigureCall.restype = hipError_t
    hipConfigureCall.argtypes = [dim3, dim3, size_t, hipStream_t]
except AttributeError:
    pass
try:
    hipSetupArgument = _libraries[LIB_HIP].hipSetupArgument
    hipSetupArgument.restype = hipError_t
    hipSetupArgument.argtypes = [ctypes.POINTER(None), size_t, size_t]
except AttributeError:
    pass
try:
    hipLaunchByPtr = _libraries[LIB_HIP].hipLaunchByPtr
    hipLaunchByPtr.restype = hipError_t
    hipLaunchByPtr.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    __hipPushCallConfiguration = _libraries[LIB_HIP].__hipPushCallConfiguration
    __hipPushCallConfiguration.restype = hipError_t
    __hipPushCallConfiguration.argtypes = [dim3, dim3, size_t, hipStream_t]
except AttributeError:
    pass
try:
    __hipPopCallConfiguration = _libraries[LIB_HIP].__hipPopCallConfiguration
    __hipPopCallConfiguration.restype = hipError_t
    __hipPopCallConfiguration.argtypes = [ctypes.POINTER(struct_dim3), ctypes.POINTER(struct_dim3), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.POINTER(struct_ihipStream_t))]
except AttributeError:
    pass
try:
    hipLaunchKernel = _libraries[LIB_HIP].hipLaunchKernel
    hipLaunchKernel.restype = hipError_t
    hipLaunchKernel.argtypes = [ctypes.POINTER(None), dim3, dim3, ctypes.POINTER(ctypes.POINTER(None)), size_t, hipStream_t]
except AttributeError:
    pass
try:
    hipLaunchHostFunc = _libraries[LIB_HIP].hipLaunchHostFunc
    hipLaunchHostFunc.restype = hipError_t
    hipLaunchHostFunc.argtypes = [hipStream_t, hipHostFn_t, ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipDrvMemcpy2DUnaligned = _libraries[LIB_HIP].hipDrvMemcpy2DUnaligned
    hipDrvMemcpy2DUnaligned.restype = hipError_t
    hipDrvMemcpy2DUnaligned.argtypes = [ctypes.POINTER(struct_hip_Memcpy2D)]
except AttributeError:
    pass
try:
    hipExtLaunchKernel = _libraries[LIB_HIP].hipExtLaunchKernel
    hipExtLaunchKernel.restype = hipError_t
    hipExtLaunchKernel.argtypes = [ctypes.POINTER(None), dim3, dim3, ctypes.POINTER(ctypes.POINTER(None)), size_t, hipStream_t, hipEvent_t, hipEvent_t, ctypes.c_int32]
except AttributeError:
    pass
class struct_hipTextureDesc(Structure):
    pass

struct_hipTextureDesc._pack_ = 1 # source:False
struct_hipTextureDesc._fields_ = [
    ('addressMode', hipTextureAddressMode * 3),
    ('filterMode', hipTextureFilterMode),
    ('readMode', hipTextureReadMode),
    ('sRGB', ctypes.c_int32),
    ('borderColor', ctypes.c_float * 4),
    ('normalizedCoords', ctypes.c_int32),
    ('maxAnisotropy', ctypes.c_uint32),
    ('mipmapFilterMode', hipTextureFilterMode),
    ('mipmapLevelBias', ctypes.c_float),
    ('minMipmapLevelClamp', ctypes.c_float),
    ('maxMipmapLevelClamp', ctypes.c_float),
]

try:
    hipCreateTextureObject = _libraries[LIB_HIP].hipCreateTextureObject
    hipCreateTextureObject.restype = hipError_t
    hipCreateTextureObject.argtypes = [ctypes.POINTER(ctypes.POINTER(struct___hip_texture)), ctypes.POINTER(struct_hipResourceDesc), ctypes.POINTER(struct_hipTextureDesc), ctypes.POINTER(struct_hipResourceViewDesc)]
except AttributeError:
    pass
hipTextureObject_t = ctypes.POINTER(struct___hip_texture)
try:
    hipDestroyTextureObject = _libraries[LIB_HIP].hipDestroyTextureObject
    hipDestroyTextureObject.restype = hipError_t
    hipDestroyTextureObject.argtypes = [hipTextureObject_t]
except AttributeError:
    pass
try:
    hipGetChannelDesc = _libraries[LIB_HIP].hipGetChannelDesc
    hipGetChannelDesc.restype = hipError_t
    hipGetChannelDesc.argtypes = [ctypes.POINTER(struct_hipChannelFormatDesc), hipArray_const_t]
except AttributeError:
    pass
try:
    hipGetTextureObjectResourceDesc = _libraries[LIB_HIP].hipGetTextureObjectResourceDesc
    hipGetTextureObjectResourceDesc.restype = hipError_t
    hipGetTextureObjectResourceDesc.argtypes = [ctypes.POINTER(struct_hipResourceDesc), hipTextureObject_t]
except AttributeError:
    pass
try:
    hipGetTextureObjectResourceViewDesc = _libraries[LIB_HIP].hipGetTextureObjectResourceViewDesc
    hipGetTextureObjectResourceViewDesc.restype = hipError_t
    hipGetTextureObjectResourceViewDesc.argtypes = [ctypes.POINTER(struct_hipResourceViewDesc), hipTextureObject_t]
except AttributeError:
    pass
try:
    hipGetTextureObjectTextureDesc = _libraries[LIB_HIP].hipGetTextureObjectTextureDesc
    hipGetTextureObjectTextureDesc.restype = hipError_t
    hipGetTextureObjectTextureDesc.argtypes = [ctypes.POINTER(struct_hipTextureDesc), hipTextureObject_t]
except AttributeError:
    pass
try:
    hipTexObjectCreate = _libraries[LIB_HIP].hipTexObjectCreate
    hipTexObjectCreate.restype = hipError_t
    hipTexObjectCreate.argtypes = [ctypes.POINTER(ctypes.POINTER(struct___hip_texture)), ctypes.POINTER(struct_HIP_RESOURCE_DESC_st), ctypes.POINTER(struct_HIP_TEXTURE_DESC_st), ctypes.POINTER(struct_HIP_RESOURCE_VIEW_DESC_st)]
except AttributeError:
    pass
try:
    hipTexObjectDestroy = _libraries[LIB_HIP].hipTexObjectDestroy
    hipTexObjectDestroy.restype = hipError_t
    hipTexObjectDestroy.argtypes = [hipTextureObject_t]
except AttributeError:
    pass
try:
    hipTexObjectGetResourceDesc = _libraries[LIB_HIP].hipTexObjectGetResourceDesc
    hipTexObjectGetResourceDesc.restype = hipError_t
    hipTexObjectGetResourceDesc.argtypes = [ctypes.POINTER(struct_HIP_RESOURCE_DESC_st), hipTextureObject_t]
except AttributeError:
    pass
try:
    hipTexObjectGetResourceViewDesc = _libraries[LIB_HIP].hipTexObjectGetResourceViewDesc
    hipTexObjectGetResourceViewDesc.restype = hipError_t
    hipTexObjectGetResourceViewDesc.argtypes = [ctypes.POINTER(struct_HIP_RESOURCE_VIEW_DESC_st), hipTextureObject_t]
except AttributeError:
    pass
try:
    hipTexObjectGetTextureDesc = _libraries[LIB_HIP].hipTexObjectGetTextureDesc
    hipTexObjectGetTextureDesc.restype = hipError_t
    hipTexObjectGetTextureDesc.argtypes = [ctypes.POINTER(struct_HIP_TEXTURE_DESC_st), hipTextureObject_t]
except AttributeError:
    pass
try:
    hipMallocMipmappedArray = _libraries[LIB_HIP].hipMallocMipmappedArray
    hipMallocMipmappedArray.restype = hipError_t
    hipMallocMipmappedArray.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipMipmappedArray)), ctypes.POINTER(struct_hipChannelFormatDesc), struct_hipExtent, ctypes.c_uint32, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipFreeMipmappedArray = _libraries[LIB_HIP].hipFreeMipmappedArray
    hipFreeMipmappedArray.restype = hipError_t
    hipFreeMipmappedArray.argtypes = [hipMipmappedArray_t]
except AttributeError:
    pass
try:
    hipGetMipmappedArrayLevel = _libraries[LIB_HIP].hipGetMipmappedArrayLevel
    hipGetMipmappedArrayLevel.restype = hipError_t
    hipGetMipmappedArrayLevel.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipArray)), hipMipmappedArray_const_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipMipmappedArrayCreate = _libraries[LIB_HIP].hipMipmappedArrayCreate
    hipMipmappedArrayCreate.restype = hipError_t
    hipMipmappedArrayCreate.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipMipmappedArray)), ctypes.POINTER(struct_HIP_ARRAY3D_DESCRIPTOR), ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipMipmappedArrayDestroy = _libraries[LIB_HIP].hipMipmappedArrayDestroy
    hipMipmappedArrayDestroy.restype = hipError_t
    hipMipmappedArrayDestroy.argtypes = [hipMipmappedArray_t]
except AttributeError:
    pass
try:
    hipMipmappedArrayGetLevel = _libraries[LIB_HIP].hipMipmappedArrayGetLevel
    hipMipmappedArrayGetLevel.restype = hipError_t
    hipMipmappedArrayGetLevel.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipArray)), hipMipmappedArray_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipBindTextureToMipmappedArray = _libraries[LIB_HIP].hipBindTextureToMipmappedArray
    hipBindTextureToMipmappedArray.restype = hipError_t
    hipBindTextureToMipmappedArray.argtypes = [ctypes.POINTER(struct_textureReference), hipMipmappedArray_const_t, ctypes.POINTER(struct_hipChannelFormatDesc)]
except AttributeError:
    pass
try:
    hipGetTextureReference = _libraries[LIB_HIP].hipGetTextureReference
    hipGetTextureReference.restype = hipError_t
    hipGetTextureReference.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_textureReference)), ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipTexRefSetAddressMode = _libraries[LIB_HIP].hipTexRefSetAddressMode
    hipTexRefSetAddressMode.restype = hipError_t
    hipTexRefSetAddressMode.argtypes = [ctypes.POINTER(struct_textureReference), ctypes.c_int32, hipTextureAddressMode]
except AttributeError:
    pass
try:
    hipTexRefSetArray = _libraries[LIB_HIP].hipTexRefSetArray
    hipTexRefSetArray.restype = hipError_t
    hipTexRefSetArray.argtypes = [ctypes.POINTER(struct_textureReference), hipArray_const_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipTexRefSetFilterMode = _libraries[LIB_HIP].hipTexRefSetFilterMode
    hipTexRefSetFilterMode.restype = hipError_t
    hipTexRefSetFilterMode.argtypes = [ctypes.POINTER(struct_textureReference), hipTextureFilterMode]
except AttributeError:
    pass
try:
    hipTexRefSetFlags = _libraries[LIB_HIP].hipTexRefSetFlags
    hipTexRefSetFlags.restype = hipError_t
    hipTexRefSetFlags.argtypes = [ctypes.POINTER(struct_textureReference), ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipTexRefSetFormat = _libraries[LIB_HIP].hipTexRefSetFormat
    hipTexRefSetFormat.restype = hipError_t
    hipTexRefSetFormat.argtypes = [ctypes.POINTER(struct_textureReference), hipArray_Format, ctypes.c_int32]
except AttributeError:
    pass
try:
    hipBindTexture = _libraries[LIB_HIP].hipBindTexture
    hipBindTexture.restype = hipError_t
    hipBindTexture.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(struct_textureReference), ctypes.POINTER(None), ctypes.POINTER(struct_hipChannelFormatDesc), size_t]
except AttributeError:
    pass
try:
    hipBindTexture2D = _libraries[LIB_HIP].hipBindTexture2D
    hipBindTexture2D.restype = hipError_t
    hipBindTexture2D.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(struct_textureReference), ctypes.POINTER(None), ctypes.POINTER(struct_hipChannelFormatDesc), size_t, size_t, size_t]
except AttributeError:
    pass
try:
    hipBindTextureToArray = _libraries[LIB_HIP].hipBindTextureToArray
    hipBindTextureToArray.restype = hipError_t
    hipBindTextureToArray.argtypes = [ctypes.POINTER(struct_textureReference), hipArray_const_t, ctypes.POINTER(struct_hipChannelFormatDesc)]
except AttributeError:
    pass
try:
    hipGetTextureAlignmentOffset = _libraries[LIB_HIP].hipGetTextureAlignmentOffset
    hipGetTextureAlignmentOffset.restype = hipError_t
    hipGetTextureAlignmentOffset.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(struct_textureReference)]
except AttributeError:
    pass
try:
    hipUnbindTexture = _libraries[LIB_HIP].hipUnbindTexture
    hipUnbindTexture.restype = hipError_t
    hipUnbindTexture.argtypes = [ctypes.POINTER(struct_textureReference)]
except AttributeError:
    pass
try:
    hipTexRefGetAddress = _libraries[LIB_HIP].hipTexRefGetAddress
    hipTexRefGetAddress.restype = hipError_t
    hipTexRefGetAddress.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(struct_textureReference)]
except AttributeError:
    pass
try:
    hipTexRefGetAddressMode = _libraries[LIB_HIP].hipTexRefGetAddressMode
    hipTexRefGetAddressMode.restype = hipError_t
    hipTexRefGetAddressMode.argtypes = [ctypes.POINTER(hipTextureAddressMode), ctypes.POINTER(struct_textureReference), ctypes.c_int32]
except AttributeError:
    pass
try:
    hipTexRefGetFilterMode = _libraries[LIB_HIP].hipTexRefGetFilterMode
    hipTexRefGetFilterMode.restype = hipError_t
    hipTexRefGetFilterMode.argtypes = [ctypes.POINTER(hipTextureFilterMode), ctypes.POINTER(struct_textureReference)]
except AttributeError:
    pass
try:
    hipTexRefGetFlags = _libraries[LIB_HIP].hipTexRefGetFlags
    hipTexRefGetFlags.restype = hipError_t
    hipTexRefGetFlags.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(struct_textureReference)]
except AttributeError:
    pass
try:
    hipTexRefGetFormat = _libraries[LIB_HIP].hipTexRefGetFormat
    hipTexRefGetFormat.restype = hipError_t
    hipTexRefGetFormat.argtypes = [ctypes.POINTER(hipArray_Format), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(struct_textureReference)]
except AttributeError:
    pass
try:
    hipTexRefGetMaxAnisotropy = _libraries[LIB_HIP].hipTexRefGetMaxAnisotropy
    hipTexRefGetMaxAnisotropy.restype = hipError_t
    hipTexRefGetMaxAnisotropy.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(struct_textureReference)]
except AttributeError:
    pass
try:
    hipTexRefGetMipmapFilterMode = _libraries[LIB_HIP].hipTexRefGetMipmapFilterMode
    hipTexRefGetMipmapFilterMode.restype = hipError_t
    hipTexRefGetMipmapFilterMode.argtypes = [ctypes.POINTER(hipTextureFilterMode), ctypes.POINTER(struct_textureReference)]
except AttributeError:
    pass
try:
    hipTexRefGetMipmapLevelBias = _libraries[LIB_HIP].hipTexRefGetMipmapLevelBias
    hipTexRefGetMipmapLevelBias.restype = hipError_t
    hipTexRefGetMipmapLevelBias.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.POINTER(struct_textureReference)]
except AttributeError:
    pass
try:
    hipTexRefGetMipmapLevelClamp = _libraries[LIB_HIP].hipTexRefGetMipmapLevelClamp
    hipTexRefGetMipmapLevelClamp.restype = hipError_t
    hipTexRefGetMipmapLevelClamp.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(struct_textureReference)]
except AttributeError:
    pass
try:
    hipTexRefGetMipMappedArray = _libraries['FIXME_STUB'].hipTexRefGetMipMappedArray
    hipTexRefGetMipMappedArray.restype = hipError_t
    hipTexRefGetMipMappedArray.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipMipmappedArray)), ctypes.POINTER(struct_textureReference)]
except AttributeError:
    pass
try:
    hipTexRefSetAddress = _libraries[LIB_HIP].hipTexRefSetAddress
    hipTexRefSetAddress.restype = hipError_t
    hipTexRefSetAddress.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(struct_textureReference), hipDeviceptr_t, size_t]
except AttributeError:
    pass
try:
    hipTexRefSetAddress2D = _libraries[LIB_HIP].hipTexRefSetAddress2D
    hipTexRefSetAddress2D.restype = hipError_t
    hipTexRefSetAddress2D.argtypes = [ctypes.POINTER(struct_textureReference), ctypes.POINTER(struct_HIP_ARRAY_DESCRIPTOR), hipDeviceptr_t, size_t]
except AttributeError:
    pass
try:
    hipTexRefSetMaxAnisotropy = _libraries[LIB_HIP].hipTexRefSetMaxAnisotropy
    hipTexRefSetMaxAnisotropy.restype = hipError_t
    hipTexRefSetMaxAnisotropy.argtypes = [ctypes.POINTER(struct_textureReference), ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipTexRefSetBorderColor = _libraries[LIB_HIP].hipTexRefSetBorderColor
    hipTexRefSetBorderColor.restype = hipError_t
    hipTexRefSetBorderColor.argtypes = [ctypes.POINTER(struct_textureReference), ctypes.POINTER(ctypes.c_float)]
except AttributeError:
    pass
try:
    hipTexRefSetMipmapFilterMode = _libraries[LIB_HIP].hipTexRefSetMipmapFilterMode
    hipTexRefSetMipmapFilterMode.restype = hipError_t
    hipTexRefSetMipmapFilterMode.argtypes = [ctypes.POINTER(struct_textureReference), hipTextureFilterMode]
except AttributeError:
    pass
try:
    hipTexRefSetMipmapLevelBias = _libraries[LIB_HIP].hipTexRefSetMipmapLevelBias
    hipTexRefSetMipmapLevelBias.restype = hipError_t
    hipTexRefSetMipmapLevelBias.argtypes = [ctypes.POINTER(struct_textureReference), ctypes.c_float]
except AttributeError:
    pass
try:
    hipTexRefSetMipmapLevelClamp = _libraries[LIB_HIP].hipTexRefSetMipmapLevelClamp
    hipTexRefSetMipmapLevelClamp.restype = hipError_t
    hipTexRefSetMipmapLevelClamp.argtypes = [ctypes.POINTER(struct_textureReference), ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    hipTexRefSetMipmappedArray = _libraries[LIB_HIP].hipTexRefSetMipmappedArray
    hipTexRefSetMipmappedArray.restype = hipError_t
    hipTexRefSetMipmappedArray.argtypes = [ctypes.POINTER(struct_textureReference), ctypes.POINTER(struct_hipMipmappedArray), ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipApiName = _libraries[LIB_HIP].hipApiName
    hipApiName.restype = ctypes.POINTER(ctypes.c_char)
    hipApiName.argtypes = [uint32_t]
except AttributeError:
    pass
try:
    hipKernelNameRef = _libraries[LIB_HIP].hipKernelNameRef
    hipKernelNameRef.restype = ctypes.POINTER(ctypes.c_char)
    hipKernelNameRef.argtypes = [hipFunction_t]
except AttributeError:
    pass
try:
    hipKernelNameRefByPtr = _libraries[LIB_HIP].hipKernelNameRefByPtr
    hipKernelNameRefByPtr.restype = ctypes.POINTER(ctypes.c_char)
    hipKernelNameRefByPtr.argtypes = [ctypes.POINTER(None), hipStream_t]
except AttributeError:
    pass
try:
    hipGetStreamDeviceId = _libraries[LIB_HIP].hipGetStreamDeviceId
    hipGetStreamDeviceId.restype = ctypes.c_int32
    hipGetStreamDeviceId.argtypes = [hipStream_t]
except AttributeError:
    pass
try:
    hipStreamBeginCapture = _libraries[LIB_HIP].hipStreamBeginCapture
    hipStreamBeginCapture.restype = hipError_t
    hipStreamBeginCapture.argtypes = [hipStream_t, hipStreamCaptureMode]
except AttributeError:
    pass
try:
    hipStreamEndCapture = _libraries[LIB_HIP].hipStreamEndCapture
    hipStreamEndCapture.restype = hipError_t
    hipStreamEndCapture.argtypes = [hipStream_t, ctypes.POINTER(ctypes.POINTER(struct_ihipGraph))]
except AttributeError:
    pass
try:
    hipStreamGetCaptureInfo = _libraries[LIB_HIP].hipStreamGetCaptureInfo
    hipStreamGetCaptureInfo.restype = hipError_t
    hipStreamGetCaptureInfo.argtypes = [hipStream_t, ctypes.POINTER(hipStreamCaptureStatus), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    hipStreamGetCaptureInfo_v2 = _libraries[LIB_HIP].hipStreamGetCaptureInfo_v2
    hipStreamGetCaptureInfo_v2.restype = hipError_t
    hipStreamGetCaptureInfo_v2.argtypes = [hipStream_t, ctypes.POINTER(hipStreamCaptureStatus), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.POINTER(struct_ihipGraph)), ctypes.POINTER(ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode))), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    hipStreamIsCapturing = _libraries[LIB_HIP].hipStreamIsCapturing
    hipStreamIsCapturing.restype = hipError_t
    hipStreamIsCapturing.argtypes = [hipStream_t, ctypes.POINTER(hipStreamCaptureStatus)]
except AttributeError:
    pass
try:
    hipStreamUpdateCaptureDependencies = _libraries[LIB_HIP].hipStreamUpdateCaptureDependencies
    hipStreamUpdateCaptureDependencies.restype = hipError_t
    hipStreamUpdateCaptureDependencies.argtypes = [hipStream_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), size_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipThreadExchangeStreamCaptureMode = _libraries[LIB_HIP].hipThreadExchangeStreamCaptureMode
    hipThreadExchangeStreamCaptureMode.restype = hipError_t
    hipThreadExchangeStreamCaptureMode.argtypes = [ctypes.POINTER(hipStreamCaptureMode)]
except AttributeError:
    pass
try:
    hipGraphCreate = _libraries[LIB_HIP].hipGraphCreate
    hipGraphCreate.restype = hipError_t
    hipGraphCreate.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipGraph)), ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipGraphDestroy = _libraries[LIB_HIP].hipGraphDestroy
    hipGraphDestroy.restype = hipError_t
    hipGraphDestroy.argtypes = [hipGraph_t]
except AttributeError:
    pass
try:
    hipGraphAddDependencies = _libraries[LIB_HIP].hipGraphAddDependencies
    hipGraphAddDependencies.restype = hipError_t
    hipGraphAddDependencies.argtypes = [hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), size_t]
except AttributeError:
    pass
try:
    hipGraphRemoveDependencies = _libraries[LIB_HIP].hipGraphRemoveDependencies
    hipGraphRemoveDependencies.restype = hipError_t
    hipGraphRemoveDependencies.argtypes = [hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), size_t]
except AttributeError:
    pass
try:
    hipGraphGetEdges = _libraries[LIB_HIP].hipGraphGetEdges
    hipGraphGetEdges.restype = hipError_t
    hipGraphGetEdges.argtypes = [hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    hipGraphGetNodes = _libraries[LIB_HIP].hipGraphGetNodes
    hipGraphGetNodes.restype = hipError_t
    hipGraphGetNodes.argtypes = [hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    hipGraphGetRootNodes = _libraries[LIB_HIP].hipGraphGetRootNodes
    hipGraphGetRootNodes.restype = hipError_t
    hipGraphGetRootNodes.argtypes = [hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    hipGraphNodeGetDependencies = _libraries[LIB_HIP].hipGraphNodeGetDependencies
    hipGraphNodeGetDependencies.restype = hipError_t
    hipGraphNodeGetDependencies.argtypes = [hipGraphNode_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    hipGraphNodeGetDependentNodes = _libraries[LIB_HIP].hipGraphNodeGetDependentNodes
    hipGraphNodeGetDependentNodes.restype = hipError_t
    hipGraphNodeGetDependentNodes.argtypes = [hipGraphNode_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    hipGraphNodeGetType = _libraries[LIB_HIP].hipGraphNodeGetType
    hipGraphNodeGetType.restype = hipError_t
    hipGraphNodeGetType.argtypes = [hipGraphNode_t, ctypes.POINTER(hipGraphNodeType)]
except AttributeError:
    pass
try:
    hipGraphDestroyNode = _libraries[LIB_HIP].hipGraphDestroyNode
    hipGraphDestroyNode.restype = hipError_t
    hipGraphDestroyNode.argtypes = [hipGraphNode_t]
except AttributeError:
    pass
try:
    hipGraphClone = _libraries[LIB_HIP].hipGraphClone
    hipGraphClone.restype = hipError_t
    hipGraphClone.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipGraph)), hipGraph_t]
except AttributeError:
    pass
try:
    hipGraphNodeFindInClone = _libraries[LIB_HIP].hipGraphNodeFindInClone
    hipGraphNodeFindInClone.restype = hipError_t
    hipGraphNodeFindInClone.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), hipGraphNode_t, hipGraph_t]
except AttributeError:
    pass
try:
    hipGraphInstantiate = _libraries[LIB_HIP].hipGraphInstantiate
    hipGraphInstantiate.restype = hipError_t
    hipGraphInstantiate.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipGraphExec)), hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), ctypes.POINTER(ctypes.c_char), size_t]
except AttributeError:
    pass
try:
    hipGraphInstantiateWithFlags = _libraries[LIB_HIP].hipGraphInstantiateWithFlags
    hipGraphInstantiateWithFlags.restype = hipError_t
    hipGraphInstantiateWithFlags.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipGraphExec)), hipGraph_t, ctypes.c_uint64]
except AttributeError:
    pass
try:
    hipGraphLaunch = _libraries[LIB_HIP].hipGraphLaunch
    hipGraphLaunch.restype = hipError_t
    hipGraphLaunch.argtypes = [hipGraphExec_t, hipStream_t]
except AttributeError:
    pass
try:
    hipGraphUpload = _libraries[LIB_HIP].hipGraphUpload
    hipGraphUpload.restype = hipError_t
    hipGraphUpload.argtypes = [hipGraphExec_t, hipStream_t]
except AttributeError:
    pass
try:
    hipGraphExecDestroy = _libraries[LIB_HIP].hipGraphExecDestroy
    hipGraphExecDestroy.restype = hipError_t
    hipGraphExecDestroy.argtypes = [hipGraphExec_t]
except AttributeError:
    pass
try:
    hipGraphExecUpdate = _libraries[LIB_HIP].hipGraphExecUpdate
    hipGraphExecUpdate.restype = hipError_t
    hipGraphExecUpdate.argtypes = [hipGraphExec_t, hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), ctypes.POINTER(hipGraphExecUpdateResult)]
except AttributeError:
    pass
try:
    hipGraphAddKernelNode = _libraries[LIB_HIP].hipGraphAddKernelNode
    hipGraphAddKernelNode.restype = hipError_t
    hipGraphAddKernelNode.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), size_t, ctypes.POINTER(struct_hipKernelNodeParams)]
except AttributeError:
    pass
try:
    hipGraphKernelNodeGetParams = _libraries[LIB_HIP].hipGraphKernelNodeGetParams
    hipGraphKernelNodeGetParams.restype = hipError_t
    hipGraphKernelNodeGetParams.argtypes = [hipGraphNode_t, ctypes.POINTER(struct_hipKernelNodeParams)]
except AttributeError:
    pass
try:
    hipGraphKernelNodeSetParams = _libraries[LIB_HIP].hipGraphKernelNodeSetParams
    hipGraphKernelNodeSetParams.restype = hipError_t
    hipGraphKernelNodeSetParams.argtypes = [hipGraphNode_t, ctypes.POINTER(struct_hipKernelNodeParams)]
except AttributeError:
    pass
try:
    hipGraphExecKernelNodeSetParams = _libraries[LIB_HIP].hipGraphExecKernelNodeSetParams
    hipGraphExecKernelNodeSetParams.restype = hipError_t
    hipGraphExecKernelNodeSetParams.argtypes = [hipGraphExec_t, hipGraphNode_t, ctypes.POINTER(struct_hipKernelNodeParams)]
except AttributeError:
    pass
try:
    hipGraphAddMemcpyNode = _libraries[LIB_HIP].hipGraphAddMemcpyNode
    hipGraphAddMemcpyNode.restype = hipError_t
    hipGraphAddMemcpyNode.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), size_t, ctypes.POINTER(struct_hipMemcpy3DParms)]
except AttributeError:
    pass
try:
    hipGraphMemcpyNodeGetParams = _libraries[LIB_HIP].hipGraphMemcpyNodeGetParams
    hipGraphMemcpyNodeGetParams.restype = hipError_t
    hipGraphMemcpyNodeGetParams.argtypes = [hipGraphNode_t, ctypes.POINTER(struct_hipMemcpy3DParms)]
except AttributeError:
    pass
try:
    hipGraphMemcpyNodeSetParams = _libraries[LIB_HIP].hipGraphMemcpyNodeSetParams
    hipGraphMemcpyNodeSetParams.restype = hipError_t
    hipGraphMemcpyNodeSetParams.argtypes = [hipGraphNode_t, ctypes.POINTER(struct_hipMemcpy3DParms)]
except AttributeError:
    pass
try:
    hipGraphKernelNodeSetAttribute = _libraries[LIB_HIP].hipGraphKernelNodeSetAttribute
    hipGraphKernelNodeSetAttribute.restype = hipError_t
    hipGraphKernelNodeSetAttribute.argtypes = [hipGraphNode_t, hipKernelNodeAttrID, ctypes.POINTER(union_hipKernelNodeAttrValue)]
except AttributeError:
    pass
try:
    hipGraphKernelNodeGetAttribute = _libraries[LIB_HIP].hipGraphKernelNodeGetAttribute
    hipGraphKernelNodeGetAttribute.restype = hipError_t
    hipGraphKernelNodeGetAttribute.argtypes = [hipGraphNode_t, hipKernelNodeAttrID, ctypes.POINTER(union_hipKernelNodeAttrValue)]
except AttributeError:
    pass
try:
    hipGraphExecMemcpyNodeSetParams = _libraries[LIB_HIP].hipGraphExecMemcpyNodeSetParams
    hipGraphExecMemcpyNodeSetParams.restype = hipError_t
    hipGraphExecMemcpyNodeSetParams.argtypes = [hipGraphExec_t, hipGraphNode_t, ctypes.POINTER(struct_hipMemcpy3DParms)]
except AttributeError:
    pass
try:
    hipGraphAddMemcpyNode1D = _libraries[LIB_HIP].hipGraphAddMemcpyNode1D
    hipGraphAddMemcpyNode1D.restype = hipError_t
    hipGraphAddMemcpyNode1D.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), size_t, ctypes.POINTER(None), ctypes.POINTER(None), size_t, hipMemcpyKind]
except AttributeError:
    pass
try:
    hipGraphMemcpyNodeSetParams1D = _libraries[LIB_HIP].hipGraphMemcpyNodeSetParams1D
    hipGraphMemcpyNodeSetParams1D.restype = hipError_t
    hipGraphMemcpyNodeSetParams1D.argtypes = [hipGraphNode_t, ctypes.POINTER(None), ctypes.POINTER(None), size_t, hipMemcpyKind]
except AttributeError:
    pass
try:
    hipGraphExecMemcpyNodeSetParams1D = _libraries[LIB_HIP].hipGraphExecMemcpyNodeSetParams1D
    hipGraphExecMemcpyNodeSetParams1D.restype = hipError_t
    hipGraphExecMemcpyNodeSetParams1D.argtypes = [hipGraphExec_t, hipGraphNode_t, ctypes.POINTER(None), ctypes.POINTER(None), size_t, hipMemcpyKind]
except AttributeError:
    pass
try:
    hipGraphAddMemcpyNodeFromSymbol = _libraries[LIB_HIP].hipGraphAddMemcpyNodeFromSymbol
    hipGraphAddMemcpyNodeFromSymbol.restype = hipError_t
    hipGraphAddMemcpyNodeFromSymbol.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), size_t, ctypes.POINTER(None), ctypes.POINTER(None), size_t, size_t, hipMemcpyKind]
except AttributeError:
    pass
try:
    hipGraphMemcpyNodeSetParamsFromSymbol = _libraries[LIB_HIP].hipGraphMemcpyNodeSetParamsFromSymbol
    hipGraphMemcpyNodeSetParamsFromSymbol.restype = hipError_t
    hipGraphMemcpyNodeSetParamsFromSymbol.argtypes = [hipGraphNode_t, ctypes.POINTER(None), ctypes.POINTER(None), size_t, size_t, hipMemcpyKind]
except AttributeError:
    pass
try:
    hipGraphExecMemcpyNodeSetParamsFromSymbol = _libraries[LIB_HIP].hipGraphExecMemcpyNodeSetParamsFromSymbol
    hipGraphExecMemcpyNodeSetParamsFromSymbol.restype = hipError_t
    hipGraphExecMemcpyNodeSetParamsFromSymbol.argtypes = [hipGraphExec_t, hipGraphNode_t, ctypes.POINTER(None), ctypes.POINTER(None), size_t, size_t, hipMemcpyKind]
except AttributeError:
    pass
try:
    hipGraphAddMemcpyNodeToSymbol = _libraries[LIB_HIP].hipGraphAddMemcpyNodeToSymbol
    hipGraphAddMemcpyNodeToSymbol.restype = hipError_t
    hipGraphAddMemcpyNodeToSymbol.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), size_t, ctypes.POINTER(None), ctypes.POINTER(None), size_t, size_t, hipMemcpyKind]
except AttributeError:
    pass
try:
    hipGraphMemcpyNodeSetParamsToSymbol = _libraries[LIB_HIP].hipGraphMemcpyNodeSetParamsToSymbol
    hipGraphMemcpyNodeSetParamsToSymbol.restype = hipError_t
    hipGraphMemcpyNodeSetParamsToSymbol.argtypes = [hipGraphNode_t, ctypes.POINTER(None), ctypes.POINTER(None), size_t, size_t, hipMemcpyKind]
except AttributeError:
    pass
try:
    hipGraphExecMemcpyNodeSetParamsToSymbol = _libraries[LIB_HIP].hipGraphExecMemcpyNodeSetParamsToSymbol
    hipGraphExecMemcpyNodeSetParamsToSymbol.restype = hipError_t
    hipGraphExecMemcpyNodeSetParamsToSymbol.argtypes = [hipGraphExec_t, hipGraphNode_t, ctypes.POINTER(None), ctypes.POINTER(None), size_t, size_t, hipMemcpyKind]
except AttributeError:
    pass
try:
    hipGraphAddMemsetNode = _libraries[LIB_HIP].hipGraphAddMemsetNode
    hipGraphAddMemsetNode.restype = hipError_t
    hipGraphAddMemsetNode.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), size_t, ctypes.POINTER(struct_hipMemsetParams)]
except AttributeError:
    pass
try:
    hipGraphMemsetNodeGetParams = _libraries[LIB_HIP].hipGraphMemsetNodeGetParams
    hipGraphMemsetNodeGetParams.restype = hipError_t
    hipGraphMemsetNodeGetParams.argtypes = [hipGraphNode_t, ctypes.POINTER(struct_hipMemsetParams)]
except AttributeError:
    pass
try:
    hipGraphMemsetNodeSetParams = _libraries[LIB_HIP].hipGraphMemsetNodeSetParams
    hipGraphMemsetNodeSetParams.restype = hipError_t
    hipGraphMemsetNodeSetParams.argtypes = [hipGraphNode_t, ctypes.POINTER(struct_hipMemsetParams)]
except AttributeError:
    pass
try:
    hipGraphExecMemsetNodeSetParams = _libraries[LIB_HIP].hipGraphExecMemsetNodeSetParams
    hipGraphExecMemsetNodeSetParams.restype = hipError_t
    hipGraphExecMemsetNodeSetParams.argtypes = [hipGraphExec_t, hipGraphNode_t, ctypes.POINTER(struct_hipMemsetParams)]
except AttributeError:
    pass
try:
    hipGraphAddHostNode = _libraries[LIB_HIP].hipGraphAddHostNode
    hipGraphAddHostNode.restype = hipError_t
    hipGraphAddHostNode.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), size_t, ctypes.POINTER(struct_hipHostNodeParams)]
except AttributeError:
    pass
try:
    hipGraphHostNodeGetParams = _libraries[LIB_HIP].hipGraphHostNodeGetParams
    hipGraphHostNodeGetParams.restype = hipError_t
    hipGraphHostNodeGetParams.argtypes = [hipGraphNode_t, ctypes.POINTER(struct_hipHostNodeParams)]
except AttributeError:
    pass
try:
    hipGraphHostNodeSetParams = _libraries[LIB_HIP].hipGraphHostNodeSetParams
    hipGraphHostNodeSetParams.restype = hipError_t
    hipGraphHostNodeSetParams.argtypes = [hipGraphNode_t, ctypes.POINTER(struct_hipHostNodeParams)]
except AttributeError:
    pass
try:
    hipGraphExecHostNodeSetParams = _libraries[LIB_HIP].hipGraphExecHostNodeSetParams
    hipGraphExecHostNodeSetParams.restype = hipError_t
    hipGraphExecHostNodeSetParams.argtypes = [hipGraphExec_t, hipGraphNode_t, ctypes.POINTER(struct_hipHostNodeParams)]
except AttributeError:
    pass
try:
    hipGraphAddChildGraphNode = _libraries[LIB_HIP].hipGraphAddChildGraphNode
    hipGraphAddChildGraphNode.restype = hipError_t
    hipGraphAddChildGraphNode.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), size_t, hipGraph_t]
except AttributeError:
    pass
try:
    hipGraphChildGraphNodeGetGraph = _libraries[LIB_HIP].hipGraphChildGraphNodeGetGraph
    hipGraphChildGraphNodeGetGraph.restype = hipError_t
    hipGraphChildGraphNodeGetGraph.argtypes = [hipGraphNode_t, ctypes.POINTER(ctypes.POINTER(struct_ihipGraph))]
except AttributeError:
    pass
try:
    hipGraphExecChildGraphNodeSetParams = _libraries[LIB_HIP].hipGraphExecChildGraphNodeSetParams
    hipGraphExecChildGraphNodeSetParams.restype = hipError_t
    hipGraphExecChildGraphNodeSetParams.argtypes = [hipGraphExec_t, hipGraphNode_t, hipGraph_t]
except AttributeError:
    pass
try:
    hipGraphAddEmptyNode = _libraries[LIB_HIP].hipGraphAddEmptyNode
    hipGraphAddEmptyNode.restype = hipError_t
    hipGraphAddEmptyNode.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), size_t]
except AttributeError:
    pass
try:
    hipGraphAddEventRecordNode = _libraries[LIB_HIP].hipGraphAddEventRecordNode
    hipGraphAddEventRecordNode.restype = hipError_t
    hipGraphAddEventRecordNode.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), size_t, hipEvent_t]
except AttributeError:
    pass
try:
    hipGraphEventRecordNodeGetEvent = _libraries[LIB_HIP].hipGraphEventRecordNodeGetEvent
    hipGraphEventRecordNodeGetEvent.restype = hipError_t
    hipGraphEventRecordNodeGetEvent.argtypes = [hipGraphNode_t, ctypes.POINTER(ctypes.POINTER(struct_ihipEvent_t))]
except AttributeError:
    pass
try:
    hipGraphEventRecordNodeSetEvent = _libraries[LIB_HIP].hipGraphEventRecordNodeSetEvent
    hipGraphEventRecordNodeSetEvent.restype = hipError_t
    hipGraphEventRecordNodeSetEvent.argtypes = [hipGraphNode_t, hipEvent_t]
except AttributeError:
    pass
try:
    hipGraphExecEventRecordNodeSetEvent = _libraries[LIB_HIP].hipGraphExecEventRecordNodeSetEvent
    hipGraphExecEventRecordNodeSetEvent.restype = hipError_t
    hipGraphExecEventRecordNodeSetEvent.argtypes = [hipGraphExec_t, hipGraphNode_t, hipEvent_t]
except AttributeError:
    pass
try:
    hipGraphAddEventWaitNode = _libraries[LIB_HIP].hipGraphAddEventWaitNode
    hipGraphAddEventWaitNode.restype = hipError_t
    hipGraphAddEventWaitNode.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), size_t, hipEvent_t]
except AttributeError:
    pass
try:
    hipGraphEventWaitNodeGetEvent = _libraries[LIB_HIP].hipGraphEventWaitNodeGetEvent
    hipGraphEventWaitNodeGetEvent.restype = hipError_t
    hipGraphEventWaitNodeGetEvent.argtypes = [hipGraphNode_t, ctypes.POINTER(ctypes.POINTER(struct_ihipEvent_t))]
except AttributeError:
    pass
try:
    hipGraphEventWaitNodeSetEvent = _libraries[LIB_HIP].hipGraphEventWaitNodeSetEvent
    hipGraphEventWaitNodeSetEvent.restype = hipError_t
    hipGraphEventWaitNodeSetEvent.argtypes = [hipGraphNode_t, hipEvent_t]
except AttributeError:
    pass
try:
    hipGraphExecEventWaitNodeSetEvent = _libraries[LIB_HIP].hipGraphExecEventWaitNodeSetEvent
    hipGraphExecEventWaitNodeSetEvent.restype = hipError_t
    hipGraphExecEventWaitNodeSetEvent.argtypes = [hipGraphExec_t, hipGraphNode_t, hipEvent_t]
except AttributeError:
    pass
try:
    hipGraphAddMemAllocNode = _libraries[LIB_HIP].hipGraphAddMemAllocNode
    hipGraphAddMemAllocNode.restype = hipError_t
    hipGraphAddMemAllocNode.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), size_t, ctypes.POINTER(struct_hipMemAllocNodeParams)]
except AttributeError:
    pass
try:
    hipGraphMemAllocNodeGetParams = _libraries[LIB_HIP].hipGraphMemAllocNodeGetParams
    hipGraphMemAllocNodeGetParams.restype = hipError_t
    hipGraphMemAllocNodeGetParams.argtypes = [hipGraphNode_t, ctypes.POINTER(struct_hipMemAllocNodeParams)]
except AttributeError:
    pass
try:
    hipGraphAddMemFreeNode = _libraries[LIB_HIP].hipGraphAddMemFreeNode
    hipGraphAddMemFreeNode.restype = hipError_t
    hipGraphAddMemFreeNode.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), size_t, ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipGraphMemFreeNodeGetParams = _libraries[LIB_HIP].hipGraphMemFreeNodeGetParams
    hipGraphMemFreeNodeGetParams.restype = hipError_t
    hipGraphMemFreeNodeGetParams.argtypes = [hipGraphNode_t, ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipDeviceGetGraphMemAttribute = _libraries[LIB_HIP].hipDeviceGetGraphMemAttribute
    hipDeviceGetGraphMemAttribute.restype = hipError_t
    hipDeviceGetGraphMemAttribute.argtypes = [ctypes.c_int32, hipGraphMemAttributeType, ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipDeviceSetGraphMemAttribute = _libraries[LIB_HIP].hipDeviceSetGraphMemAttribute
    hipDeviceSetGraphMemAttribute.restype = hipError_t
    hipDeviceSetGraphMemAttribute.argtypes = [ctypes.c_int32, hipGraphMemAttributeType, ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipDeviceGraphMemTrim = _libraries[LIB_HIP].hipDeviceGraphMemTrim
    hipDeviceGraphMemTrim.restype = hipError_t
    hipDeviceGraphMemTrim.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    hipUserObjectCreate = _libraries[LIB_HIP].hipUserObjectCreate
    hipUserObjectCreate.restype = hipError_t
    hipUserObjectCreate.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipUserObject)), ctypes.POINTER(None), hipHostFn_t, ctypes.c_uint32, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipUserObjectRelease = _libraries[LIB_HIP].hipUserObjectRelease
    hipUserObjectRelease.restype = hipError_t
    hipUserObjectRelease.argtypes = [hipUserObject_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipUserObjectRetain = _libraries[LIB_HIP].hipUserObjectRetain
    hipUserObjectRetain.restype = hipError_t
    hipUserObjectRetain.argtypes = [hipUserObject_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipGraphRetainUserObject = _libraries[LIB_HIP].hipGraphRetainUserObject
    hipGraphRetainUserObject.restype = hipError_t
    hipGraphRetainUserObject.argtypes = [hipGraph_t, hipUserObject_t, ctypes.c_uint32, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipGraphReleaseUserObject = _libraries[LIB_HIP].hipGraphReleaseUserObject
    hipGraphReleaseUserObject.restype = hipError_t
    hipGraphReleaseUserObject.argtypes = [hipGraph_t, hipUserObject_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipGraphDebugDotPrint = _libraries[LIB_HIP].hipGraphDebugDotPrint
    hipGraphDebugDotPrint.restype = hipError_t
    hipGraphDebugDotPrint.argtypes = [hipGraph_t, ctypes.POINTER(ctypes.c_char), ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipGraphKernelNodeCopyAttributes = _libraries[LIB_HIP].hipGraphKernelNodeCopyAttributes
    hipGraphKernelNodeCopyAttributes.restype = hipError_t
    hipGraphKernelNodeCopyAttributes.argtypes = [hipGraphNode_t, hipGraphNode_t]
except AttributeError:
    pass
try:
    hipGraphNodeSetEnabled = _libraries[LIB_HIP].hipGraphNodeSetEnabled
    hipGraphNodeSetEnabled.restype = hipError_t
    hipGraphNodeSetEnabled.argtypes = [hipGraphExec_t, hipGraphNode_t, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipGraphNodeGetEnabled = _libraries[LIB_HIP].hipGraphNodeGetEnabled
    hipGraphNodeGetEnabled.restype = hipError_t
    hipGraphNodeGetEnabled.argtypes = [hipGraphExec_t, hipGraphNode_t, ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    hipGraphAddExternalSemaphoresWaitNode = _libraries['FIXME_STUB'].hipGraphAddExternalSemaphoresWaitNode
    hipGraphAddExternalSemaphoresWaitNode.restype = hipError_t
    hipGraphAddExternalSemaphoresWaitNode.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), size_t, ctypes.POINTER(struct_hipExternalSemaphoreWaitNodeParams)]
except AttributeError:
    pass
try:
    hipGraphAddExternalSemaphoresSignalNode = _libraries['FIXME_STUB'].hipGraphAddExternalSemaphoresSignalNode
    hipGraphAddExternalSemaphoresSignalNode.restype = hipError_t
    hipGraphAddExternalSemaphoresSignalNode.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), hipGraph_t, ctypes.POINTER(ctypes.POINTER(struct_hipGraphNode)), size_t, ctypes.POINTER(struct_hipExternalSemaphoreSignalNodeParams)]
except AttributeError:
    pass
try:
    hipGraphExternalSemaphoresSignalNodeSetParams = _libraries['FIXME_STUB'].hipGraphExternalSemaphoresSignalNodeSetParams
    hipGraphExternalSemaphoresSignalNodeSetParams.restype = hipError_t
    hipGraphExternalSemaphoresSignalNodeSetParams.argtypes = [hipGraphNode_t, ctypes.POINTER(struct_hipExternalSemaphoreSignalNodeParams)]
except AttributeError:
    pass
try:
    hipGraphExternalSemaphoresWaitNodeSetParams = _libraries['FIXME_STUB'].hipGraphExternalSemaphoresWaitNodeSetParams
    hipGraphExternalSemaphoresWaitNodeSetParams.restype = hipError_t
    hipGraphExternalSemaphoresWaitNodeSetParams.argtypes = [hipGraphNode_t, ctypes.POINTER(struct_hipExternalSemaphoreWaitNodeParams)]
except AttributeError:
    pass
try:
    hipGraphExternalSemaphoresSignalNodeGetParams = _libraries['FIXME_STUB'].hipGraphExternalSemaphoresSignalNodeGetParams
    hipGraphExternalSemaphoresSignalNodeGetParams.restype = hipError_t
    hipGraphExternalSemaphoresSignalNodeGetParams.argtypes = [hipGraphNode_t, ctypes.POINTER(struct_hipExternalSemaphoreSignalNodeParams)]
except AttributeError:
    pass
try:
    hipGraphExternalSemaphoresWaitNodeGetParams = _libraries['FIXME_STUB'].hipGraphExternalSemaphoresWaitNodeGetParams
    hipGraphExternalSemaphoresWaitNodeGetParams.restype = hipError_t
    hipGraphExternalSemaphoresWaitNodeGetParams.argtypes = [hipGraphNode_t, ctypes.POINTER(struct_hipExternalSemaphoreWaitNodeParams)]
except AttributeError:
    pass
try:
    hipGraphExecExternalSemaphoresSignalNodeSetParams = _libraries['FIXME_STUB'].hipGraphExecExternalSemaphoresSignalNodeSetParams
    hipGraphExecExternalSemaphoresSignalNodeSetParams.restype = hipError_t
    hipGraphExecExternalSemaphoresSignalNodeSetParams.argtypes = [hipGraphExec_t, hipGraphNode_t, ctypes.POINTER(struct_hipExternalSemaphoreSignalNodeParams)]
except AttributeError:
    pass
try:
    hipGraphExecExternalSemaphoresWaitNodeSetParams = _libraries['FIXME_STUB'].hipGraphExecExternalSemaphoresWaitNodeSetParams
    hipGraphExecExternalSemaphoresWaitNodeSetParams.restype = hipError_t
    hipGraphExecExternalSemaphoresWaitNodeSetParams.argtypes = [hipGraphExec_t, hipGraphNode_t, ctypes.POINTER(struct_hipExternalSemaphoreWaitNodeParams)]
except AttributeError:
    pass
try:
    hipMemAddressFree = _libraries[LIB_HIP].hipMemAddressFree
    hipMemAddressFree.restype = hipError_t
    hipMemAddressFree.argtypes = [ctypes.POINTER(None), size_t]
except AttributeError:
    pass
try:
    hipMemAddressReserve = _libraries[LIB_HIP].hipMemAddressReserve
    hipMemAddressReserve.restype = hipError_t
    hipMemAddressReserve.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), size_t, size_t, ctypes.POINTER(None), ctypes.c_uint64]
except AttributeError:
    pass
try:
    hipMemCreate = _libraries[LIB_HIP].hipMemCreate
    hipMemCreate.restype = hipError_t
    hipMemCreate.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipMemGenericAllocationHandle)), size_t, ctypes.POINTER(struct_hipMemAllocationProp), ctypes.c_uint64]
except AttributeError:
    pass
try:
    hipMemExportToShareableHandle = _libraries[LIB_HIP].hipMemExportToShareableHandle
    hipMemExportToShareableHandle.restype = hipError_t
    hipMemExportToShareableHandle.argtypes = [ctypes.POINTER(None), hipMemGenericAllocationHandle_t, hipMemAllocationHandleType, ctypes.c_uint64]
except AttributeError:
    pass
try:
    hipMemGetAccess = _libraries[LIB_HIP].hipMemGetAccess
    hipMemGetAccess.restype = hipError_t
    hipMemGetAccess.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(struct_hipMemLocation), ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipMemGetAllocationGranularity = _libraries[LIB_HIP].hipMemGetAllocationGranularity
    hipMemGetAllocationGranularity.restype = hipError_t
    hipMemGetAllocationGranularity.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(struct_hipMemAllocationProp), hipMemAllocationGranularity_flags]
except AttributeError:
    pass
try:
    hipMemGetAllocationPropertiesFromHandle = _libraries[LIB_HIP].hipMemGetAllocationPropertiesFromHandle
    hipMemGetAllocationPropertiesFromHandle.restype = hipError_t
    hipMemGetAllocationPropertiesFromHandle.argtypes = [ctypes.POINTER(struct_hipMemAllocationProp), hipMemGenericAllocationHandle_t]
except AttributeError:
    pass
try:
    hipMemImportFromShareableHandle = _libraries[LIB_HIP].hipMemImportFromShareableHandle
    hipMemImportFromShareableHandle.restype = hipError_t
    hipMemImportFromShareableHandle.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipMemGenericAllocationHandle)), ctypes.POINTER(None), hipMemAllocationHandleType]
except AttributeError:
    pass
try:
    hipMemMap = _libraries[LIB_HIP].hipMemMap
    hipMemMap.restype = hipError_t
    hipMemMap.argtypes = [ctypes.POINTER(None), size_t, size_t, hipMemGenericAllocationHandle_t, ctypes.c_uint64]
except AttributeError:
    pass
try:
    hipMemMapArrayAsync = _libraries[LIB_HIP].hipMemMapArrayAsync
    hipMemMapArrayAsync.restype = hipError_t
    hipMemMapArrayAsync.argtypes = [ctypes.POINTER(struct_hipArrayMapInfo), ctypes.c_uint32, hipStream_t]
except AttributeError:
    pass
try:
    hipMemRelease = _libraries[LIB_HIP].hipMemRelease
    hipMemRelease.restype = hipError_t
    hipMemRelease.argtypes = [hipMemGenericAllocationHandle_t]
except AttributeError:
    pass
try:
    hipMemRetainAllocationHandle = _libraries[LIB_HIP].hipMemRetainAllocationHandle
    hipMemRetainAllocationHandle.restype = hipError_t
    hipMemRetainAllocationHandle.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_ihipMemGenericAllocationHandle)), ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    hipMemSetAccess = _libraries[LIB_HIP].hipMemSetAccess
    hipMemSetAccess.restype = hipError_t
    hipMemSetAccess.argtypes = [ctypes.POINTER(None), size_t, ctypes.POINTER(struct_hipMemAccessDesc), size_t]
except AttributeError:
    pass
try:
    hipMemUnmap = _libraries[LIB_HIP].hipMemUnmap
    hipMemUnmap.restype = hipError_t
    hipMemUnmap.argtypes = [ctypes.POINTER(None), size_t]
except AttributeError:
    pass
GLuint = ctypes.c_uint32
GLenum = ctypes.c_uint32
try:
    hipGLGetDevices = _libraries[LIB_HIP].hipGLGetDevices
    hipGLGetDevices.restype = hipError_t
    hipGLGetDevices.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_int32), ctypes.c_uint32, hipGLDeviceList]
except AttributeError:
    pass
try:
    hipGraphicsGLRegisterBuffer = _libraries[LIB_HIP].hipGraphicsGLRegisterBuffer
    hipGraphicsGLRegisterBuffer.restype = hipError_t
    hipGraphicsGLRegisterBuffer.argtypes = [ctypes.POINTER(ctypes.POINTER(struct__hipGraphicsResource)), GLuint, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipGraphicsGLRegisterImage = _libraries[LIB_HIP].hipGraphicsGLRegisterImage
    hipGraphicsGLRegisterImage.restype = hipError_t
    hipGraphicsGLRegisterImage.argtypes = [ctypes.POINTER(ctypes.POINTER(struct__hipGraphicsResource)), GLuint, GLenum, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipGraphicsMapResources = _libraries[LIB_HIP].hipGraphicsMapResources
    hipGraphicsMapResources.restype = hipError_t
    hipGraphicsMapResources.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.POINTER(struct__hipGraphicsResource)), hipStream_t]
except AttributeError:
    pass
try:
    hipGraphicsSubResourceGetMappedArray = _libraries[LIB_HIP].hipGraphicsSubResourceGetMappedArray
    hipGraphicsSubResourceGetMappedArray.restype = hipError_t
    hipGraphicsSubResourceGetMappedArray.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_hipArray)), hipGraphicsResource_t, ctypes.c_uint32, ctypes.c_uint32]
except AttributeError:
    pass
try:
    hipGraphicsResourceGetMappedPointer = _libraries[LIB_HIP].hipGraphicsResourceGetMappedPointer
    hipGraphicsResourceGetMappedPointer.restype = hipError_t
    hipGraphicsResourceGetMappedPointer.argtypes = [ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(ctypes.c_uint64), hipGraphicsResource_t]
except AttributeError:
    pass
try:
    hipGraphicsUnmapResources = _libraries[LIB_HIP].hipGraphicsUnmapResources
    hipGraphicsUnmapResources.restype = hipError_t
    hipGraphicsUnmapResources.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.POINTER(struct__hipGraphicsResource)), hipStream_t]
except AttributeError:
    pass
try:
    hipGraphicsUnregisterResource = _libraries[LIB_HIP].hipGraphicsUnregisterResource
    hipGraphicsUnregisterResource.restype = hipError_t
    hipGraphicsUnregisterResource.argtypes = [hipGraphicsResource_t]
except AttributeError:
    pass
class struct___hip_surface(Structure):
    pass

try:
    hipCreateSurfaceObject = _libraries[LIB_HIP].hipCreateSurfaceObject
    hipCreateSurfaceObject.restype = hipError_t
    hipCreateSurfaceObject.argtypes = [ctypes.POINTER(ctypes.POINTER(struct___hip_surface)), ctypes.POINTER(struct_hipResourceDesc)]
except AttributeError:
    pass
hipSurfaceObject_t = ctypes.POINTER(struct___hip_surface)
try:
    hipDestroySurfaceObject = _libraries[LIB_HIP].hipDestroySurfaceObject
    hipDestroySurfaceObject.restype = hipError_t
    hipDestroySurfaceObject.argtypes = [hipSurfaceObject_t]
except AttributeError:
    pass
__all__ = \
    ['GLenum', 'GLuint', 'HIPRTC_ERROR_BUILTIN_OPERATION_FAILURE',
    'HIPRTC_ERROR_COMPILATION', 'HIPRTC_ERROR_INTERNAL_ERROR',
    'HIPRTC_ERROR_INVALID_INPUT', 'HIPRTC_ERROR_INVALID_OPTION',
    'HIPRTC_ERROR_INVALID_PROGRAM', 'HIPRTC_ERROR_LINKING',
    'HIPRTC_ERROR_NAME_EXPRESSION_NOT_VALID',
    'HIPRTC_ERROR_NO_LOWERED_NAMES_BEFORE_COMPILATION',
    'HIPRTC_ERROR_NO_NAME_EXPRESSIONS_AFTER_COMPILATION',
    'HIPRTC_ERROR_OUT_OF_MEMORY',
    'HIPRTC_ERROR_PROGRAM_CREATION_FAILURE', 'HIPRTC_JIT_CACHE_MODE',
    'HIPRTC_JIT_ERROR_LOG_BUFFER',
    'HIPRTC_JIT_ERROR_LOG_BUFFER_SIZE_BYTES',
    'HIPRTC_JIT_FALLBACK_STRATEGY', 'HIPRTC_JIT_FAST_COMPILE',
    'HIPRTC_JIT_FMA', 'HIPRTC_JIT_FTZ',
    'HIPRTC_JIT_GENERATE_DEBUG_INFO', 'HIPRTC_JIT_GENERATE_LINE_INFO',
    'HIPRTC_JIT_GLOBAL_SYMBOL_ADDRESS',
    'HIPRTC_JIT_GLOBAL_SYMBOL_COUNT',
    'HIPRTC_JIT_GLOBAL_SYMBOL_NAMES', 'HIPRTC_JIT_INFO_LOG_BUFFER',
    'HIPRTC_JIT_INFO_LOG_BUFFER_SIZE_BYTES', 'HIPRTC_JIT_INPUT_CUBIN',
    'HIPRTC_JIT_INPUT_FATBINARY', 'HIPRTC_JIT_INPUT_LIBRARY',
    'HIPRTC_JIT_INPUT_LLVM_ARCHIVES_OF_BUNDLED_BITCODE',
    'HIPRTC_JIT_INPUT_LLVM_BITCODE',
    'HIPRTC_JIT_INPUT_LLVM_BUNDLED_BITCODE', 'HIPRTC_JIT_INPUT_NVVM',
    'HIPRTC_JIT_INPUT_OBJECT', 'HIPRTC_JIT_INPUT_PTX',
    'HIPRTC_JIT_IR_TO_ISA_OPT_COUNT_EXT',
    'HIPRTC_JIT_IR_TO_ISA_OPT_EXT', 'HIPRTC_JIT_LOG_VERBOSE',
    'HIPRTC_JIT_LTO', 'HIPRTC_JIT_MAX_REGISTERS',
    'HIPRTC_JIT_NEW_SM3X_OPT', 'HIPRTC_JIT_NUM_INPUT_TYPES',
    'HIPRTC_JIT_NUM_LEGACY_INPUT_TYPES', 'HIPRTC_JIT_NUM_OPTIONS',
    'HIPRTC_JIT_OPTIMIZATION_LEVEL', 'HIPRTC_JIT_PREC_DIV',
    'HIPRTC_JIT_PREC_SQRT', 'HIPRTC_JIT_TARGET',
    'HIPRTC_JIT_TARGET_FROM_HIPCONTEXT',
    'HIPRTC_JIT_THREADS_PER_BLOCK', 'HIPRTC_JIT_WALL_TIME',
    'HIPRTC_SUCCESS', 'HIP_AD_FORMAT_FLOAT', 'HIP_AD_FORMAT_HALF',
    'HIP_AD_FORMAT_SIGNED_INT16', 'HIP_AD_FORMAT_SIGNED_INT32',
    'HIP_AD_FORMAT_SIGNED_INT8', 'HIP_AD_FORMAT_UNSIGNED_INT16',
    'HIP_AD_FORMAT_UNSIGNED_INT32', 'HIP_AD_FORMAT_UNSIGNED_INT8',
    'HIP_ARRAY3D_DESCRIPTOR', 'HIP_ARRAY_DESCRIPTOR',
    'HIP_ERROR_INVALID_VALUE', 'HIP_ERROR_LAUNCH_OUT_OF_RESOURCES',
    'HIP_ERROR_NOT_INITIALIZED', 'HIP_FUNC_ATTRIBUTE_BINARY_VERSION',
    'HIP_FUNC_ATTRIBUTE_CACHE_MODE_CA',
    'HIP_FUNC_ATTRIBUTE_CONST_SIZE_BYTES',
    'HIP_FUNC_ATTRIBUTE_LOCAL_SIZE_BYTES', 'HIP_FUNC_ATTRIBUTE_MAX',
    'HIP_FUNC_ATTRIBUTE_MAX_DYNAMIC_SHARED_SIZE_BYTES',
    'HIP_FUNC_ATTRIBUTE_MAX_THREADS_PER_BLOCK',
    'HIP_FUNC_ATTRIBUTE_NUM_REGS',
    'HIP_FUNC_ATTRIBUTE_PREFERRED_SHARED_MEMORY_CARVEOUT',
    'HIP_FUNC_ATTRIBUTE_PTX_VERSION',
    'HIP_FUNC_ATTRIBUTE_SHARED_SIZE_BYTES', 'HIP_MEMCPY3D',
    'HIP_POINTER_ATTRIBUTE_ACCESS_FLAGS',
    'HIP_POINTER_ATTRIBUTE_ALLOWED_HANDLE_TYPES',
    'HIP_POINTER_ATTRIBUTE_BUFFER_ID',
    'HIP_POINTER_ATTRIBUTE_CONTEXT',
    'HIP_POINTER_ATTRIBUTE_DEVICE_ORDINAL',
    'HIP_POINTER_ATTRIBUTE_DEVICE_POINTER',
    'HIP_POINTER_ATTRIBUTE_HOST_POINTER',
    'HIP_POINTER_ATTRIBUTE_IS_GPU_DIRECT_RDMA_CAPABLE',
    'HIP_POINTER_ATTRIBUTE_IS_LEGACY_HIP_IPC_CAPABLE',
    'HIP_POINTER_ATTRIBUTE_IS_MANAGED',
    'HIP_POINTER_ATTRIBUTE_MAPPED',
    'HIP_POINTER_ATTRIBUTE_MEMORY_TYPE',
    'HIP_POINTER_ATTRIBUTE_MEMPOOL_HANDLE',
    'HIP_POINTER_ATTRIBUTE_P2P_TOKENS',
    'HIP_POINTER_ATTRIBUTE_RANGE_SIZE',
    'HIP_POINTER_ATTRIBUTE_RANGE_START_ADDR',
    'HIP_POINTER_ATTRIBUTE_SYNC_MEMOPS', 'HIP_RESOURCE_DESC',
    'HIP_RESOURCE_TYPE_ARRAY', 'HIP_RESOURCE_TYPE_LINEAR',
    'HIP_RESOURCE_TYPE_MIPMAPPED_ARRAY', 'HIP_RESOURCE_TYPE_PITCH2D',
    'HIP_RESOURCE_VIEW_DESC', 'HIP_RES_VIEW_FORMAT_FLOAT_1X16',
    'HIP_RES_VIEW_FORMAT_FLOAT_1X32',
    'HIP_RES_VIEW_FORMAT_FLOAT_2X16',
    'HIP_RES_VIEW_FORMAT_FLOAT_2X32',
    'HIP_RES_VIEW_FORMAT_FLOAT_4X16',
    'HIP_RES_VIEW_FORMAT_FLOAT_4X32', 'HIP_RES_VIEW_FORMAT_NONE',
    'HIP_RES_VIEW_FORMAT_SIGNED_BC4',
    'HIP_RES_VIEW_FORMAT_SIGNED_BC5',
    'HIP_RES_VIEW_FORMAT_SIGNED_BC6H',
    'HIP_RES_VIEW_FORMAT_SINT_1X16', 'HIP_RES_VIEW_FORMAT_SINT_1X32',
    'HIP_RES_VIEW_FORMAT_SINT_1X8', 'HIP_RES_VIEW_FORMAT_SINT_2X16',
    'HIP_RES_VIEW_FORMAT_SINT_2X32', 'HIP_RES_VIEW_FORMAT_SINT_2X8',
    'HIP_RES_VIEW_FORMAT_SINT_4X16', 'HIP_RES_VIEW_FORMAT_SINT_4X32',
    'HIP_RES_VIEW_FORMAT_SINT_4X8', 'HIP_RES_VIEW_FORMAT_UINT_1X16',
    'HIP_RES_VIEW_FORMAT_UINT_1X32', 'HIP_RES_VIEW_FORMAT_UINT_1X8',
    'HIP_RES_VIEW_FORMAT_UINT_2X16', 'HIP_RES_VIEW_FORMAT_UINT_2X32',
    'HIP_RES_VIEW_FORMAT_UINT_2X8', 'HIP_RES_VIEW_FORMAT_UINT_4X16',
    'HIP_RES_VIEW_FORMAT_UINT_4X32', 'HIP_RES_VIEW_FORMAT_UINT_4X8',
    'HIP_RES_VIEW_FORMAT_UNSIGNED_BC1',
    'HIP_RES_VIEW_FORMAT_UNSIGNED_BC2',
    'HIP_RES_VIEW_FORMAT_UNSIGNED_BC3',
    'HIP_RES_VIEW_FORMAT_UNSIGNED_BC4',
    'HIP_RES_VIEW_FORMAT_UNSIGNED_BC5',
    'HIP_RES_VIEW_FORMAT_UNSIGNED_BC6H',
    'HIP_RES_VIEW_FORMAT_UNSIGNED_BC7', 'HIP_SUCCESS',
    'HIP_TEXTURE_DESC', 'HIP_TR_ADDRESS_MODE_BORDER',
    'HIP_TR_ADDRESS_MODE_CLAMP', 'HIP_TR_ADDRESS_MODE_MIRROR',
    'HIP_TR_ADDRESS_MODE_WRAP', 'HIP_TR_FILTER_MODE_LINEAR',
    'HIP_TR_FILTER_MODE_POINT', 'HIPaddress_mode',
    'HIPaddress_mode__enumvalues', 'HIPaddress_mode_enum',
    'HIPfilter_mode', 'HIPfilter_mode__enumvalues',
    'HIPfilter_mode_enum', 'HIPresourceViewFormat',
    'HIPresourceViewFormat__enumvalues', 'HIPresourceViewFormat_enum',
    'HIPresourcetype', 'HIPresourcetype__enumvalues',
    'HIPresourcetype_enum', '__hipGetPCH',
    '__hipPopCallConfiguration', '__hipPushCallConfiguration',
    'c__Ea_HIP_SUCCESS', 'dim3', 'hipAccessPolicyWindow',
    'hipAccessProperty', 'hipAccessPropertyNormal',
    'hipAccessPropertyPersisting', 'hipAccessPropertyStreaming',
    'hipAddressModeBorder', 'hipAddressModeClamp',
    'hipAddressModeMirror', 'hipAddressModeWrap', 'hipApiName',
    'hipArray', 'hipArray3DCreate', 'hipArray3DGetDescriptor',
    'hipArrayCreate', 'hipArrayDestroy', 'hipArrayGetDescriptor',
    'hipArrayGetInfo', 'hipArrayMapInfo',
    'hipArraySparseSubresourceType',
    'hipArraySparseSubresourceTypeMiptail',
    'hipArraySparseSubresourceTypeSparseLevel', 'hipArray_Format',
    'hipArray_const_t', 'hipArray_t', 'hipBindTexture',
    'hipBindTexture2D', 'hipBindTextureToArray',
    'hipBindTextureToMipmappedArray', 'hipChannelFormatDesc',
    'hipChannelFormatKind', 'hipChannelFormatKindFloat',
    'hipChannelFormatKindNone', 'hipChannelFormatKindSigned',
    'hipChannelFormatKindUnsigned', 'hipChooseDevice',
    'hipComputeMode', 'hipComputeModeDefault',
    'hipComputeModeExclusive', 'hipComputeModeExclusiveProcess',
    'hipComputeModeProhibited', 'hipConfigureCall',
    'hipCreateSurfaceObject', 'hipCreateTextureObject',
    'hipCtxCreate', 'hipCtxDestroy', 'hipCtxDisablePeerAccess',
    'hipCtxEnablePeerAccess', 'hipCtxGetApiVersion',
    'hipCtxGetCacheConfig', 'hipCtxGetCurrent', 'hipCtxGetDevice',
    'hipCtxGetFlags', 'hipCtxGetSharedMemConfig', 'hipCtxPopCurrent',
    'hipCtxPushCurrent', 'hipCtxSetCacheConfig', 'hipCtxSetCurrent',
    'hipCtxSetSharedMemConfig', 'hipCtxSynchronize', 'hipCtx_t',
    'hipDestroyExternalMemory', 'hipDestroyExternalSemaphore',
    'hipDestroySurfaceObject', 'hipDestroyTextureObject',
    'hipDevP2PAttrAccessSupported',
    'hipDevP2PAttrHipArrayAccessSupported',
    'hipDevP2PAttrNativeAtomicSupported',
    'hipDevP2PAttrPerformanceRank', 'hipDeviceArch_t',
    'hipDeviceAttributeAccessPolicyMaxWindowSize',
    'hipDeviceAttributeAmdSpecificBegin',
    'hipDeviceAttributeAmdSpecificEnd', 'hipDeviceAttributeArch',
    'hipDeviceAttributeAsicRevision',
    'hipDeviceAttributeAsyncEngineCount',
    'hipDeviceAttributeCanMapHostMemory',
    'hipDeviceAttributeCanUseHostPointerForRegisteredMem',
    'hipDeviceAttributeCanUseStreamWaitValue',
    'hipDeviceAttributeClockInstructionRate',
    'hipDeviceAttributeClockRate',
    'hipDeviceAttributeComputeCapabilityMajor',
    'hipDeviceAttributeComputeCapabilityMinor',
    'hipDeviceAttributeComputeMode',
    'hipDeviceAttributeComputePreemptionSupported',
    'hipDeviceAttributeConcurrentKernels',
    'hipDeviceAttributeConcurrentManagedAccess',
    'hipDeviceAttributeCooperativeLaunch',
    'hipDeviceAttributeCooperativeMultiDeviceLaunch',
    'hipDeviceAttributeCooperativeMultiDeviceUnmatchedBlockDim',
    'hipDeviceAttributeCooperativeMultiDeviceUnmatchedFunc',
    'hipDeviceAttributeCooperativeMultiDeviceUnmatchedGridDim',
    'hipDeviceAttributeCooperativeMultiDeviceUnmatchedSharedMem',
    'hipDeviceAttributeCudaCompatibleBegin',
    'hipDeviceAttributeCudaCompatibleEnd',
    'hipDeviceAttributeDeviceOverlap',
    'hipDeviceAttributeDirectManagedMemAccessFromHost',
    'hipDeviceAttributeEccEnabled',
    'hipDeviceAttributeFineGrainSupport', 'hipDeviceAttributeGcnArch',
    'hipDeviceAttributeGcnArchName',
    'hipDeviceAttributeGlobalL1CacheSupported',
    'hipDeviceAttributeHdpMemFlushCntl',
    'hipDeviceAttributeHdpRegFlushCntl',
    'hipDeviceAttributeHostNativeAtomicSupported',
    'hipDeviceAttributeImageSupport', 'hipDeviceAttributeIntegrated',
    'hipDeviceAttributeIsLargeBar',
    'hipDeviceAttributeIsMultiGpuBoard',
    'hipDeviceAttributeKernelExecTimeout',
    'hipDeviceAttributeL2CacheSize',
    'hipDeviceAttributeLocalL1CacheSupported',
    'hipDeviceAttributeLuid', 'hipDeviceAttributeLuidDeviceNodeMask',
    'hipDeviceAttributeManagedMemory',
    'hipDeviceAttributeMaxBlockDimX',
    'hipDeviceAttributeMaxBlockDimY',
    'hipDeviceAttributeMaxBlockDimZ',
    'hipDeviceAttributeMaxBlocksPerMultiProcessor',
    'hipDeviceAttributeMaxGridDimX', 'hipDeviceAttributeMaxGridDimY',
    'hipDeviceAttributeMaxGridDimZ', 'hipDeviceAttributeMaxPitch',
    'hipDeviceAttributeMaxRegistersPerBlock',
    'hipDeviceAttributeMaxRegistersPerMultiprocessor',
    'hipDeviceAttributeMaxSharedMemoryPerBlock',
    'hipDeviceAttributeMaxSharedMemoryPerMultiprocessor',
    'hipDeviceAttributeMaxSurface1D',
    'hipDeviceAttributeMaxSurface1DLayered',
    'hipDeviceAttributeMaxSurface2D',
    'hipDeviceAttributeMaxSurface2DLayered',
    'hipDeviceAttributeMaxSurface3D',
    'hipDeviceAttributeMaxSurfaceCubemap',
    'hipDeviceAttributeMaxSurfaceCubemapLayered',
    'hipDeviceAttributeMaxTexture1DLayered',
    'hipDeviceAttributeMaxTexture1DLinear',
    'hipDeviceAttributeMaxTexture1DMipmap',
    'hipDeviceAttributeMaxTexture1DWidth',
    'hipDeviceAttributeMaxTexture2DGather',
    'hipDeviceAttributeMaxTexture2DHeight',
    'hipDeviceAttributeMaxTexture2DLayered',
    'hipDeviceAttributeMaxTexture2DLinear',
    'hipDeviceAttributeMaxTexture2DMipmap',
    'hipDeviceAttributeMaxTexture2DWidth',
    'hipDeviceAttributeMaxTexture3DAlt',
    'hipDeviceAttributeMaxTexture3DDepth',
    'hipDeviceAttributeMaxTexture3DHeight',
    'hipDeviceAttributeMaxTexture3DWidth',
    'hipDeviceAttributeMaxTextureCubemap',
    'hipDeviceAttributeMaxTextureCubemapLayered',
    'hipDeviceAttributeMaxThreadsDim',
    'hipDeviceAttributeMaxThreadsPerBlock',
    'hipDeviceAttributeMaxThreadsPerMultiProcessor',
    'hipDeviceAttributeMemoryBusWidth',
    'hipDeviceAttributeMemoryClockRate',
    'hipDeviceAttributeMemoryPoolsSupported',
    'hipDeviceAttributeMultiGpuBoardGroupID',
    'hipDeviceAttributeMultiprocessorCount', 'hipDeviceAttributeName',
    'hipDeviceAttributePageableMemoryAccess',
    'hipDeviceAttributePageableMemoryAccessUsesHostPageTables',
    'hipDeviceAttributePciBusId', 'hipDeviceAttributePciDeviceId',
    'hipDeviceAttributePciDomainID',
    'hipDeviceAttributePersistingL2CacheMaxSize',
    'hipDeviceAttributePhysicalMultiProcessorCount',
    'hipDeviceAttributeReservedSharedMemPerBlock',
    'hipDeviceAttributeSharedMemPerBlockOptin',
    'hipDeviceAttributeSharedMemPerMultiprocessor',
    'hipDeviceAttributeSingleToDoublePrecisionPerfRatio',
    'hipDeviceAttributeStreamPrioritiesSupported',
    'hipDeviceAttributeSurfaceAlignment',
    'hipDeviceAttributeTccDriver',
    'hipDeviceAttributeTextureAlignment',
    'hipDeviceAttributeTexturePitchAlignment',
    'hipDeviceAttributeTotalConstantMemory',
    'hipDeviceAttributeTotalGlobalMem',
    'hipDeviceAttributeUnifiedAddressing', 'hipDeviceAttributeUuid',
    'hipDeviceAttributeVendorSpecificBegin',
    'hipDeviceAttributeVirtualMemoryManagementSupported',
    'hipDeviceAttributeWallClockRate', 'hipDeviceAttributeWarpSize',
    'hipDeviceAttribute_t', 'hipDeviceCanAccessPeer',
    'hipDeviceComputeCapability', 'hipDeviceDisablePeerAccess',
    'hipDeviceEnablePeerAccess', 'hipDeviceGet',
    'hipDeviceGetAttribute', 'hipDeviceGetByPCIBusId',
    'hipDeviceGetCacheConfig', 'hipDeviceGetDefaultMemPool',
    'hipDeviceGetGraphMemAttribute', 'hipDeviceGetLimit',
    'hipDeviceGetMemPool', 'hipDeviceGetName',
    'hipDeviceGetP2PAttribute', 'hipDeviceGetPCIBusId',
    'hipDeviceGetSharedMemConfig', 'hipDeviceGetStreamPriorityRange',
    'hipDeviceGetUuid', 'hipDeviceGraphMemTrim', 'hipDeviceP2PAttr',
    'hipDevicePrimaryCtxGetState', 'hipDevicePrimaryCtxRelease',
    'hipDevicePrimaryCtxReset', 'hipDevicePrimaryCtxRetain',
    'hipDevicePrimaryCtxSetFlags', 'hipDeviceProp_t',
    'hipDeviceReset', 'hipDeviceSetCacheConfig',
    'hipDeviceSetGraphMemAttribute', 'hipDeviceSetLimit',
    'hipDeviceSetMemPool', 'hipDeviceSetSharedMemConfig',
    'hipDeviceSynchronize', 'hipDeviceTotalMem', 'hipDevice_t',
    'hipDeviceptr_t', 'hipDriverGetVersion', 'hipDrvGetErrorName',
    'hipDrvGetErrorString', 'hipDrvMemcpy2DUnaligned',
    'hipDrvMemcpy3D', 'hipDrvMemcpy3DAsync',
    'hipDrvPointerGetAttributes', 'hipErrorAlreadyAcquired',
    'hipErrorAlreadyMapped', 'hipErrorArrayIsMapped',
    'hipErrorAssert', 'hipErrorCapturedEvent',
    'hipErrorContextAlreadyCurrent', 'hipErrorContextAlreadyInUse',
    'hipErrorContextIsDestroyed', 'hipErrorCooperativeLaunchTooLarge',
    'hipErrorDeinitialized', 'hipErrorECCNotCorrectable',
    'hipErrorFileNotFound', 'hipErrorGraphExecUpdateFailure',
    'hipErrorHostMemoryAlreadyRegistered',
    'hipErrorHostMemoryNotRegistered', 'hipErrorIllegalAddress',
    'hipErrorIllegalState', 'hipErrorInitializationError',
    'hipErrorInsufficientDriver', 'hipErrorInvalidConfiguration',
    'hipErrorInvalidContext', 'hipErrorInvalidDevice',
    'hipErrorInvalidDeviceFunction', 'hipErrorInvalidDevicePointer',
    'hipErrorInvalidGraphicsContext', 'hipErrorInvalidHandle',
    'hipErrorInvalidImage', 'hipErrorInvalidKernelFile',
    'hipErrorInvalidMemcpyDirection', 'hipErrorInvalidPitchValue',
    'hipErrorInvalidResourceHandle', 'hipErrorInvalidSource',
    'hipErrorInvalidSymbol', 'hipErrorInvalidValue',
    'hipErrorLaunchFailure', 'hipErrorLaunchOutOfResources',
    'hipErrorLaunchTimeOut', 'hipErrorMapBufferObjectFailed',
    'hipErrorMapFailed', 'hipErrorMemoryAllocation',
    'hipErrorMissingConfiguration', 'hipErrorNoBinaryForGpu',
    'hipErrorNoDevice', 'hipErrorNotFound', 'hipErrorNotInitialized',
    'hipErrorNotMapped', 'hipErrorNotMappedAsArray',
    'hipErrorNotMappedAsPointer', 'hipErrorNotReady',
    'hipErrorNotSupported', 'hipErrorOperatingSystem',
    'hipErrorOutOfMemory', 'hipErrorPeerAccessAlreadyEnabled',
    'hipErrorPeerAccessNotEnabled', 'hipErrorPeerAccessUnsupported',
    'hipErrorPriorLaunchFailure', 'hipErrorProfilerAlreadyStarted',
    'hipErrorProfilerAlreadyStopped', 'hipErrorProfilerDisabled',
    'hipErrorProfilerNotInitialized', 'hipErrorRuntimeMemory',
    'hipErrorRuntimeOther', 'hipErrorSetOnActiveProcess',
    'hipErrorSharedObjectInitFailed',
    'hipErrorSharedObjectSymbolNotFound',
    'hipErrorStreamCaptureImplicit',
    'hipErrorStreamCaptureInvalidated',
    'hipErrorStreamCaptureIsolation', 'hipErrorStreamCaptureMerge',
    'hipErrorStreamCaptureUnjoined', 'hipErrorStreamCaptureUnmatched',
    'hipErrorStreamCaptureUnsupported',
    'hipErrorStreamCaptureWrongThread', 'hipErrorTbd',
    'hipErrorUnknown', 'hipErrorUnmapFailed',
    'hipErrorUnsupportedLimit', 'hipError_t', 'hipEventCreate',
    'hipEventCreateWithFlags', 'hipEventDestroy',
    'hipEventElapsedTime', 'hipEventQuery', 'hipEventRecord',
    'hipEventSynchronize', 'hipEvent_t',
    'hipExtGetLinkTypeAndHopCount', 'hipExtLaunchKernel',
    'hipExtLaunchMultiKernelMultiDevice', 'hipExtMallocWithFlags',
    'hipExtStreamCreateWithCUMask', 'hipExtStreamGetCUMask',
    'hipExtent', 'hipExternalMemoryBufferDesc',
    'hipExternalMemoryGetMappedBuffer', 'hipExternalMemoryHandleDesc',
    'hipExternalMemoryHandleType',
    'hipExternalMemoryHandleTypeD3D11Resource',
    'hipExternalMemoryHandleTypeD3D11ResourceKmt',
    'hipExternalMemoryHandleTypeD3D12Heap',
    'hipExternalMemoryHandleTypeD3D12Resource',
    'hipExternalMemoryHandleTypeOpaqueFd',
    'hipExternalMemoryHandleTypeOpaqueWin32',
    'hipExternalMemoryHandleTypeOpaqueWin32Kmt',
    'hipExternalMemoryHandleType__enumvalues',
    'hipExternalMemoryHandleType_enum', 'hipExternalMemory_t',
    'hipExternalSemaphoreHandleDesc',
    'hipExternalSemaphoreHandleType',
    'hipExternalSemaphoreHandleTypeD3D12Fence',
    'hipExternalSemaphoreHandleTypeOpaqueFd',
    'hipExternalSemaphoreHandleTypeOpaqueWin32',
    'hipExternalSemaphoreHandleTypeOpaqueWin32Kmt',
    'hipExternalSemaphoreHandleType__enumvalues',
    'hipExternalSemaphoreHandleType_enum',
    'hipExternalSemaphoreSignalNodeParams',
    'hipExternalSemaphoreSignalParams',
    'hipExternalSemaphoreWaitNodeParams',
    'hipExternalSemaphoreWaitParams', 'hipExternalSemaphore_t',
    'hipFilterModeLinear', 'hipFilterModePoint', 'hipFree',
    'hipFreeArray', 'hipFreeAsync', 'hipFreeHost',
    'hipFreeMipmappedArray', 'hipFuncAttribute',
    'hipFuncAttributeMax',
    'hipFuncAttributeMaxDynamicSharedMemorySize',
    'hipFuncAttributePreferredSharedMemoryCarveout',
    'hipFuncAttributes', 'hipFuncCachePreferEqual',
    'hipFuncCachePreferL1', 'hipFuncCachePreferNone',
    'hipFuncCachePreferShared', 'hipFuncCache_t',
    'hipFuncGetAttribute', 'hipFuncGetAttributes',
    'hipFuncSetAttribute', 'hipFuncSetCacheConfig',
    'hipFuncSetSharedMemConfig', 'hipFunctionLaunchParams',
    'hipFunction_attribute', 'hipFunction_t', 'hipGLDeviceList',
    'hipGLDeviceListAll', 'hipGLDeviceListCurrentFrame',
    'hipGLDeviceListNextFrame', 'hipGLGetDevices',
    'hipGetChannelDesc', 'hipGetDevice', 'hipGetDeviceCount',
    'hipGetDeviceFlags', 'hipGetDeviceProperties', 'hipGetErrorName',
    'hipGetErrorString', 'hipGetLastError',
    'hipGetMipmappedArrayLevel', 'hipGetStreamDeviceId',
    'hipGetSymbolAddress', 'hipGetSymbolSize',
    'hipGetTextureAlignmentOffset', 'hipGetTextureObjectResourceDesc',
    'hipGetTextureObjectResourceViewDesc',
    'hipGetTextureObjectTextureDesc', 'hipGetTextureReference',
    'hipGraphAddChildGraphNode', 'hipGraphAddDependencies',
    'hipGraphAddEmptyNode', 'hipGraphAddEventRecordNode',
    'hipGraphAddEventWaitNode',
    'hipGraphAddExternalSemaphoresSignalNode',
    'hipGraphAddExternalSemaphoresWaitNode', 'hipGraphAddHostNode',
    'hipGraphAddKernelNode', 'hipGraphAddMemAllocNode',
    'hipGraphAddMemFreeNode', 'hipGraphAddMemcpyNode',
    'hipGraphAddMemcpyNode1D', 'hipGraphAddMemcpyNodeFromSymbol',
    'hipGraphAddMemcpyNodeToSymbol', 'hipGraphAddMemsetNode',
    'hipGraphChildGraphNodeGetGraph', 'hipGraphClone',
    'hipGraphCreate', 'hipGraphDebugDotFlags',
    'hipGraphDebugDotFlagsEventNodeParams',
    'hipGraphDebugDotFlagsExtSemasSignalNodeParams',
    'hipGraphDebugDotFlagsExtSemasWaitNodeParams',
    'hipGraphDebugDotFlagsHandles',
    'hipGraphDebugDotFlagsHostNodeParams',
    'hipGraphDebugDotFlagsKernelNodeAttributes',
    'hipGraphDebugDotFlagsKernelNodeParams',
    'hipGraphDebugDotFlagsMemcpyNodeParams',
    'hipGraphDebugDotFlagsMemsetNodeParams',
    'hipGraphDebugDotFlagsVerbose', 'hipGraphDebugDotPrint',
    'hipGraphDestroy', 'hipGraphDestroyNode',
    'hipGraphEventRecordNodeGetEvent',
    'hipGraphEventRecordNodeSetEvent',
    'hipGraphEventWaitNodeGetEvent', 'hipGraphEventWaitNodeSetEvent',
    'hipGraphExecChildGraphNodeSetParams', 'hipGraphExecDestroy',
    'hipGraphExecEventRecordNodeSetEvent',
    'hipGraphExecEventWaitNodeSetEvent',
    'hipGraphExecExternalSemaphoresSignalNodeSetParams',
    'hipGraphExecExternalSemaphoresWaitNodeSetParams',
    'hipGraphExecHostNodeSetParams',
    'hipGraphExecKernelNodeSetParams',
    'hipGraphExecMemcpyNodeSetParams',
    'hipGraphExecMemcpyNodeSetParams1D',
    'hipGraphExecMemcpyNodeSetParamsFromSymbol',
    'hipGraphExecMemcpyNodeSetParamsToSymbol',
    'hipGraphExecMemsetNodeSetParams', 'hipGraphExecUpdate',
    'hipGraphExecUpdateError',
    'hipGraphExecUpdateErrorFunctionChanged',
    'hipGraphExecUpdateErrorNodeTypeChanged',
    'hipGraphExecUpdateErrorNotSupported',
    'hipGraphExecUpdateErrorParametersChanged',
    'hipGraphExecUpdateErrorTopologyChanged',
    'hipGraphExecUpdateErrorUnsupportedFunctionChange',
    'hipGraphExecUpdateResult', 'hipGraphExecUpdateSuccess',
    'hipGraphExec_t', 'hipGraphExternalSemaphoresSignalNodeGetParams',
    'hipGraphExternalSemaphoresSignalNodeSetParams',
    'hipGraphExternalSemaphoresWaitNodeGetParams',
    'hipGraphExternalSemaphoresWaitNodeSetParams', 'hipGraphGetEdges',
    'hipGraphGetNodes', 'hipGraphGetRootNodes',
    'hipGraphHostNodeGetParams', 'hipGraphHostNodeSetParams',
    'hipGraphInstantiate', 'hipGraphInstantiateFlagAutoFreeOnLaunch',
    'hipGraphInstantiateFlagDeviceLaunch',
    'hipGraphInstantiateFlagUpload',
    'hipGraphInstantiateFlagUseNodePriority',
    'hipGraphInstantiateFlags', 'hipGraphInstantiateWithFlags',
    'hipGraphKernelNodeCopyAttributes',
    'hipGraphKernelNodeGetAttribute', 'hipGraphKernelNodeGetParams',
    'hipGraphKernelNodeSetAttribute', 'hipGraphKernelNodeSetParams',
    'hipGraphLaunch', 'hipGraphMemAllocNodeGetParams',
    'hipGraphMemAttrReservedMemCurrent',
    'hipGraphMemAttrReservedMemHigh', 'hipGraphMemAttrUsedMemCurrent',
    'hipGraphMemAttrUsedMemHigh', 'hipGraphMemAttributeType',
    'hipGraphMemFreeNodeGetParams', 'hipGraphMemcpyNodeGetParams',
    'hipGraphMemcpyNodeSetParams', 'hipGraphMemcpyNodeSetParams1D',
    'hipGraphMemcpyNodeSetParamsFromSymbol',
    'hipGraphMemcpyNodeSetParamsToSymbol',
    'hipGraphMemsetNodeGetParams', 'hipGraphMemsetNodeSetParams',
    'hipGraphNodeFindInClone', 'hipGraphNodeGetDependencies',
    'hipGraphNodeGetDependentNodes', 'hipGraphNodeGetEnabled',
    'hipGraphNodeGetType', 'hipGraphNodeSetEnabled',
    'hipGraphNodeType', 'hipGraphNodeTypeCount',
    'hipGraphNodeTypeEmpty', 'hipGraphNodeTypeEventRecord',
    'hipGraphNodeTypeExtSemaphoreSignal',
    'hipGraphNodeTypeExtSemaphoreWait', 'hipGraphNodeTypeGraph',
    'hipGraphNodeTypeHost', 'hipGraphNodeTypeKernel',
    'hipGraphNodeTypeMemAlloc', 'hipGraphNodeTypeMemFree',
    'hipGraphNodeTypeMemcpy', 'hipGraphNodeTypeMemcpyFromSymbol',
    'hipGraphNodeTypeMemcpyToSymbol', 'hipGraphNodeTypeMemset',
    'hipGraphNodeTypeWaitEvent', 'hipGraphNode_t',
    'hipGraphReleaseUserObject', 'hipGraphRemoveDependencies',
    'hipGraphRetainUserObject', 'hipGraphUpload',
    'hipGraphUserObjectMove', 'hipGraph_t',
    'hipGraphicsGLRegisterBuffer', 'hipGraphicsGLRegisterImage',
    'hipGraphicsMapResources', 'hipGraphicsRegisterFlags',
    'hipGraphicsRegisterFlagsNone',
    'hipGraphicsRegisterFlagsReadOnly',
    'hipGraphicsRegisterFlagsSurfaceLoadStore',
    'hipGraphicsRegisterFlagsTextureGather',
    'hipGraphicsRegisterFlagsWriteDiscard', 'hipGraphicsResource',
    'hipGraphicsResourceGetMappedPointer', 'hipGraphicsResource_t',
    'hipGraphicsSubResourceGetMappedArray',
    'hipGraphicsUnmapResources', 'hipGraphicsUnregisterResource',
    'hipHostAlloc', 'hipHostFn_t', 'hipHostFree',
    'hipHostGetDevicePointer', 'hipHostGetFlags', 'hipHostMalloc',
    'hipHostNodeParams', 'hipHostRegister', 'hipHostUnregister',
    'hipImportExternalMemory', 'hipImportExternalSemaphore',
    'hipInit', 'hipIpcCloseMemHandle', 'hipIpcEventHandle_t',
    'hipIpcGetEventHandle', 'hipIpcGetMemHandle', 'hipIpcMemHandle_t',
    'hipIpcOpenEventHandle', 'hipIpcOpenMemHandle', 'hipJitOption',
    'hipJitOptionCacheMode', 'hipJitOptionErrorLogBuffer',
    'hipJitOptionErrorLogBufferSizeBytes',
    'hipJitOptionFallbackStrategy', 'hipJitOptionFastCompile',
    'hipJitOptionGenerateDebugInfo', 'hipJitOptionGenerateLineInfo',
    'hipJitOptionInfoLogBuffer', 'hipJitOptionInfoLogBufferSizeBytes',
    'hipJitOptionLogVerbose', 'hipJitOptionMaxRegisters',
    'hipJitOptionNumOptions', 'hipJitOptionOptimizationLevel',
    'hipJitOptionSm3xOpt', 'hipJitOptionTarget',
    'hipJitOptionTargetFromContext', 'hipJitOptionThreadsPerBlock',
    'hipJitOptionWallTime', 'hipKernelNameRef',
    'hipKernelNameRefByPtr', 'hipKernelNodeAttrID',
    'hipKernelNodeAttrValue',
    'hipKernelNodeAttributeAccessPolicyWindow',
    'hipKernelNodeAttributeCooperative', 'hipKernelNodeParams',
    'hipLaunchByPtr', 'hipLaunchCooperativeKernel',
    'hipLaunchCooperativeKernelMultiDevice', 'hipLaunchHostFunc',
    'hipLaunchKernel', 'hipLaunchParams', 'hipLimitMallocHeapSize',
    'hipLimitPrintfFifoSize', 'hipLimitRange', 'hipLimitStackSize',
    'hipLimit_t', 'hipMalloc', 'hipMalloc3D', 'hipMalloc3DArray',
    'hipMallocArray', 'hipMallocAsync', 'hipMallocFromPoolAsync',
    'hipMallocHost', 'hipMallocManaged', 'hipMallocMipmappedArray',
    'hipMallocPitch', 'hipMemAccessDesc', 'hipMemAccessFlags',
    'hipMemAccessFlagsProtNone', 'hipMemAccessFlagsProtRead',
    'hipMemAccessFlagsProtReadWrite', 'hipMemAddressFree',
    'hipMemAddressReserve', 'hipMemAdvise',
    'hipMemAdviseSetAccessedBy', 'hipMemAdviseSetCoarseGrain',
    'hipMemAdviseSetPreferredLocation', 'hipMemAdviseSetReadMostly',
    'hipMemAdviseUnsetAccessedBy', 'hipMemAdviseUnsetCoarseGrain',
    'hipMemAdviseUnsetPreferredLocation',
    'hipMemAdviseUnsetReadMostly', 'hipMemAllocHost',
    'hipMemAllocNodeParams', 'hipMemAllocPitch',
    'hipMemAllocationGranularityMinimum',
    'hipMemAllocationGranularityRecommended',
    'hipMemAllocationGranularity_flags', 'hipMemAllocationHandleType',
    'hipMemAllocationProp', 'hipMemAllocationType',
    'hipMemAllocationTypeInvalid', 'hipMemAllocationTypeMax',
    'hipMemAllocationTypePinned', 'hipMemCreate',
    'hipMemExportToShareableHandle',
    'hipMemGenericAllocationHandle_t', 'hipMemGetAccess',
    'hipMemGetAddressRange', 'hipMemGetAllocationGranularity',
    'hipMemGetAllocationPropertiesFromHandle', 'hipMemGetInfo',
    'hipMemHandleType', 'hipMemHandleTypeGeneric',
    'hipMemHandleTypeNone', 'hipMemHandleTypePosixFileDescriptor',
    'hipMemHandleTypeWin32', 'hipMemHandleTypeWin32Kmt',
    'hipMemImportFromShareableHandle', 'hipMemLocation',
    'hipMemLocationType', 'hipMemLocationTypeDevice',
    'hipMemLocationTypeInvalid', 'hipMemMap', 'hipMemMapArrayAsync',
    'hipMemOperationType', 'hipMemOperationTypeMap',
    'hipMemOperationTypeUnmap', 'hipMemPoolAttr',
    'hipMemPoolAttrReleaseThreshold',
    'hipMemPoolAttrReservedMemCurrent',
    'hipMemPoolAttrReservedMemHigh', 'hipMemPoolAttrUsedMemCurrent',
    'hipMemPoolAttrUsedMemHigh', 'hipMemPoolCreate',
    'hipMemPoolDestroy', 'hipMemPoolExportPointer',
    'hipMemPoolExportToShareableHandle', 'hipMemPoolGetAccess',
    'hipMemPoolGetAttribute', 'hipMemPoolImportFromShareableHandle',
    'hipMemPoolImportPointer', 'hipMemPoolProps',
    'hipMemPoolPtrExportData',
    'hipMemPoolReuseAllowInternalDependencies',
    'hipMemPoolReuseAllowOpportunistic',
    'hipMemPoolReuseFollowEventDependencies', 'hipMemPoolSetAccess',
    'hipMemPoolSetAttribute', 'hipMemPoolTrimTo', 'hipMemPool_t',
    'hipMemPrefetchAsync', 'hipMemPtrGetInfo', 'hipMemRangeAttribute',
    'hipMemRangeAttributeAccessedBy',
    'hipMemRangeAttributeCoherencyMode',
    'hipMemRangeAttributeLastPrefetchLocation',
    'hipMemRangeAttributePreferredLocation',
    'hipMemRangeAttributeReadMostly', 'hipMemRangeCoherencyMode',
    'hipMemRangeCoherencyModeCoarseGrain',
    'hipMemRangeCoherencyModeFineGrain',
    'hipMemRangeCoherencyModeIndeterminate',
    'hipMemRangeGetAttribute', 'hipMemRangeGetAttributes',
    'hipMemRelease', 'hipMemRetainAllocationHandle',
    'hipMemSetAccess', 'hipMemUnmap', 'hipMemcpy', 'hipMemcpy2D',
    'hipMemcpy2DAsync', 'hipMemcpy2DFromArray',
    'hipMemcpy2DFromArrayAsync', 'hipMemcpy2DToArray',
    'hipMemcpy2DToArrayAsync', 'hipMemcpy3D', 'hipMemcpy3DAsync',
    'hipMemcpy3DParms', 'hipMemcpyAsync', 'hipMemcpyAtoH',
    'hipMemcpyDefault', 'hipMemcpyDeviceToDevice',
    'hipMemcpyDeviceToHost', 'hipMemcpyDtoD', 'hipMemcpyDtoDAsync',
    'hipMemcpyDtoH', 'hipMemcpyDtoHAsync', 'hipMemcpyFromArray',
    'hipMemcpyFromSymbol', 'hipMemcpyFromSymbolAsync',
    'hipMemcpyHostToDevice', 'hipMemcpyHostToHost', 'hipMemcpyHtoA',
    'hipMemcpyHtoD', 'hipMemcpyHtoDAsync', 'hipMemcpyKind',
    'hipMemcpyParam2D', 'hipMemcpyParam2DAsync', 'hipMemcpyPeer',
    'hipMemcpyPeerAsync', 'hipMemcpyToArray', 'hipMemcpyToSymbol',
    'hipMemcpyToSymbolAsync', 'hipMemcpyWithStream',
    'hipMemoryAdvise', 'hipMemoryType', 'hipMemoryTypeArray',
    'hipMemoryTypeDevice', 'hipMemoryTypeHost',
    'hipMemoryTypeManaged', 'hipMemoryTypeUnified', 'hipMemset',
    'hipMemset2D', 'hipMemset2DAsync', 'hipMemset3D',
    'hipMemset3DAsync', 'hipMemsetAsync', 'hipMemsetD16',
    'hipMemsetD16Async', 'hipMemsetD32', 'hipMemsetD32Async',
    'hipMemsetD8', 'hipMemsetD8Async', 'hipMemsetParams',
    'hipMipmappedArray', 'hipMipmappedArrayCreate',
    'hipMipmappedArrayDestroy', 'hipMipmappedArrayGetLevel',
    'hipMipmappedArray_const_t', 'hipMipmappedArray_t',
    'hipModuleGetFunction', 'hipModuleGetGlobal',
    'hipModuleGetTexRef', 'hipModuleLaunchCooperativeKernel',
    'hipModuleLaunchCooperativeKernelMultiDevice',
    'hipModuleLaunchKernel', 'hipModuleLoad', 'hipModuleLoadData',
    'hipModuleLoadDataEx',
    'hipModuleOccupancyMaxActiveBlocksPerMultiprocessor',
    'hipModuleOccupancyMaxActiveBlocksPerMultiprocessorWithFlags',
    'hipModuleOccupancyMaxPotentialBlockSize',
    'hipModuleOccupancyMaxPotentialBlockSizeWithFlags',
    'hipModuleUnload', 'hipModule_t',
    'hipOccupancyMaxActiveBlocksPerMultiprocessor',
    'hipOccupancyMaxActiveBlocksPerMultiprocessorWithFlags',
    'hipOccupancyMaxPotentialBlockSize', 'hipPeekAtLastError',
    'hipPitchedPtr', 'hipPointerAttribute_t',
    'hipPointerGetAttribute', 'hipPointerGetAttributes',
    'hipPointerSetAttribute', 'hipPointer_attribute', 'hipPos',
    'hipProfilerStart', 'hipProfilerStop', 'hipReadModeElementType',
    'hipReadModeNormalizedFloat', 'hipResViewFormatFloat1',
    'hipResViewFormatFloat2', 'hipResViewFormatFloat4',
    'hipResViewFormatHalf1', 'hipResViewFormatHalf2',
    'hipResViewFormatHalf4', 'hipResViewFormatNone',
    'hipResViewFormatSignedBlockCompressed4',
    'hipResViewFormatSignedBlockCompressed5',
    'hipResViewFormatSignedBlockCompressed6H',
    'hipResViewFormatSignedChar1', 'hipResViewFormatSignedChar2',
    'hipResViewFormatSignedChar4', 'hipResViewFormatSignedInt1',
    'hipResViewFormatSignedInt2', 'hipResViewFormatSignedInt4',
    'hipResViewFormatSignedShort1', 'hipResViewFormatSignedShort2',
    'hipResViewFormatSignedShort4',
    'hipResViewFormatUnsignedBlockCompressed1',
    'hipResViewFormatUnsignedBlockCompressed2',
    'hipResViewFormatUnsignedBlockCompressed3',
    'hipResViewFormatUnsignedBlockCompressed4',
    'hipResViewFormatUnsignedBlockCompressed5',
    'hipResViewFormatUnsignedBlockCompressed6H',
    'hipResViewFormatUnsignedBlockCompressed7',
    'hipResViewFormatUnsignedChar1', 'hipResViewFormatUnsignedChar2',
    'hipResViewFormatUnsignedChar4', 'hipResViewFormatUnsignedInt1',
    'hipResViewFormatUnsignedInt2', 'hipResViewFormatUnsignedInt4',
    'hipResViewFormatUnsignedShort1',
    'hipResViewFormatUnsignedShort2',
    'hipResViewFormatUnsignedShort4', 'hipResourceDesc',
    'hipResourceType', 'hipResourceTypeArray',
    'hipResourceTypeLinear', 'hipResourceTypeMipmappedArray',
    'hipResourceTypePitch2D', 'hipResourceViewFormat',
    'hipResourcetype', 'hipResourcetype__enumvalues',
    'hipRuntimeGetVersion', 'hipSetDevice', 'hipSetDeviceFlags',
    'hipSetupArgument', 'hipSharedMemBankSizeDefault',
    'hipSharedMemBankSizeEightByte', 'hipSharedMemBankSizeFourByte',
    'hipSharedMemConfig', 'hipSignalExternalSemaphoresAsync',
    'hipStreamAddCallback', 'hipStreamAddCaptureDependencies',
    'hipStreamAttachMemAsync', 'hipStreamBeginCapture',
    'hipStreamCallback_t', 'hipStreamCaptureMode',
    'hipStreamCaptureModeGlobal', 'hipStreamCaptureModeRelaxed',
    'hipStreamCaptureModeThreadLocal', 'hipStreamCaptureStatus',
    'hipStreamCaptureStatusActive',
    'hipStreamCaptureStatusInvalidated', 'hipStreamCaptureStatusNone',
    'hipStreamCreate', 'hipStreamCreateWithFlags',
    'hipStreamCreateWithPriority', 'hipStreamDestroy',
    'hipStreamEndCapture', 'hipStreamGetCaptureInfo',
    'hipStreamGetCaptureInfo_v2', 'hipStreamGetDevice',
    'hipStreamGetFlags', 'hipStreamGetPriority',
    'hipStreamIsCapturing', 'hipStreamQuery',
    'hipStreamSetCaptureDependencies', 'hipStreamSynchronize',
    'hipStreamUpdateCaptureDependencies',
    'hipStreamUpdateCaptureDependenciesFlags', 'hipStreamWaitEvent',
    'hipStreamWaitValue32', 'hipStreamWaitValue64',
    'hipStreamWriteValue32', 'hipStreamWriteValue64', 'hipStream_t',
    'hipSuccess', 'hipSurfaceObject_t', 'hipTexObjectCreate',
    'hipTexObjectDestroy', 'hipTexObjectGetResourceDesc',
    'hipTexObjectGetResourceViewDesc', 'hipTexObjectGetTextureDesc',
    'hipTexRefGetAddress', 'hipTexRefGetAddressMode',
    'hipTexRefGetFilterMode', 'hipTexRefGetFlags',
    'hipTexRefGetFormat', 'hipTexRefGetMaxAnisotropy',
    'hipTexRefGetMipMappedArray', 'hipTexRefGetMipmapFilterMode',
    'hipTexRefGetMipmapLevelBias', 'hipTexRefGetMipmapLevelClamp',
    'hipTexRefSetAddress', 'hipTexRefSetAddress2D',
    'hipTexRefSetAddressMode', 'hipTexRefSetArray',
    'hipTexRefSetBorderColor', 'hipTexRefSetFilterMode',
    'hipTexRefSetFlags', 'hipTexRefSetFormat',
    'hipTexRefSetMaxAnisotropy', 'hipTexRefSetMipmapFilterMode',
    'hipTexRefSetMipmapLevelBias', 'hipTexRefSetMipmapLevelClamp',
    'hipTexRefSetMipmappedArray', 'hipTextureAddressMode',
    'hipTextureFilterMode', 'hipTextureObject_t',
    'hipTextureReadMode', 'hipThreadExchangeStreamCaptureMode',
    'hipUUID', 'hipUnbindTexture', 'hipUserObjectCreate',
    'hipUserObjectFlags', 'hipUserObjectNoDestructorSync',
    'hipUserObjectRelease', 'hipUserObjectRetain',
    'hipUserObjectRetainFlags', 'hipUserObject_t',
    'hipWaitExternalSemaphoresAsync', 'hip_Memcpy2D', 'hiparray',
    'hipmipmappedArray', 'hiprtcAddNameExpression',
    'hiprtcCompileProgram', 'hiprtcCreateProgram',
    'hiprtcDestroyProgram', 'hiprtcGetBitcode',
    'hiprtcGetBitcodeSize', 'hiprtcGetCode', 'hiprtcGetCodeSize',
    'hiprtcGetErrorString', 'hiprtcGetLoweredName',
    'hiprtcGetProgramLog', 'hiprtcGetProgramLogSize',
    'hiprtcJITInputType', 'hiprtcJIT_option', 'hiprtcLinkAddData',
    'hiprtcLinkAddFile', 'hiprtcLinkComplete', 'hiprtcLinkCreate',
    'hiprtcLinkDestroy', 'hiprtcLinkState', 'hiprtcProgram',
    'hiprtcResult', 'hiprtcVersion', 'make_hipExtent',
    'make_hipPitchedPtr', 'make_hipPos', 'size_t',
    'struct_HIP_ARRAY3D_DESCRIPTOR', 'struct_HIP_ARRAY_DESCRIPTOR',
    'struct_HIP_MEMCPY3D', 'struct_HIP_RESOURCE_DESC_st',
    'struct_HIP_RESOURCE_DESC_st_0_array',
    'struct_HIP_RESOURCE_DESC_st_0_linear',
    'struct_HIP_RESOURCE_DESC_st_0_mipmap',
    'struct_HIP_RESOURCE_DESC_st_0_pitch2D',
    'struct_HIP_RESOURCE_DESC_st_0_reserved',
    'struct_HIP_RESOURCE_VIEW_DESC_st', 'struct_HIP_TEXTURE_DESC_st',
    'struct___hip_surface', 'struct___hip_texture',
    'struct__hipGraphicsResource', 'struct__hiprtcProgram',
    'struct_c__SA_hipDeviceArch_t', 'struct_dim3',
    'struct_hipAccessPolicyWindow', 'struct_hipArray',
    'struct_hipArrayMapInfo', 'struct_hipArrayMapInfo_1_miptail',
    'struct_hipArrayMapInfo_1_sparseLevel',
    'struct_hipChannelFormatDesc', 'struct_hipDeviceProp_t',
    'struct_hipExtent', 'struct_hipExternalMemoryBufferDesc_st',
    'struct_hipExternalMemoryHandleDesc_st',
    'struct_hipExternalMemoryHandleDesc_st_0_win32',
    'struct_hipExternalSemaphoreHandleDesc_st',
    'struct_hipExternalSemaphoreHandleDesc_st_0_win32',
    'struct_hipExternalSemaphoreSignalNodeParams',
    'struct_hipExternalSemaphoreSignalParams_st',
    'struct_hipExternalSemaphoreSignalParams_st_0_fence',
    'struct_hipExternalSemaphoreSignalParams_st_0_keyedMutex',
    'struct_hipExternalSemaphoreSignalParams_st_params',
    'struct_hipExternalSemaphoreWaitNodeParams',
    'struct_hipExternalSemaphoreWaitParams_st',
    'struct_hipExternalSemaphoreWaitParams_st_0_fence',
    'struct_hipExternalSemaphoreWaitParams_st_0_keyedMutex',
    'struct_hipExternalSemaphoreWaitParams_st_params',
    'struct_hipFuncAttributes', 'struct_hipFunctionLaunchParams_t',
    'struct_hipGraphExec', 'struct_hipGraphNode',
    'struct_hipHostNodeParams', 'struct_hipIpcEventHandle_st',
    'struct_hipIpcMemHandle_st', 'struct_hipKernelNodeParams',
    'struct_hipLaunchParams_t', 'struct_hipMemAccessDesc',
    'struct_hipMemAllocNodeParams', 'struct_hipMemAllocationProp',
    'struct_hipMemAllocationProp_allocFlags', 'struct_hipMemLocation',
    'struct_hipMemPoolProps', 'struct_hipMemPoolPtrExportData',
    'struct_hipMemcpy3DParms', 'struct_hipMemsetParams',
    'struct_hipMipmappedArray', 'struct_hipPitchedPtr',
    'struct_hipPointerAttribute_t', 'struct_hipPos',
    'struct_hipResourceDesc', 'struct_hipResourceDesc_0_array',
    'struct_hipResourceDesc_0_linear',
    'struct_hipResourceDesc_0_mipmap',
    'struct_hipResourceDesc_0_pitch2D', 'struct_hipResourceViewDesc',
    'struct_hipTextureDesc', 'struct_hipUUID_t',
    'struct_hipUserObject', 'struct_hip_Memcpy2D', 'struct_ihipCtx_t',
    'struct_ihipEvent_t', 'struct_ihipGraph',
    'struct_ihipMemGenericAllocationHandle',
    'struct_ihipMemPoolHandle_t', 'struct_ihipModuleSymbol_t',
    'struct_ihipModule_t', 'struct_ihipStream_t',
    'struct_ihiprtcLinkState', 'struct_textureReference', 'uint32_t',
    'uint64_t', 'union_HIP_RESOURCE_DESC_st_res',
    'union_hipArrayMapInfo_memHandle',
    'union_hipArrayMapInfo_resource',
    'union_hipArrayMapInfo_subresource',
    'union_hipExternalMemoryHandleDesc_st_handle',
    'union_hipExternalSemaphoreHandleDesc_st_handle',
    'union_hipKernelNodeAttrValue', 'union_hipPointerAttribute_t_0',
    'union_hipResourceDesc_res']
