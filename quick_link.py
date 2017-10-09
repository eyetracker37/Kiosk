from ctypes import *
from logger import log

dll = CDLL('DLL\QuickLink2.dll')

error_list = ['OK', 'Invalid Device ID', 'Invalid Settings ID', 'Invalid Calibration ID', 'Invalid Target ID',
              'Invalid Password', 'Invalid Path', 'Invalid Duration', 'Invalid Pointer', 'Timeout Elapsed',
              'Internal Error', 'Buffer Too Small', 'Calibration Not Initialized', 'Device Not Started',
              'Device Not Supported', 'Settings Not Found', 'UNAUTHORIZED', 'Invalid Group']

connected_device = 0  # This is set on initialization


def __display_error(code):
    if code is not 0:
        log(error_list[code], 0)


def get_version():
    func = dll.QLAPI_GetVersion
    buffer_size = 32
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


def initialize():
    device_list = device_enumerate()

    if len(device_list) is 0:
        log("No devices found", 0)
        return 0
    elif len(device_list) > 1:
        log("More than 1 device found", 1)

    global connected_device
    connected_device = device_list[0]

    for device in device_list:
        if get_status(device) is 1:
            log("Starting device " + str(device), 2)
            start(device)
            log(("Waiting for device " + str(device) + " to start"), 3)
            while get_status(device) is not 3:
                pass
        log(("Device " + str(device) + " started"), 3)


def stop_all():
    log("Stopping all devices", 3)
    func = dll.QLDevice_Stop_All
    __display_error(func())
    log("All devices stopped", 2)


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
        ("GazePoint", QLXYPairFloat),
        ("Reserved", (c_voidp * 16))
    ]


class QLWeightedGazePoint(Structure):
    _fields_ = [
        ("Valid", c_bool),
        ("x", c_float),
        ("y", c_float),
        ("LeftWeight", c_float),
        ("RightWeight", c_float),
        ("Reserved", (c_voidp * 16))
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
        ("ScaleFactor", c_float),
        ("Reserved", (c_voidp * 13))
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
        ("Reserved", (c_voidp * 15))
    ]


class FrameObject:
    def __init__(self, frame_struct):
        self.x_pos = frame_struct.WeightedGazePoint.x
        self.y_pos = frame_struct.WeightedGazePoint.y
        self.is_valid = frame_struct.WeightedGazePoint.Valid


def get_frame():
    if connected_device is 0:
        log("Attempted to get data from unconnected device", 0)
        return None

    func = dll.QLDevice_GetFrame
    device_or_group = c_int(connected_device)
    frame_struct = FrameData()
    __display_error(func(device_or_group, c_int(1000), byref(frame_struct)))
    return FrameObject(frame_struct)
