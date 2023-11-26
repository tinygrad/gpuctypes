# -*- coding: utf-8 -*-
#
# TARGET arch is: []
# WORD_SIZE is: 8
# POINTER_SIZE is: 8
# LONGDOUBLE_SIZE is: 16
#
import ctypes


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



_libraries = {}
_libraries['libOpenCL.so'] = ctypes.CDLL('/usr/lib/x86_64-linux-gnu/libOpenCL.so')
c_int128 = ctypes.c_ubyte*16
c_uint128 = c_int128
void = None
if ctypes.sizeof(ctypes.c_longdouble) == 16:
    c_long_double_t = ctypes.c_longdouble
else:
    c_long_double_t = ctypes.c_ubyte*16

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





class struct__cl_platform_id(Structure):
    pass

cl_platform_id = ctypes.POINTER(struct__cl_platform_id)
class struct__cl_device_id(Structure):
    pass

cl_device_id = ctypes.POINTER(struct__cl_device_id)
class struct__cl_context(Structure):
    pass

cl_context = ctypes.POINTER(struct__cl_context)
class struct__cl_command_queue(Structure):
    pass

cl_command_queue = ctypes.POINTER(struct__cl_command_queue)
class struct__cl_mem(Structure):
    pass

cl_mem = ctypes.POINTER(struct__cl_mem)
class struct__cl_program(Structure):
    pass

cl_program = ctypes.POINTER(struct__cl_program)
class struct__cl_kernel(Structure):
    pass

cl_kernel = ctypes.POINTER(struct__cl_kernel)
class struct__cl_event(Structure):
    pass

cl_event = ctypes.POINTER(struct__cl_event)
class struct__cl_sampler(Structure):
    pass

cl_sampler = ctypes.POINTER(struct__cl_sampler)
cl_bool = ctypes.c_uint32
cl_bitfield = ctypes.c_uint64
cl_properties = ctypes.c_uint64
cl_device_type = ctypes.c_uint64
cl_platform_info = ctypes.c_uint32
cl_device_info = ctypes.c_uint32
cl_device_fp_config = ctypes.c_uint64
cl_device_mem_cache_type = ctypes.c_uint32
cl_device_local_mem_type = ctypes.c_uint32
cl_device_exec_capabilities = ctypes.c_uint64
cl_device_svm_capabilities = ctypes.c_uint64
cl_command_queue_properties = ctypes.c_uint64
cl_device_partition_property = ctypes.c_int64
cl_device_affinity_domain = ctypes.c_uint64
cl_context_properties = ctypes.c_int64
cl_context_info = ctypes.c_uint32
cl_queue_properties = ctypes.c_uint64
cl_command_queue_info = ctypes.c_uint32
cl_channel_order = ctypes.c_uint32
cl_channel_type = ctypes.c_uint32
cl_mem_flags = ctypes.c_uint64
cl_svm_mem_flags = ctypes.c_uint64
cl_mem_object_type = ctypes.c_uint32
cl_mem_info = ctypes.c_uint32
cl_mem_migration_flags = ctypes.c_uint64
cl_image_info = ctypes.c_uint32
cl_buffer_create_type = ctypes.c_uint32
cl_addressing_mode = ctypes.c_uint32
cl_filter_mode = ctypes.c_uint32
cl_sampler_info = ctypes.c_uint32
cl_map_flags = ctypes.c_uint64
cl_pipe_properties = ctypes.c_int64
cl_pipe_info = ctypes.c_uint32
cl_program_info = ctypes.c_uint32
cl_program_build_info = ctypes.c_uint32
cl_program_binary_type = ctypes.c_uint32
cl_build_status = ctypes.c_int32
cl_kernel_info = ctypes.c_uint32
cl_kernel_arg_info = ctypes.c_uint32
cl_kernel_arg_address_qualifier = ctypes.c_uint32
cl_kernel_arg_access_qualifier = ctypes.c_uint32
cl_kernel_arg_type_qualifier = ctypes.c_uint64
cl_kernel_work_group_info = ctypes.c_uint32
cl_kernel_sub_group_info = ctypes.c_uint32
cl_event_info = ctypes.c_uint32
cl_command_type = ctypes.c_uint32
cl_profiling_info = ctypes.c_uint32
cl_sampler_properties = ctypes.c_uint64
cl_kernel_exec_info = ctypes.c_uint32
cl_device_atomic_capabilities = ctypes.c_uint64
cl_device_device_enqueue_capabilities = ctypes.c_uint64
cl_khronos_vendor_id = ctypes.c_uint32
cl_mem_properties = ctypes.c_uint64
cl_version = ctypes.c_uint32
class struct__cl_image_format(Structure):
    pass

struct__cl_image_format._pack_ = 1 # source:False
struct__cl_image_format._fields_ = [
    ('image_channel_order', ctypes.c_uint32),
    ('image_channel_data_type', ctypes.c_uint32),
]

cl_image_format = struct__cl_image_format
class struct__cl_image_desc(Structure):
    pass

class union__cl_image_desc_0(Union):
    pass

union__cl_image_desc_0._pack_ = 1 # source:False
union__cl_image_desc_0._fields_ = [
    ('buffer', ctypes.POINTER(struct__cl_mem)),
    ('mem_object', ctypes.POINTER(struct__cl_mem)),
]

struct__cl_image_desc._pack_ = 1 # source:False
struct__cl_image_desc._anonymous_ = ('_0',)
struct__cl_image_desc._fields_ = [
    ('image_type', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('image_width', ctypes.c_uint64),
    ('image_height', ctypes.c_uint64),
    ('image_depth', ctypes.c_uint64),
    ('image_array_size', ctypes.c_uint64),
    ('image_row_pitch', ctypes.c_uint64),
    ('image_slice_pitch', ctypes.c_uint64),
    ('num_mip_levels', ctypes.c_uint32),
    ('num_samples', ctypes.c_uint32),
    ('_0', union__cl_image_desc_0),
]

cl_image_desc = struct__cl_image_desc
class struct__cl_buffer_region(Structure):
    pass

struct__cl_buffer_region._pack_ = 1 # source:False
struct__cl_buffer_region._fields_ = [
    ('origin', ctypes.c_uint64),
    ('size', ctypes.c_uint64),
]

cl_buffer_region = struct__cl_buffer_region
class struct__cl_name_version(Structure):
    pass

struct__cl_name_version._pack_ = 1 # source:False
struct__cl_name_version._fields_ = [
    ('version', ctypes.c_uint32),
    ('name', ctypes.c_char * 64),
]

cl_name_version = struct__cl_name_version
cl_int = ctypes.c_int32
cl_uint = ctypes.c_uint32
clGetPlatformIDs = _libraries['libOpenCL.so'].clGetPlatformIDs
clGetPlatformIDs.restype = cl_int
clGetPlatformIDs.argtypes = [cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_platform_id)), ctypes.POINTER(ctypes.c_uint32)]
size_t = ctypes.c_uint64
clGetPlatformInfo = _libraries['libOpenCL.so'].clGetPlatformInfo
clGetPlatformInfo.restype = cl_int
clGetPlatformInfo.argtypes = [cl_platform_id, cl_platform_info, size_t, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
clGetDeviceIDs = _libraries['libOpenCL.so'].clGetDeviceIDs
clGetDeviceIDs.restype = cl_int
clGetDeviceIDs.argtypes = [cl_platform_id, cl_device_type, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_device_id)), ctypes.POINTER(ctypes.c_uint32)]
clGetDeviceInfo = _libraries['libOpenCL.so'].clGetDeviceInfo
clGetDeviceInfo.restype = cl_int
clGetDeviceInfo.argtypes = [cl_device_id, cl_device_info, size_t, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
clCreateSubDevices = _libraries['libOpenCL.so'].clCreateSubDevices
clCreateSubDevices.restype = cl_int
clCreateSubDevices.argtypes = [cl_device_id, ctypes.POINTER(ctypes.c_int64), cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_device_id)), ctypes.POINTER(ctypes.c_uint32)]
clRetainDevice = _libraries['libOpenCL.so'].clRetainDevice
clRetainDevice.restype = cl_int
clRetainDevice.argtypes = [cl_device_id]
clReleaseDevice = _libraries['libOpenCL.so'].clReleaseDevice
clReleaseDevice.restype = cl_int
clReleaseDevice.argtypes = [cl_device_id]
clSetDefaultDeviceCommandQueue = _libraries['libOpenCL.so'].clSetDefaultDeviceCommandQueue
clSetDefaultDeviceCommandQueue.restype = cl_int
clSetDefaultDeviceCommandQueue.argtypes = [cl_context, cl_device_id, cl_command_queue]
clGetDeviceAndHostTimer = _libraries['libOpenCL.so'].clGetDeviceAndHostTimer
clGetDeviceAndHostTimer.restype = cl_int
clGetDeviceAndHostTimer.argtypes = [cl_device_id, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64)]
clGetHostTimer = _libraries['libOpenCL.so'].clGetHostTimer
clGetHostTimer.restype = cl_int
clGetHostTimer.argtypes = [cl_device_id, ctypes.POINTER(ctypes.c_uint64)]
clCreateContext = _libraries['libOpenCL.so'].clCreateContext
clCreateContext.restype = cl_context
clCreateContext.argtypes = [ctypes.POINTER(ctypes.c_int64), cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_device_id)), ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_char), ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(None)), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_int32)]
clCreateContextFromType = _libraries['libOpenCL.so'].clCreateContextFromType
clCreateContextFromType.restype = cl_context
clCreateContextFromType.argtypes = [ctypes.POINTER(ctypes.c_int64), cl_device_type, ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_char), ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(None)), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_int32)]
clRetainContext = _libraries['libOpenCL.so'].clRetainContext
clRetainContext.restype = cl_int
clRetainContext.argtypes = [cl_context]
clReleaseContext = _libraries['libOpenCL.so'].clReleaseContext
clReleaseContext.restype = cl_int
clReleaseContext.argtypes = [cl_context]
clGetContextInfo = _libraries['libOpenCL.so'].clGetContextInfo
clGetContextInfo.restype = cl_int
clGetContextInfo.argtypes = [cl_context, cl_context_info, size_t, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
clSetContextDestructorCallback = _libraries['libOpenCL.so'].clSetContextDestructorCallback
clSetContextDestructorCallback.restype = cl_int
clSetContextDestructorCallback.argtypes = [cl_context, ctypes.CFUNCTYPE(None, ctypes.POINTER(struct__cl_context), ctypes.POINTER(None)), ctypes.POINTER(None)]
clCreateCommandQueueWithProperties = _libraries['libOpenCL.so'].clCreateCommandQueueWithProperties
clCreateCommandQueueWithProperties.restype = cl_command_queue
clCreateCommandQueueWithProperties.argtypes = [cl_context, cl_device_id, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_int32)]
clRetainCommandQueue = _libraries['libOpenCL.so'].clRetainCommandQueue
clRetainCommandQueue.restype = cl_int
clRetainCommandQueue.argtypes = [cl_command_queue]
clReleaseCommandQueue = _libraries['libOpenCL.so'].clReleaseCommandQueue
clReleaseCommandQueue.restype = cl_int
clReleaseCommandQueue.argtypes = [cl_command_queue]
clGetCommandQueueInfo = _libraries['libOpenCL.so'].clGetCommandQueueInfo
clGetCommandQueueInfo.restype = cl_int
clGetCommandQueueInfo.argtypes = [cl_command_queue, cl_command_queue_info, size_t, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
clCreateBuffer = _libraries['libOpenCL.so'].clCreateBuffer
clCreateBuffer.restype = cl_mem
clCreateBuffer.argtypes = [cl_context, cl_mem_flags, size_t, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_int32)]
clCreateSubBuffer = _libraries['libOpenCL.so'].clCreateSubBuffer
clCreateSubBuffer.restype = cl_mem
clCreateSubBuffer.argtypes = [cl_mem, cl_mem_flags, cl_buffer_create_type, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_int32)]
clCreateImage = _libraries['libOpenCL.so'].clCreateImage
clCreateImage.restype = cl_mem
clCreateImage.argtypes = [cl_context, cl_mem_flags, ctypes.POINTER(struct__cl_image_format), ctypes.POINTER(struct__cl_image_desc), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_int32)]
clCreatePipe = _libraries['libOpenCL.so'].clCreatePipe
clCreatePipe.restype = cl_mem
clCreatePipe.argtypes = [cl_context, cl_mem_flags, cl_uint, cl_uint, ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_int32)]
clCreateBufferWithProperties = _libraries['libOpenCL.so'].clCreateBufferWithProperties
clCreateBufferWithProperties.restype = cl_mem
clCreateBufferWithProperties.argtypes = [cl_context, ctypes.POINTER(ctypes.c_uint64), cl_mem_flags, size_t, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_int32)]
clCreateImageWithProperties = _libraries['libOpenCL.so'].clCreateImageWithProperties
clCreateImageWithProperties.restype = cl_mem
clCreateImageWithProperties.argtypes = [cl_context, ctypes.POINTER(ctypes.c_uint64), cl_mem_flags, ctypes.POINTER(struct__cl_image_format), ctypes.POINTER(struct__cl_image_desc), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_int32)]
clRetainMemObject = _libraries['libOpenCL.so'].clRetainMemObject
clRetainMemObject.restype = cl_int
clRetainMemObject.argtypes = [cl_mem]
clReleaseMemObject = _libraries['libOpenCL.so'].clReleaseMemObject
clReleaseMemObject.restype = cl_int
clReleaseMemObject.argtypes = [cl_mem]
clGetSupportedImageFormats = _libraries['libOpenCL.so'].clGetSupportedImageFormats
clGetSupportedImageFormats.restype = cl_int
clGetSupportedImageFormats.argtypes = [cl_context, cl_mem_flags, cl_mem_object_type, cl_uint, ctypes.POINTER(struct__cl_image_format), ctypes.POINTER(ctypes.c_uint32)]
clGetMemObjectInfo = _libraries['libOpenCL.so'].clGetMemObjectInfo
clGetMemObjectInfo.restype = cl_int
clGetMemObjectInfo.argtypes = [cl_mem, cl_mem_info, size_t, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
clGetImageInfo = _libraries['libOpenCL.so'].clGetImageInfo
clGetImageInfo.restype = cl_int
clGetImageInfo.argtypes = [cl_mem, cl_image_info, size_t, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
clGetPipeInfo = _libraries['libOpenCL.so'].clGetPipeInfo
clGetPipeInfo.restype = cl_int
clGetPipeInfo.argtypes = [cl_mem, cl_pipe_info, size_t, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
clSetMemObjectDestructorCallback = _libraries['libOpenCL.so'].clSetMemObjectDestructorCallback
clSetMemObjectDestructorCallback.restype = cl_int
clSetMemObjectDestructorCallback.argtypes = [cl_mem, ctypes.CFUNCTYPE(None, ctypes.POINTER(struct__cl_mem), ctypes.POINTER(None)), ctypes.POINTER(None)]
clSVMAlloc = _libraries['libOpenCL.so'].clSVMAlloc
clSVMAlloc.restype = ctypes.POINTER(None)
clSVMAlloc.argtypes = [cl_context, cl_svm_mem_flags, size_t, cl_uint]
clSVMFree = _libraries['libOpenCL.so'].clSVMFree
clSVMFree.restype = None
clSVMFree.argtypes = [cl_context, ctypes.POINTER(None)]
clCreateSamplerWithProperties = _libraries['libOpenCL.so'].clCreateSamplerWithProperties
clCreateSamplerWithProperties.restype = cl_sampler
clCreateSamplerWithProperties.argtypes = [cl_context, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_int32)]
clRetainSampler = _libraries['libOpenCL.so'].clRetainSampler
clRetainSampler.restype = cl_int
clRetainSampler.argtypes = [cl_sampler]
clReleaseSampler = _libraries['libOpenCL.so'].clReleaseSampler
clReleaseSampler.restype = cl_int
clReleaseSampler.argtypes = [cl_sampler]
clGetSamplerInfo = _libraries['libOpenCL.so'].clGetSamplerInfo
clGetSamplerInfo.restype = cl_int
clGetSamplerInfo.argtypes = [cl_sampler, cl_sampler_info, size_t, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
clCreateProgramWithSource = _libraries['libOpenCL.so'].clCreateProgramWithSource
clCreateProgramWithSource.restype = cl_program
clCreateProgramWithSource.argtypes = [cl_context, cl_uint, ctypes.POINTER(ctypes.POINTER(ctypes.c_char)), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_int32)]
clCreateProgramWithBinary = _libraries['libOpenCL.so'].clCreateProgramWithBinary
clCreateProgramWithBinary.restype = cl_program
clCreateProgramWithBinary.argtypes = [cl_context, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_device_id)), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte)), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32)]
clCreateProgramWithBuiltInKernels = _libraries['libOpenCL.so'].clCreateProgramWithBuiltInKernels
clCreateProgramWithBuiltInKernels.restype = cl_program
clCreateProgramWithBuiltInKernels.argtypes = [cl_context, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_device_id)), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_int32)]
clCreateProgramWithIL = _libraries['libOpenCL.so'].clCreateProgramWithIL
clCreateProgramWithIL.restype = cl_program
clCreateProgramWithIL.argtypes = [cl_context, ctypes.POINTER(None), size_t, ctypes.POINTER(ctypes.c_int32)]
clRetainProgram = _libraries['libOpenCL.so'].clRetainProgram
clRetainProgram.restype = cl_int
clRetainProgram.argtypes = [cl_program]
clReleaseProgram = _libraries['libOpenCL.so'].clReleaseProgram
clReleaseProgram.restype = cl_int
clReleaseProgram.argtypes = [cl_program]
clBuildProgram = _libraries['libOpenCL.so'].clBuildProgram
clBuildProgram.restype = cl_int
clBuildProgram.argtypes = [cl_program, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_device_id)), ctypes.POINTER(ctypes.c_char), ctypes.CFUNCTYPE(None, ctypes.POINTER(struct__cl_program), ctypes.POINTER(None)), ctypes.POINTER(None)]
clCompileProgram = _libraries['libOpenCL.so'].clCompileProgram
clCompileProgram.restype = cl_int
clCompileProgram.argtypes = [cl_program, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_device_id)), ctypes.POINTER(ctypes.c_char), cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_program)), ctypes.POINTER(ctypes.POINTER(ctypes.c_char)), ctypes.CFUNCTYPE(None, ctypes.POINTER(struct__cl_program), ctypes.POINTER(None)), ctypes.POINTER(None)]
clLinkProgram = _libraries['libOpenCL.so'].clLinkProgram
clLinkProgram.restype = cl_program
clLinkProgram.argtypes = [cl_context, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_device_id)), ctypes.POINTER(ctypes.c_char), cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_program)), ctypes.CFUNCTYPE(None, ctypes.POINTER(struct__cl_program), ctypes.POINTER(None)), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_int32)]
clSetProgramReleaseCallback = _libraries['libOpenCL.so'].clSetProgramReleaseCallback
clSetProgramReleaseCallback.restype = cl_int
clSetProgramReleaseCallback.argtypes = [cl_program, ctypes.CFUNCTYPE(None, ctypes.POINTER(struct__cl_program), ctypes.POINTER(None)), ctypes.POINTER(None)]
clSetProgramSpecializationConstant = _libraries['libOpenCL.so'].clSetProgramSpecializationConstant
clSetProgramSpecializationConstant.restype = cl_int
clSetProgramSpecializationConstant.argtypes = [cl_program, cl_uint, size_t, ctypes.POINTER(None)]
clUnloadPlatformCompiler = _libraries['libOpenCL.so'].clUnloadPlatformCompiler
clUnloadPlatformCompiler.restype = cl_int
clUnloadPlatformCompiler.argtypes = [cl_platform_id]
clGetProgramInfo = _libraries['libOpenCL.so'].clGetProgramInfo
clGetProgramInfo.restype = cl_int
clGetProgramInfo.argtypes = [cl_program, cl_program_info, size_t, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
clGetProgramBuildInfo = _libraries['libOpenCL.so'].clGetProgramBuildInfo
clGetProgramBuildInfo.restype = cl_int
clGetProgramBuildInfo.argtypes = [cl_program, cl_device_id, cl_program_build_info, size_t, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
clCreateKernel = _libraries['libOpenCL.so'].clCreateKernel
clCreateKernel.restype = cl_kernel
clCreateKernel.argtypes = [cl_program, ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_int32)]
clCreateKernelsInProgram = _libraries['libOpenCL.so'].clCreateKernelsInProgram
clCreateKernelsInProgram.restype = cl_int
clCreateKernelsInProgram.argtypes = [cl_program, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_kernel)), ctypes.POINTER(ctypes.c_uint32)]
clCloneKernel = _libraries['libOpenCL.so'].clCloneKernel
clCloneKernel.restype = cl_kernel
clCloneKernel.argtypes = [cl_kernel, ctypes.POINTER(ctypes.c_int32)]
clRetainKernel = _libraries['libOpenCL.so'].clRetainKernel
clRetainKernel.restype = cl_int
clRetainKernel.argtypes = [cl_kernel]
clReleaseKernel = _libraries['libOpenCL.so'].clReleaseKernel
clReleaseKernel.restype = cl_int
clReleaseKernel.argtypes = [cl_kernel]
clSetKernelArg = _libraries['libOpenCL.so'].clSetKernelArg
clSetKernelArg.restype = cl_int
clSetKernelArg.argtypes = [cl_kernel, cl_uint, size_t, ctypes.POINTER(None)]
clSetKernelArgSVMPointer = _libraries['libOpenCL.so'].clSetKernelArgSVMPointer
clSetKernelArgSVMPointer.restype = cl_int
clSetKernelArgSVMPointer.argtypes = [cl_kernel, cl_uint, ctypes.POINTER(None)]
clSetKernelExecInfo = _libraries['libOpenCL.so'].clSetKernelExecInfo
clSetKernelExecInfo.restype = cl_int
clSetKernelExecInfo.argtypes = [cl_kernel, cl_kernel_exec_info, size_t, ctypes.POINTER(None)]
clGetKernelInfo = _libraries['libOpenCL.so'].clGetKernelInfo
clGetKernelInfo.restype = cl_int
clGetKernelInfo.argtypes = [cl_kernel, cl_kernel_info, size_t, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
clGetKernelArgInfo = _libraries['libOpenCL.so'].clGetKernelArgInfo
clGetKernelArgInfo.restype = cl_int
clGetKernelArgInfo.argtypes = [cl_kernel, cl_uint, cl_kernel_arg_info, size_t, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
clGetKernelWorkGroupInfo = _libraries['libOpenCL.so'].clGetKernelWorkGroupInfo
clGetKernelWorkGroupInfo.restype = cl_int
clGetKernelWorkGroupInfo.argtypes = [cl_kernel, cl_device_id, cl_kernel_work_group_info, size_t, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
clGetKernelSubGroupInfo = _libraries['libOpenCL.so'].clGetKernelSubGroupInfo
clGetKernelSubGroupInfo.restype = cl_int
clGetKernelSubGroupInfo.argtypes = [cl_kernel, cl_device_id, cl_kernel_sub_group_info, size_t, ctypes.POINTER(None), size_t, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
clWaitForEvents = _libraries['libOpenCL.so'].clWaitForEvents
clWaitForEvents.restype = cl_int
clWaitForEvents.argtypes = [cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clGetEventInfo = _libraries['libOpenCL.so'].clGetEventInfo
clGetEventInfo.restype = cl_int
clGetEventInfo.argtypes = [cl_event, cl_event_info, size_t, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
clCreateUserEvent = _libraries['libOpenCL.so'].clCreateUserEvent
clCreateUserEvent.restype = cl_event
clCreateUserEvent.argtypes = [cl_context, ctypes.POINTER(ctypes.c_int32)]
clRetainEvent = _libraries['libOpenCL.so'].clRetainEvent
clRetainEvent.restype = cl_int
clRetainEvent.argtypes = [cl_event]
clReleaseEvent = _libraries['libOpenCL.so'].clReleaseEvent
clReleaseEvent.restype = cl_int
clReleaseEvent.argtypes = [cl_event]
clSetUserEventStatus = _libraries['libOpenCL.so'].clSetUserEventStatus
clSetUserEventStatus.restype = cl_int
clSetUserEventStatus.argtypes = [cl_event, cl_int]
clSetEventCallback = _libraries['libOpenCL.so'].clSetEventCallback
clSetEventCallback.restype = cl_int
clSetEventCallback.argtypes = [cl_event, cl_int, ctypes.CFUNCTYPE(None, ctypes.POINTER(struct__cl_event), ctypes.c_int32, ctypes.POINTER(None)), ctypes.POINTER(None)]
clGetEventProfilingInfo = _libraries['libOpenCL.so'].clGetEventProfilingInfo
clGetEventProfilingInfo.restype = cl_int
clGetEventProfilingInfo.argtypes = [cl_event, cl_profiling_info, size_t, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
clFlush = _libraries['libOpenCL.so'].clFlush
clFlush.restype = cl_int
clFlush.argtypes = [cl_command_queue]
clFinish = _libraries['libOpenCL.so'].clFinish
clFinish.restype = cl_int
clFinish.argtypes = [cl_command_queue]
clEnqueueReadBuffer = _libraries['libOpenCL.so'].clEnqueueReadBuffer
clEnqueueReadBuffer.restype = cl_int
clEnqueueReadBuffer.argtypes = [cl_command_queue, cl_mem, cl_bool, size_t, size_t, ctypes.POINTER(None), cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueReadBufferRect = _libraries['libOpenCL.so'].clEnqueueReadBufferRect
clEnqueueReadBufferRect.restype = cl_int
clEnqueueReadBufferRect.argtypes = [cl_command_queue, cl_mem, cl_bool, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64), size_t, size_t, size_t, size_t, ctypes.POINTER(None), cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueWriteBuffer = _libraries['libOpenCL.so'].clEnqueueWriteBuffer
clEnqueueWriteBuffer.restype = cl_int
clEnqueueWriteBuffer.argtypes = [cl_command_queue, cl_mem, cl_bool, size_t, size_t, ctypes.POINTER(None), cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueWriteBufferRect = _libraries['libOpenCL.so'].clEnqueueWriteBufferRect
clEnqueueWriteBufferRect.restype = cl_int
clEnqueueWriteBufferRect.argtypes = [cl_command_queue, cl_mem, cl_bool, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64), size_t, size_t, size_t, size_t, ctypes.POINTER(None), cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueFillBuffer = _libraries['libOpenCL.so'].clEnqueueFillBuffer
clEnqueueFillBuffer.restype = cl_int
clEnqueueFillBuffer.argtypes = [cl_command_queue, cl_mem, ctypes.POINTER(None), size_t, size_t, size_t, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueCopyBuffer = _libraries['libOpenCL.so'].clEnqueueCopyBuffer
clEnqueueCopyBuffer.restype = cl_int
clEnqueueCopyBuffer.argtypes = [cl_command_queue, cl_mem, cl_mem, size_t, size_t, size_t, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueCopyBufferRect = _libraries['libOpenCL.so'].clEnqueueCopyBufferRect
clEnqueueCopyBufferRect.restype = cl_int
clEnqueueCopyBufferRect.argtypes = [cl_command_queue, cl_mem, cl_mem, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64), size_t, size_t, size_t, size_t, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueReadImage = _libraries['libOpenCL.so'].clEnqueueReadImage
clEnqueueReadImage.restype = cl_int
clEnqueueReadImage.argtypes = [cl_command_queue, cl_mem, cl_bool, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64), size_t, size_t, ctypes.POINTER(None), cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueWriteImage = _libraries['libOpenCL.so'].clEnqueueWriteImage
clEnqueueWriteImage.restype = cl_int
clEnqueueWriteImage.argtypes = [cl_command_queue, cl_mem, cl_bool, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64), size_t, size_t, ctypes.POINTER(None), cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueFillImage = _libraries['libOpenCL.so'].clEnqueueFillImage
clEnqueueFillImage.restype = cl_int
clEnqueueFillImage.argtypes = [cl_command_queue, cl_mem, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64), cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueCopyImage = _libraries['libOpenCL.so'].clEnqueueCopyImage
clEnqueueCopyImage.restype = cl_int
clEnqueueCopyImage.argtypes = [cl_command_queue, cl_mem, cl_mem, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64), cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueCopyImageToBuffer = _libraries['libOpenCL.so'].clEnqueueCopyImageToBuffer
clEnqueueCopyImageToBuffer.restype = cl_int
clEnqueueCopyImageToBuffer.argtypes = [cl_command_queue, cl_mem, cl_mem, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64), size_t, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueCopyBufferToImage = _libraries['libOpenCL.so'].clEnqueueCopyBufferToImage
clEnqueueCopyBufferToImage.restype = cl_int
clEnqueueCopyBufferToImage.argtypes = [cl_command_queue, cl_mem, cl_mem, size_t, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64), cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueMapBuffer = _libraries['libOpenCL.so'].clEnqueueMapBuffer
clEnqueueMapBuffer.restype = ctypes.POINTER(None)
clEnqueueMapBuffer.argtypes = [cl_command_queue, cl_mem, cl_bool, cl_map_flags, size_t, size_t, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.c_int32)]
clEnqueueMapImage = _libraries['libOpenCL.so'].clEnqueueMapImage
clEnqueueMapImage.restype = ctypes.POINTER(None)
clEnqueueMapImage.argtypes = [cl_command_queue, cl_mem, cl_bool, cl_map_flags, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64), cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.c_int32)]
clEnqueueUnmapMemObject = _libraries['libOpenCL.so'].clEnqueueUnmapMemObject
clEnqueueUnmapMemObject.restype = cl_int
clEnqueueUnmapMemObject.argtypes = [cl_command_queue, cl_mem, ctypes.POINTER(None), cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueMigrateMemObjects = _libraries['libOpenCL.so'].clEnqueueMigrateMemObjects
clEnqueueMigrateMemObjects.restype = cl_int
clEnqueueMigrateMemObjects.argtypes = [cl_command_queue, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_mem)), cl_mem_migration_flags, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueNDRangeKernel = _libraries['libOpenCL.so'].clEnqueueNDRangeKernel
clEnqueueNDRangeKernel.restype = cl_int
clEnqueueNDRangeKernel.argtypes = [cl_command_queue, cl_kernel, cl_uint, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64), cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueNativeKernel = _libraries['libOpenCL.so'].clEnqueueNativeKernel
clEnqueueNativeKernel.restype = cl_int
clEnqueueNativeKernel.argtypes = [cl_command_queue, ctypes.CFUNCTYPE(None, ctypes.POINTER(None)), ctypes.POINTER(None), size_t, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_mem)), ctypes.POINTER(ctypes.POINTER(None)), cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueMarkerWithWaitList = _libraries['libOpenCL.so'].clEnqueueMarkerWithWaitList
clEnqueueMarkerWithWaitList.restype = cl_int
clEnqueueMarkerWithWaitList.argtypes = [cl_command_queue, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueBarrierWithWaitList = _libraries['libOpenCL.so'].clEnqueueBarrierWithWaitList
clEnqueueBarrierWithWaitList.restype = cl_int
clEnqueueBarrierWithWaitList.argtypes = [cl_command_queue, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueSVMFree = _libraries['libOpenCL.so'].clEnqueueSVMFree
clEnqueueSVMFree.restype = cl_int
clEnqueueSVMFree.argtypes = [cl_command_queue, cl_uint, ctypes.POINTER(None) * 0, ctypes.CFUNCTYPE(None, ctypes.POINTER(struct__cl_command_queue), ctypes.c_uint32, ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(None)), ctypes.POINTER(None), cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueSVMMemcpy = _libraries['libOpenCL.so'].clEnqueueSVMMemcpy
clEnqueueSVMMemcpy.restype = cl_int
clEnqueueSVMMemcpy.argtypes = [cl_command_queue, cl_bool, ctypes.POINTER(None), ctypes.POINTER(None), size_t, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueSVMMemFill = _libraries['libOpenCL.so'].clEnqueueSVMMemFill
clEnqueueSVMMemFill.restype = cl_int
clEnqueueSVMMemFill.argtypes = [cl_command_queue, ctypes.POINTER(None), ctypes.POINTER(None), size_t, size_t, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueSVMMap = _libraries['libOpenCL.so'].clEnqueueSVMMap
clEnqueueSVMMap.restype = cl_int
clEnqueueSVMMap.argtypes = [cl_command_queue, cl_bool, cl_map_flags, ctypes.POINTER(None), size_t, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueSVMUnmap = _libraries['libOpenCL.so'].clEnqueueSVMUnmap
clEnqueueSVMUnmap.restype = cl_int
clEnqueueSVMUnmap.argtypes = [cl_command_queue, ctypes.POINTER(None), cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueSVMMigrateMem = _libraries['libOpenCL.so'].clEnqueueSVMMigrateMem
clEnqueueSVMMigrateMem.restype = cl_int
clEnqueueSVMMigrateMem.argtypes = [cl_command_queue, cl_uint, ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(ctypes.c_uint64), cl_mem_migration_flags, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clGetExtensionFunctionAddressForPlatform = _libraries['libOpenCL.so'].clGetExtensionFunctionAddressForPlatform
clGetExtensionFunctionAddressForPlatform.restype = ctypes.POINTER(None)
clGetExtensionFunctionAddressForPlatform.argtypes = [cl_platform_id, ctypes.POINTER(ctypes.c_char)]
clCreateImage2D = _libraries['libOpenCL.so'].clCreateImage2D
clCreateImage2D.restype = cl_mem
clCreateImage2D.argtypes = [cl_context, cl_mem_flags, ctypes.POINTER(struct__cl_image_format), size_t, size_t, size_t, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_int32)]
clCreateImage3D = _libraries['libOpenCL.so'].clCreateImage3D
clCreateImage3D.restype = cl_mem
clCreateImage3D.argtypes = [cl_context, cl_mem_flags, ctypes.POINTER(struct__cl_image_format), size_t, size_t, size_t, size_t, size_t, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_int32)]
clEnqueueMarker = _libraries['libOpenCL.so'].clEnqueueMarker
clEnqueueMarker.restype = cl_int
clEnqueueMarker.argtypes = [cl_command_queue, ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueWaitForEvents = _libraries['libOpenCL.so'].clEnqueueWaitForEvents
clEnqueueWaitForEvents.restype = cl_int
clEnqueueWaitForEvents.argtypes = [cl_command_queue, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
clEnqueueBarrier = _libraries['libOpenCL.so'].clEnqueueBarrier
clEnqueueBarrier.restype = cl_int
clEnqueueBarrier.argtypes = [cl_command_queue]
clUnloadCompiler = _libraries['libOpenCL.so'].clUnloadCompiler
clUnloadCompiler.restype = cl_int
clUnloadCompiler.argtypes = []
clGetExtensionFunctionAddress = _libraries['libOpenCL.so'].clGetExtensionFunctionAddress
clGetExtensionFunctionAddress.restype = ctypes.POINTER(None)
clGetExtensionFunctionAddress.argtypes = [ctypes.POINTER(ctypes.c_char)]
clCreateCommandQueue = _libraries['libOpenCL.so'].clCreateCommandQueue
clCreateCommandQueue.restype = cl_command_queue
clCreateCommandQueue.argtypes = [cl_context, cl_device_id, cl_command_queue_properties, ctypes.POINTER(ctypes.c_int32)]
clCreateSampler = _libraries['libOpenCL.so'].clCreateSampler
clCreateSampler.restype = cl_sampler
clCreateSampler.argtypes = [cl_context, cl_bool, cl_addressing_mode, cl_filter_mode, ctypes.POINTER(ctypes.c_int32)]
clEnqueueTask = _libraries['libOpenCL.so'].clEnqueueTask
clEnqueueTask.restype = cl_int
clEnqueueTask.argtypes = [cl_command_queue, cl_kernel, cl_uint, ctypes.POINTER(ctypes.POINTER(struct__cl_event)), ctypes.POINTER(ctypes.POINTER(struct__cl_event))]
__all__ = \
    ['clBuildProgram', 'clCloneKernel', 'clCompileProgram',
    'clCreateBuffer', 'clCreateBufferWithProperties',
    'clCreateCommandQueue', 'clCreateCommandQueueWithProperties',
    'clCreateContext', 'clCreateContextFromType', 'clCreateImage',
    'clCreateImage2D', 'clCreateImage3D',
    'clCreateImageWithProperties', 'clCreateKernel',
    'clCreateKernelsInProgram', 'clCreatePipe',
    'clCreateProgramWithBinary', 'clCreateProgramWithBuiltInKernels',
    'clCreateProgramWithIL', 'clCreateProgramWithSource',
    'clCreateSampler', 'clCreateSamplerWithProperties',
    'clCreateSubBuffer', 'clCreateSubDevices', 'clCreateUserEvent',
    'clEnqueueBarrier', 'clEnqueueBarrierWithWaitList',
    'clEnqueueCopyBuffer', 'clEnqueueCopyBufferRect',
    'clEnqueueCopyBufferToImage', 'clEnqueueCopyImage',
    'clEnqueueCopyImageToBuffer', 'clEnqueueFillBuffer',
    'clEnqueueFillImage', 'clEnqueueMapBuffer', 'clEnqueueMapImage',
    'clEnqueueMarker', 'clEnqueueMarkerWithWaitList',
    'clEnqueueMigrateMemObjects', 'clEnqueueNDRangeKernel',
    'clEnqueueNativeKernel', 'clEnqueueReadBuffer',
    'clEnqueueReadBufferRect', 'clEnqueueReadImage',
    'clEnqueueSVMFree', 'clEnqueueSVMMap', 'clEnqueueSVMMemFill',
    'clEnqueueSVMMemcpy', 'clEnqueueSVMMigrateMem',
    'clEnqueueSVMUnmap', 'clEnqueueTask', 'clEnqueueUnmapMemObject',
    'clEnqueueWaitForEvents', 'clEnqueueWriteBuffer',
    'clEnqueueWriteBufferRect', 'clEnqueueWriteImage', 'clFinish',
    'clFlush', 'clGetCommandQueueInfo', 'clGetContextInfo',
    'clGetDeviceAndHostTimer', 'clGetDeviceIDs', 'clGetDeviceInfo',
    'clGetEventInfo', 'clGetEventProfilingInfo',
    'clGetExtensionFunctionAddress',
    'clGetExtensionFunctionAddressForPlatform', 'clGetHostTimer',
    'clGetImageInfo', 'clGetKernelArgInfo', 'clGetKernelInfo',
    'clGetKernelSubGroupInfo', 'clGetKernelWorkGroupInfo',
    'clGetMemObjectInfo', 'clGetPipeInfo', 'clGetPlatformIDs',
    'clGetPlatformInfo', 'clGetProgramBuildInfo', 'clGetProgramInfo',
    'clGetSamplerInfo', 'clGetSupportedImageFormats', 'clLinkProgram',
    'clReleaseCommandQueue', 'clReleaseContext', 'clReleaseDevice',
    'clReleaseEvent', 'clReleaseKernel', 'clReleaseMemObject',
    'clReleaseProgram', 'clReleaseSampler', 'clRetainCommandQueue',
    'clRetainContext', 'clRetainDevice', 'clRetainEvent',
    'clRetainKernel', 'clRetainMemObject', 'clRetainProgram',
    'clRetainSampler', 'clSVMAlloc', 'clSVMFree',
    'clSetContextDestructorCallback',
    'clSetDefaultDeviceCommandQueue', 'clSetEventCallback',
    'clSetKernelArg', 'clSetKernelArgSVMPointer',
    'clSetKernelExecInfo', 'clSetMemObjectDestructorCallback',
    'clSetProgramReleaseCallback',
    'clSetProgramSpecializationConstant', 'clSetUserEventStatus',
    'clUnloadCompiler', 'clUnloadPlatformCompiler', 'clWaitForEvents',
    'cl_addressing_mode', 'cl_bitfield', 'cl_bool',
    'cl_buffer_create_type', 'cl_buffer_region', 'cl_build_status',
    'cl_channel_order', 'cl_channel_type', 'cl_command_queue',
    'cl_command_queue_info', 'cl_command_queue_properties',
    'cl_command_type', 'cl_context', 'cl_context_info',
    'cl_context_properties', 'cl_device_affinity_domain',
    'cl_device_atomic_capabilities',
    'cl_device_device_enqueue_capabilities',
    'cl_device_exec_capabilities', 'cl_device_fp_config',
    'cl_device_id', 'cl_device_info', 'cl_device_local_mem_type',
    'cl_device_mem_cache_type', 'cl_device_partition_property',
    'cl_device_svm_capabilities', 'cl_device_type', 'cl_event',
    'cl_event_info', 'cl_filter_mode', 'cl_image_desc',
    'cl_image_format', 'cl_image_info', 'cl_int', 'cl_kernel',
    'cl_kernel_arg_access_qualifier',
    'cl_kernel_arg_address_qualifier', 'cl_kernel_arg_info',
    'cl_kernel_arg_type_qualifier', 'cl_kernel_exec_info',
    'cl_kernel_info', 'cl_kernel_sub_group_info',
    'cl_kernel_work_group_info', 'cl_khronos_vendor_id',
    'cl_map_flags', 'cl_mem', 'cl_mem_flags', 'cl_mem_info',
    'cl_mem_migration_flags', 'cl_mem_object_type',
    'cl_mem_properties', 'cl_name_version', 'cl_pipe_info',
    'cl_pipe_properties', 'cl_platform_id', 'cl_platform_info',
    'cl_profiling_info', 'cl_program', 'cl_program_binary_type',
    'cl_program_build_info', 'cl_program_info', 'cl_properties',
    'cl_queue_properties', 'cl_sampler', 'cl_sampler_info',
    'cl_sampler_properties', 'cl_svm_mem_flags', 'cl_uint',
    'cl_version', 'size_t', 'struct__cl_buffer_region',
    'struct__cl_command_queue', 'struct__cl_context',
    'struct__cl_device_id', 'struct__cl_event',
    'struct__cl_image_desc', 'struct__cl_image_format',
    'struct__cl_kernel', 'struct__cl_mem', 'struct__cl_name_version',
    'struct__cl_platform_id', 'struct__cl_program',
    'struct__cl_sampler', 'union__cl_image_desc_0']
