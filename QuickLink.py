from ctypes import *

dll = CDLL('DLL\QuickLink2.dll')

error_list = ['OK', 'Invalid Device ID', 'Invalid Settings ID', 'Invalid Calibration ID', 'Invalid Target ID',
              'Invalid Password', 'Invalid Path', 'Invalid Duration', 'Invalid Pointer', 'Timeout Elapsed',
              'Internal Error', 'Buffer Too Small', 'Calibration Not Initialized', 'Device Not Started',
              'Device Not Supported', 'Settings Not Found', 'UNAUTHORIZED', 'Invalid Group']


def __display_error(code):
    if code is not 0:
        print(error_list[code])


def get_version():
    func = dll.QLAPI_GetVersion
    buffer_size = 32
    func.argtypes = [c_int, c_char_p]
    output = create_string_buffer(buffer_size)
    __display_error(func(c_int(buffer_size), output))
    return output.value.decode('UTF-8')


def device_enumerate():
    func = dll.QLDevice_Enumerate
    buffer_size = 5
    num_devices = c_int(buffer_size)
    num_devices_pointer = pointer(num_devices)
    device_buffer = (c_int * buffer_size)()
    device_buffer_pointer = pointer(device_buffer)
    func(num_devices_pointer, device_buffer_pointer)
    number = num_devices.value
    device_list = []
    for i in range(0, number):
        device_list.append(device_buffer[i])
    return device_list


def get_status(identifier):
    func = dll.QLDevice_GetStatus
    device_id = c_int(identifier)
    device_status = c_int()
    device_status_pointer = pointer(device_status)
    __display_error(func(device_id, device_status_pointer))
    return device_status.value


def start(identifier):
    func = dll.QLDevice_Start
    device_id = c_int(identifier)
    __display_error(func(device_id))


def stop_all():
    func = dll.QLDevice_Stop_All
    __display_error(func())


class QLXYPairFloat(Structure):
    _fields_ = [
        ("x", c_float),
        ("y", c_float)
    ]


class QLEyeData(Structure):
    _fields_ = [
        ("Found", c_bool),
        ("Calibrated", c_bool),
        ("PupilDiameter", c_float),
        ("Pupil", QLXYPairFloat),
        ("Glint0", QLXYPairFloat),
        ("Glint1", QLXYPairFloat),
        ("GazePoint", QLXYPairFloat)
        # Reserved 16 possibly needed here
    ]


class QLWeightedGazePoint(Structure):
    _fields_ = [
        ("Valid", c_bool),
        ("x", c_float),
        ("y", c_float),
        ("LeftWeight", c_float),
        ("RightWeight", c_float)
        # Reserved 16 possibly needed here
    ]


class QLRectInt(Structure):
    _fields_ = [
        ("x", c_int),
        ("y", c_int),
        ("width", c_int),
        ("height", c_int)
    ]


class QLImageData(Structure):
    _fields_ = [
        ("PixelData", c_char_p),
        ("Width", c_int),
        ("Height", c_int),
        ("Timestamp", c_double),
        ("Gain", c_int),
        ("FrameNumber", c_long),
        ("ROI", QLRectInt),
        ("ScaleFactor", c_float)
    ]


class FrameData(Structure):
    _fields_ = [
        ("ImageData", QLImageData),
        ("LeftEye", QLEyeData),
        ("RightEye", QLEyeData),
        ("WeightedGazePoint", QLWeightedGazePoint),
        ("Focus", c_float),
        ("Distance", c_float),
        ("Bandwidth", c_int),
        ("DeviceID", c_int),
        # Will likely need a 15 long void* here called "Reserved"
    ]


def get_frame(identifier):
    func = dll.QLDevice_GetFrame
    device_or_group = c_int(identifier)
    frame = FrameData()
    __display_error(func(device_or_group, c_int(1000), byref(frame)))
    print("Device ID is " + str(frame.DeviceID))
