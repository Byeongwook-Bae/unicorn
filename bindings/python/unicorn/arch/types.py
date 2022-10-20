# Common types and structures.
#
# @author elicn

from abc import abstractmethod
from typing import Generic, Tuple, TypeVar

import ctypes

uc_err	   = ctypes.c_int
uc_engine  = ctypes.c_void_p
uc_context = ctypes.c_void_p
uc_hook_h  = ctypes.c_size_t


VT = TypeVar('VT', bound=Tuple[int, ...])


class UcReg(ctypes.Structure):
    """A base class for composite registers.

    This class is meant to be inherited, not instantiated directly.
    """

    @property
    @abstractmethod
    def value(self):
        """Get register value.
        """

        pass

    @classmethod
    @abstractmethod
    def from_value(cls, value):
        """Create a register instance from a given value.
        """

        pass


class UcTupledReg(UcReg, Generic[VT]):
    """A base class for registers whose values are represented as a set
    of fields.

    This class is meant to be inherited, not instantiated directly.
    """

    @property
    def value(self) -> VT:
        return tuple(getattr(self, fname) for fname, *_ in self.__class__._fields_)  # type: ignore

    @classmethod
    def from_value(cls, value: VT):
        assert type(value) is tuple and len(value) == len(cls._fields_)

        return cls(*value)


class UcLargeReg(UcReg):
    """A base class for large registers that are internally represented as
    an array of multiple qwords.

    This class is meant to be inherited, not instantiated directly.
    """

    qwords: ctypes.Array

    @property
    def value(self) -> int:
        return sum(qword << (64 * i) for i, qword in enumerate(self.qwords))

    @classmethod
    def from_value(cls, value: int):
        assert type(value) is int

        mask = (1 << 64) - 1
        size = cls._fields_[0][1]._length_

        return cls(tuple((value >> (64 * i)) & mask for i in range(size)))


class UcReg128(UcLargeReg):
    _fields_ = [('qwords', ctypes.c_uint64 * 2)]


class UcReg256(UcLargeReg):
    _fields_ = [('qwords', ctypes.c_uint64 * 4)]


class UcReg512(UcLargeReg):
    _fields_ = [('qwords', ctypes.c_uint64 * 8)]
