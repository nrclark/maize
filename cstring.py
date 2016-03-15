#!/usr/bin/env python

""" This module provides classes called MockStringPointer and MockUint8/16/32.
These classes can be used for prototyping uint/char[]-based C algorithms in
Python.

MockStringPointers act basically just like a regular C (char *)
pointer, except that they are connected to a fixed-length buffer
that is allocated on pointer creation. MockStringPointers are
immutable (like a Python integer), but the internal string buffer
is mutable and preserved.

MockUints act just like a python integer, except that you can specify their
width at creation (if creating with MockUint) or explicity select a width by
choosing the appropriate subclass. """

import random as _random
import collections as _collections


class MockStringPointer(object):
    """ This class implements a C-style string pointer for use in
    algorithm prototyping. It behaves more-or-less like the 'char *'
    data type in C.

    Integer values can be added/subtracted from MockStringPointer
    instances just like in C. Additionally, derived MockStringPointers
    can be subtracted from each other to simulate pointer arithmetic.
    MockStringPointers can also be indexed by integer values to
    retrieve or modify the stored data. """

    # pylint: disable=too-few-public-methods
    value = None

    def __init__(self, value='', **kwargs):
        """ Creates a MockStringPointer from an int (allocates an empty
        buffer), a string (allocates a new buffer and copies the contents),
        a bytearray (points to the existing bytearray), or another
        MockStringPointer (creates a new instance with the same buffer and
        attributes). """

        if isinstance(value, int):
            if 'size' in kwargs:
                errmsg = "Error: can't specify 'size' keyword when"
                errmsg += "manually specifying a length in the 'value' "
                errmsg += "argument."
                raise ValueError(errmsg)

            self._address = _random.randint(0, 0xFFFFFFFF - value)
            self._buffer = bytearray(value)
            self._index = 0
            self._size = value

        if isinstance(value, str):
            if 'size' in kwargs:
                size = kwargs['size']
            else:
                size = len(value)
            self._address = _random.randint(0, 0xFFFFFFFF - size)
            value = value + '\x00' * size
            value = value[0:size]
            self._buffer = bytearray(value)
            self._index = 0
            self._size = size

        elif isinstance(value, bytearray):
            # pylint: disable=redefined-variable-type
            self._buffer = value
            self._size = len(value)
            self._address = _random.randint(0, 0xFFFFFFFF - self._size)
            if 'index' in kwargs:
                self._index = kwargs['index']

        elif isinstance(value, MockStringPointer):
            # pylint: disable=protected-access, no-member
            self._buffer = value._buffer
            self._size = value._size
            self._index = value._index
            self._address = value._address
            if 'offset' in kwargs:
                self._index += kwargs['offset']

    def _verify_bounds(self, offset=0):
        """ Throws an exception if the requested offset indexes to
        an unallocated region of the buffer. This function is used
        to enforce safety when dereferencing a MockStringPointer. """

        if (self._index + offset) < 0:
            raise ValueError('Buffer underflow.')
        if (self._index + offset) >= self._size:
            raise ValueError('Buffer overflow.')

    def _value(self):
        """ This function returns the string representation of the stored
        data within the class instance. Similar to a C-style string, this
        function returns all data up to the first NULL character (\\x00).
        If no NULL is present, the entire string is returned. """

        self._verify_bounds()
        start = self._index
        end = start + (self._buffer[start:] + '\x00').index('\x00')
        return str(self._buffer[start:end])

    def __getattribute__(self, name):
        """ Wrapper around the default getattribute method. """

        if name == 'value':
            return self._value()
        else:
            return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        """ Wrapper around the default setattr method that prevents
        the 'value' attribute from being manually adjusted. """

        if name == 'value':
            pass
        else:
            return object.__setattr__(self, name, value)

    def __getitem__(self, key):
        """ Implementation of single-value indexing (such as
        myData[0]) to mimic C (char *) pointers. """

        if isinstance(key, int):
            self._verify_bounds(key)
            return chr(self._buffer[self._index + key])
        if isinstance(key, slice):
            errmsg = "Slicing is not supported for MockStringPointer "
            errmsg += "objects."
            raise IndexError(errmsg)
        else:
            errmsg = "Can't index MockStringPointer using %s."
            errmsg %= type(key)
            raise TypeError(errmsg)

    def __setitem__(self, key, value):
        """ Implementation of single-value indexing (such as
        myData[0]) to mimic C (char *) pointers. """

        if isinstance(key, int):
            self._verify_bounds(key)
            self._buffer[self._index + key] = value
        else:
            errmsg = "Can't index a MockStringPointer with type <%s>."
            errmsg = errmsg % type(key)
            raise TypeError(errmsg)

    def __add__(self, value):
        """ Adds an integer offset to a MockStringPointer and returns
        a new MockStringPointer instance with the same internal buffer. """

        if isinstance(value, int):
            return MockStringPointer(self, offset=value)
        elif isinstance(value, MockStringPointer):
            raise TypeError("Can't add two pointers.")
        else:
            errmsg = "Can't add %s to <type 'MockStringPointer'>."
            errmsg = errmsg % type(value)
            raise TypeError(errmsg)

    def __sub__(self, value):
        """ Subtracts an integer offset from a MockStringPointer and
        returns a new MockStringPointer instance with the same internal
        buffer. """

        if isinstance(value, int):
            return MockStringPointer(self, offset=-value)
        elif isinstance(value, MockStringPointer):
            # pylint: disable=protected-access
            if value._address != self._address:
                raise ValueError("Can't subtract unrelated pointers.")
            return self._index - value._index
        else:
            errmsg = "Can't subtract %s from <type 'MockStringPointer'>."
            errmsg = errmsg % type(value)
            raise TypeError(errmsg)

    def __repr__(self):
        """ Returns a machine representation of the MockStringPointer. """

        address = self._address + self._index
        label = '0x' + hex(address)[2:].upper()
        result = "<MockStringPointer to %s>" % label
        return result

    def __str__(self):
        """ Returns a human representation of the MockStringPointer.
        Used for casting MockStringPointer contents to Python strings
        or bytearrays. """

        self._verify_bounds()
        return str(self._buffer[self._index:self._size])

    def __int__(self):
        """ Returns the integer equivalent of our mock memory address. """
        return self._address + self._index

    def __eq__(self, other):
        """ x.__eq__(y) => (x == y) """
        return int(self) == int(other)

    def __ne__(self, other):
        """ x.__ne__(y) => (x != y) """
        return int(self) != int(other)

    def __gt__(self, other):
        """ x.__gt__(y) => (x > y) """
        return int(self) > int(other)

    def __lt__(self, other):
        """ x.__lt__(y) => (x < y) """
        return int(self) < int(other)

    def __ge__(self, other):
        """ x.__ge__(y) => (x >= y) """
        return int(self) >= int(other)

    def __le__(self, other):
        """ x.__le__(y) => (x <= y) """
        return int(self) <= int(other)


class _MockUintMeta(type):
    """ This metaclass should not be called directly. It is used to provide
    magic methods for all of the 'int' type's arithmetic methods. Rather than
    write them all out as class methods in MockUint, this metaclass aliases
    all of them to __math__, which intelligently handles type-checking and
    emulates overflow. """

    def __init__(cls, *args, **kwargs):
        math_funcs = ['__add__', '__sub__', '__mul__', '__floordiv__',
                      '__mod__', '__divmod__', '__pow__', '__lshift__',
                      '__rshift__', '__and__', '__xor__', '__or__']

        for name in math_funcs:
            # pylint: disable=eval-used
            func = eval("lambda x,y: cls.__math__(x,y,'%s')" % name, locals())
            setattr(cls, name, func)

        super(_MockUintMeta, cls).__init__(*args, **kwargs)


class MockUint(object):
    """ This class emulates a C-style unsigned integer. It interoperates
    seamlessly with standard Python integers, except that the width can be
    specified when each new instance is created.

    A math operation with two MockUint operands will return a MockUint with
    the larger of the two operands' widths. A math operation with one MockUint
    and one integer operand will return a MockUint with the original MockUint's
    width. """

    #pylint: disable=too-few-public-methods
    __metaclass__ = _MockUintMeta

    @staticmethod
    def __math__(op1, op2, name, width=128):
        """ This function provides MockUint with all of its arithmetic methods.
        It works by converting input arguments to type int, calling the correct
        'int' class method (by way of int.__dict__), masking off the relevant
        bits from the result, and returning the result as a MockUint. """

        new_type = MockUint

        if isinstance(op1, MockUint):
            # pylint: disable=protected-access

            width = op1._width
            new_type = type(op1)
            op1 = int(op1)

        if isinstance(op2, MockUint):
            # pylint: disable=protected-access

            if op2._width > width:
                width = op2._width
                new_type = type(op2)
            op2 = int(op2)

        mask = 2**width - 1
        result = int.__dict__[name](op1, op2)

        if isinstance(result, _collections.Iterable):
            result = [x & mask for x in result]
            result = [new_type(value=x, width=width) for x in result]
            output = tuple(result)
            return output
        else:
            result = result & mask
            return new_type(value=result, width=width)

    def __init__(self, value=0, width=128):
        """ Creates a new MockUint instance. The optional 'value' parameter
        specifies the MockUint's initial value, and the optional 'width'
        parameter specifies the MockUint's width. """

        self._width = width
        self._value = value & (2**width - 1)

    def __str__(self):
        return "%d" % self._value

    def __repr__(self):
        return "%d" % self._value

    def __int__(self):
        return self._value

    def __float__(self):
        return float(self._value)

class MockUint8(MockUint):
    """ Creates a Python mockup of an unsigned 8-bit integer. Read the MockUint
    class doctstring for more details. Delaring a MockUint8 is functionally
    equivalent to delaring a MockUint with 'width=8' passed to the constructor.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, value=0, width=128):
        """ Creates a new MockUint8 instance. The optional 'value' parameter
        specifies the MockUint8's initial value. """

        super(MockUint8, self).__init__(value, width=8)

class MockUint16(MockUint):
    """ Creates a Python mockup of an unsigned 16-bit integer. Read the MockUint
    class doctstring for more details. Delaring a MockUint16 is functionally
    equivalent to delaring a MockUint with 'width=16' passed to the constructor.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, value=0, width=128):
        """ Creates a new MockUint8 instance. The optional 'value' parameter
        specifies the MockUint8's initial value. """

        super(MockUint16, self).__init__(value, width=16)

class MockUint32(MockUint):
    """ Creates a Python mockup of an unsigned 32-bit integer. Read the MockUint
    class doctstring for more details. Delaring a MockUint16 is functionally
    equivalent to delaring a MockUint with 'width=32' passed to the constructor.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, value=0, width=128):
        """ Creates a new MockUint8 instance. The optional 'value' parameter
        specifies the MockUint8's initial value. """

        super(MockUint32, self).__init__(value, width=32)
