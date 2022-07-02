"""
A tool to read and write binary files conveniently.
"""

import struct
from typing import Any, List, Optional, Tuple, Union, Literal


def float_from_bytes(
    data: bytes,
    byteorder: Literal['big', 'little'] = 'little',
    double: bool = False
) -> float:
    """
    Convert bytes to a float.
    """
    return struct.unpack(
        ("<" if byteorder == 'little' else ">" if byteorder == 'big' else "") +
        ("d" if double else "f"),
        data
    )[0]


def float_to_bytes(
    value: float,
    byteorder: Literal['big', 'little'] = 'little',
    double: bool = False
) -> bytes:
    """
    Convert a float to bytes.
    """
    return struct.pack(
        ("<" if byteorder == 'little' else ">" if byteorder == 'big' else "") +
        ("d" if double else "f"),
        value
    )

class Parser:
    """
    A class to parse binary files.
    """

    def __init__(self, file_name):
        """
        Initialize the Parser object.

        :param file_name: The name of the file to open.
        """
        self.file_name = file_name
        self.file = open(file_name, "rb")
        self.file_size = self.file.seek(0, 2)
        self.file.seek(0)

    def __del__(self):
        """
        Close the file.
        """
        self.close()

    def __enter__(self):
        """
        Enter the context manager.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager.
        """
        self.close()

    def read(self, size: Optional[int] = 1) -> bytes:
        """
        Read a certain amount of bytes from the file.
        """
        return self.file.read(size)

    def read_all(self) -> bytes:
        """
        Read all the data from the file. This is equivalent to calling `read(None)`.
        """
        return self.read(None)

    def read_int(self, size: int = 1, signed: bool = False, endian: str = "little") -> int:
        """
        Read an integer from the file.

        :param size: The size of the integer.
        :param signed: Whether the integer is signed.
        :param endian: The byteorder of the integer.

        :return: The integer.
        """
        if endian not in ["little", "big"]:
            raise ValueError("Invalid byteorder.")
        return int.from_bytes(self.read(size), byteorder=endian, signed=signed)  # type: ignore

    def read_float(self, double: bool = True, endian: str = "little") -> float:
        """
        Read a float from the file.

        :param endian: The byteorder of the float.

        :return: The float.
        """
        return float_from_bytes(self.read(4), endian, double=double)  # type: ignore

    def read_str(self, size: int = 1, encoding: str = "utf-8") -> str:
        """
        Read a string from the file.

        :param size: The size of the string.
        :param encoding: The encoding of the string.

        :return: The string.
        """
        return self.read(size).decode(encoding)

    def read_until(self, data: bytes) -> bytes:
        """
        Read until the data is found.

        :param data: The data to read until.

        :return: The data read.
        """
        src = self.read(len(data))
        while data not in src:
            src += self.read(1)
        return src

    def read_fmt(self, fmt: str, endian: str = "little") -> Tuple[Any, ...]:
        """
        Read data from the file according to a format string.

        :param fmt: The format string.

        :return: The data read.

        The format string is under the following format:
        * `b`: A single byte. Append a number to specify the size.
        * `i`: A signed integer. Append a number to specify the size.
        * `u`: An unsigned integer. Append a number to specify the size.
        * `f`: A float. Append a number to specify the size.
        * `s`: A string. Append a number to specify the size.

        - use spaces to separate the arguments.

        Example: `head, ver = read_fmt("b4 i4")`
        """
        data: List[Any] = []
        for arg in fmt.split():
            if arg[0] == "b":
                data.append(self.read(int(arg[1:]) if len(arg) > 1 else 1))
            elif arg[0] == "i":
                data.append(self.read_int(int(arg[1:]) if len(arg) > 1 else 1, signed=True, endian=endian))
            elif arg[0] == "u":
                data.append(self.read_int(int(arg[1:]) if len(arg) > 1 else 1, signed=False, endian=endian))
            elif arg[0] == "f":
                data.append(self.read_float(False, endian))
            elif arg[0] == "d":
                data.append(self.read_float(True, endian))
            elif arg[0] == "s":
                data.append(self.read_str(int(arg[1:]) if len(arg) > 1 else 1))
            else:
                raise ValueError("Invalid format string.")
        return tuple(data)

    def seek(self, offset: int, whence: int = 0):
        """
        Seek to a certain position in the file.

        :param offset: The offset to seek to.
        :param whence: The position to seek from.
        """
        return self.file.seek(offset, whence)

    def tell(self):
        """
        Return the current position in the file.
        """
        return self.file.tell()

    def close(self):
        """
        Close the file.
        """
        self.file.close()


class Builder:
    """
    A class to build binary files.
    """

    def __init__(self, file_name):
        """
        Initialize the Builder object.

        :param file_name: The name of the file to build.
        """
        self.file_name = file_name
        self.file = open(file_name, "wb")

    def __del__(self):
        """
        Close the file.
        """
        self.close()

    def __enter__(self):
        """
        Enter the context manager.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager.
        """
        self.close()

    def write(self, data: Union[bytes, bytearray]) -> "Builder":
        """
        Write data to the file.
        """
        self.file.write(data)
        return self

    def write_int(self, data: int, size: int = 1, signed: bool = False, endian: str = "little") -> "Builder":
        """
        Write an integer to the file.

        :param data: The integer.
        :param size: The size of the integer.
        :param signed: Whether the integer is signed.
        :param endian: The byteorder of the integer.
        """
        if endian not in ["little", "big"]:
            raise ValueError("Invalid byteorder.")
        self.write(data.to_bytes(size, byteorder=endian, signed=signed))  # type: ignore
        return self

    def write_float(self, data: float, endian: str = "little") -> "Builder":
        """
        Write a float to the file.

        :param data: The float.
        :param endian: The byteorder of the float.
        """
        self.write(float_to_bytes(data, endian))  # type: ignore
        return self

    def write_str(self, data: str, encoding: str = "utf-8") -> "Builder":
        """
        Write a string to the file.

        :param data: The string.
        :param encoding: The encoding of the string.
        """
        self.write(data.encode(encoding))
        return self

    def seek(self, offset: int, whence: int = 0):
        """
        Seek to a certain position in the file.

        :param offset: The offset to seek to.
        :param whence: The position to seek from.
        """
        return self.file.seek(offset, whence)

    def tell(self):
        """
        Return the current position in the file.
        """
        return self.file.tell()

    def close(self):
        """
        Close the file.
        """
        self.file.close()