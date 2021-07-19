from ctypes import cdll
from ctypes import POINTER, byref
from ctypes import c_void_p, c_uint, c_uint16, c_uint8

from enum import IntEnum, auto
from pathlib import Path
from typing import Final, Literal, NewType, Union, overload

from . import ClkPhase, ClkPolarity
from .. import Ft4222Status
from ... import FtHandle

MODULE_PATH: Final[Path] = Path(__file__).parent

try:
    ftlib = cdll.LoadLibrary(
        str(MODULE_PATH / '..' / '..' / 'dlls' / 'libft4222.so.1.4.4.44'))
except OSError as e:
    print("Unable to load shared library!")
    exit(1)

SpiSlaveRawHandle = NewType('SpiSlaveRawHandle', c_void_p)
SpiSlaveProtoHandle = NewType('SpiSlaveProtoHandle', c_void_p)
SpiSlaveHandle = Union[SpiSlaveRawHandle, SpiSlaveProtoHandle]


class IoProtocol(IntEnum):
    WITH_PROTOCOL = 0
    NO_PROTOCOL = auto()
    NO_ACK = auto()


_init = ftlib.FT4222_SPISlave_Init
_init.argtypes = [c_void_p]
_init.restype = Ft4222Status

_init_ex = ftlib.FT4222_SPISlave_InitEx
_init_ex.argtypes = [c_void_p, c_uint]
_init_ex.restype = Ft4222Status

_set_mode = ftlib.FT4222_SPISlave_SetMode
_set_mode.argtypes = [c_void_p, c_uint, c_uint]
_set_mode.restype = Ft4222Status

_get_rx_status = ftlib.FT4222_SPISlave_GetRxStatus
_get_rx_status.argtypes = [c_void_p, POINTER(c_uint16)]
_get_rx_status.restype = Ft4222Status

_read = ftlib.FT4222_SPISlave_Read
_read.argtypes = [c_void_p, POINTER(
    c_uint8), c_uint16, POINTER(c_uint16)]
_read.restype = Ft4222Status

_write = ftlib.FT4222_SPISlave_Write
_write.argtypes = [c_void_p, POINTER(
    c_uint8), c_uint16, POINTER(c_uint16)]
_write.restype = Ft4222Status


def init(ft_handle: FtHandle) -> SpiSlaveProtoHandle:
    """Initialize the FT4222H as an SPI slave.

    Default SPI Slave protocol is 'IoProtocol.WITH_PROTOCOL'.

    Args:
        ft_handle:              Handle to an open FT4222 device

    Raises:
        RuntimeError:           TODO

    Returns:
        SpiSlaveProtoHandle:    Handle to FT4222 device in SPI Slave mode with protocol
    """
    result: Ft4222Status = _init(ft_handle)

    if result != Ft4222Status.OK:
        raise RuntimeError('TODO')

    return SpiSlaveProtoHandle(ft_handle)


@overload
def init_ex(
    ft_handle: FtHandle,
    protocol: Literal[IoProtocol.NO_PROTOCOL]
) -> SpiSlaveRawHandle: ...


@overload
def init_ex(
    ft_handle: FtHandle,
    protocol: Union[Literal[IoProtocol.WITH_PROTOCOL],
                    Literal[IoProtocol.NO_ACK]]
) -> SpiSlaveProtoHandle: ...


def init_ex(ft_handle: FtHandle, protocol: IoProtocol) -> SpiSlaveHandle:
    """Initialize the FT4222H as an SPI slave.

    Similar to 'SPI.Slave.init()' function, but with parameters to define the transmission protocol.

    Args:
        ft_handle:      Handle to an open FT4222 device
        protocol:       Protocol to be used for communication (if any)

    Raises:
        RuntimeError:   TODO

    Returns:
        SpiSlaveHandle: Handle to FT4222 device in selected protocol mode
    """
    result: Ft4222Status = _init_ex(ft_handle, protocol)

    if result != Ft4222Status.OK:
        raise RuntimeError('TODO')

    if protocol == IoProtocol.NO_PROTOCOL:
        return SpiSlaveRawHandle(ft_handle)
    else:
        return SpiSlaveProtoHandle(ft_handle)


def set_mode(
    ft_handle: SpiSlaveHandle,
    clk_polarity: ClkPolarity,
    clk_phase: ClkPhase
) -> None:
    """Set clock polarity and phase.

    Args:
        ft_handle:      Handle to an initialized FT4222 device in SPI Slave mode
        clk_polarity:   Clock polarity (idle low/high)
        clk_phase:      Clock phase

    Raises:
        RuntimeError:   TODO
    """
    result: Ft4222Status = _set_mode(
        ft_handle,
        clk_polarity,
        clk_phase
    )

    if result != Ft4222Status.OK:
        raise RuntimeError('TODO')


def get_rx_status(ft_handle: SpiSlaveHandle) -> int:
    """Get number of bytes in the receive queue.

    Args:
        ft_handle:      Handle to an initialized FT4222 device in SPI Slave mode

    Raises:
        RuntimeError:   TODO

    Return:             Number of bytes in the receive queue
    """
    rx_size = c_uint16()

    result: Ft4222Status = _get_rx_status(
        ft_handle,
        byref(rx_size)
    )

    if result != Ft4222Status.OK:
        raise RuntimeError('TODO')

    return rx_size.value


def read(ft_handle: SpiSlaveHandle, read_byte_count: int) -> bytes:
    """Read data from the receive queue of the SPI slave device.

    Args:
        ft_handle:          Handle to an initialized FT4222 device in SPI Slave mode
        read_byte_count:    Number of bytes to read from Rx queue

    Raises:
        RuntimeError:       TODO

    Returns:
        bytes:              Read data (if any)
    """
    read_buffer = (c_uint8 * read_byte_count)()
    bytes_read = c_uint16()

    result: Ft4222Status = _read(
        ft_handle,
        read_buffer,
        len(read_buffer),
        byref(bytes_read)
    )

    if result != Ft4222Status.OK:
        raise RuntimeError('TODO')

    return bytes(read_buffer[:bytes_read.value])


def write(ft_handle: SpiSlaveHandle, write_data: bytes) -> int:
    """Write data to the transmit queue of the SPI slave device.

    NOTE: For some reasons, support lib will append a dummy byte (0x00) at the first byte automatically.
    This additional byte exists at all of the three transfer methods.

    Args:
        ft_handle:      Handle to an initialized FT4222 device in SPI Slave mode
        write_data:     Data to be written into Tx queue

    Raises:
        RuntimeError:   TODO

    Returns:
        int:            Number of bytes written into Tx queue
    """
    bytes_written = c_uint16()

    result: Ft4222Status = _write(
        ft_handle,
        write_data,
        len(write_data),
        byref(bytes_written)
    )

    if result != Ft4222Status.OK:
        raise RuntimeError('TODO')

    return bytes_written.value
