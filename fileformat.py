"""
A tool to read and write binary files conveniently.
"""

from typing import Any, Optional, Union


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

    def read_all(self):
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

    def read_str(self, size: int = 1, encoding: str = "utf-8") -> str:
        """
        Read a string from the file.

        :param size: The size of the string.
        :param encoding: The encoding of the string.

        :return: The string.
        """
        return self.read(size).decode(encoding)

    def read_until(self, data: bytes):
        """
        Read until the data is found.

        :param data: The data to read until.

        :return: The data read.
        """
        src = self.read(len(data))
        while data not in src:
            src += self.read(1)
        return src

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