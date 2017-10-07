from ctypes import *

dll = CDLL('DLL\QuickLink2.dll')


def get_version():
    buffer_size = 32
    func = dll.QLAPI_GetVersion
    func.argtypes = [c_int, c_char_p]
    output = create_string_buffer(buffer_size)
    func(c_int(buffer_size), output)
    return output.value.decode('UTF-8')
