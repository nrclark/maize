#!/usr/bin/env python
""" Module for prototyping a COBS encoder and decoder. This module
can be used standalone, but it's probably not the most efficient
implementation. It is designed to be easily portable to C. """


import unittest
import random

import cobs.cobs
import cstring


class Queue(object):
    """ This class is intended to be used for prototyping
    serialization/deserialization algorithms or communications
    channels. It provides a simple FIFO/Queue interface. """

    def __init__(self, initial='', mode='byte'):
        """ Create a new Queue with an optional initial value. 'Mode', if
        set, controls the format of popped output data. Valid values for 'mode'
        are 'byte', 'string', and 'int'. """

        self.contents = bytearray(initial)
        self.set_mode(mode)

    def __len__(self):
        """ Returns the length of the stored queue. """
        return len(self.contents)

    def __repr__(self):
        """ Returns the machine representation of a Queue. """
        return repr(str(self.contents))

    def __str__(self):
        """ Returns the string representation of a Queue. """
        return str(self.contents)

    def push(self, value):
        """ Pushes a new value (either an int or a length-1 string)
        onto the target Queue. """
        #print("tx: [%s]" % str(value))
        self.contents.append(value)

    def pop(self):
        """ Returns the oldest value still in the Queue. """
        retval = self.contents[:1]
        self.contents.pop(0)

        if self._mode == 'int':
            return retval[0]
        elif self._mode == 'string':
            return str(retval)
        elif self._mode == 'byte':
            return retval
        else:
            raise ValueError("Unknown pop mode!")

    def has_data(self):
        """ Returns true if the Queue has any pending data. """
        return len(self.contents) != 0

    def set_mode(self, mode='byte'):
        """ Sets the 'pop' mode to be 'int' or 'byte', or 'string'. The default
        mode is 'byte'. """

        if mode.lower().strip() not in ['byte', 'int', 'string']:
            raise ValueError("Unknown pop mode: %s" % mode)

        self._mode = mode.lower().strip()

    def dump(self):
        """ Dumps the entire Queue and returns it as a string. """
        # pylint: disable=redefined-variable-type

        if self._mode == 'int':
            retval = list(self.contents)
        elif self._mode == 'string':
            retval = str(self.contents)
        elif self._mode == 'byte':
            retval = self.contents
        else:
            raise ValueError("Unknown pop mode!")
        self.contents = bytearray()
        return retval


def cobs_send(packet, length, transmitter):
    """ Transmits a block of data with a classic COBS encoding scheme.
    This function will call transmitter(char) on every char of data to
    transmit (in order to emulate its C equivalent). """

    pointer = cstring.MockStringPointer(packet)
    end = pointer + length
    pointer = pointer - 1

    while True:
        remaining = end - pointer
        block_size = min(remaining, 255)

        loc = 1
        while loc < block_size:
            if pointer[loc] == '\x00':
                break
            loc = loc + 1

        transmitter(loc)
        pointer = pointer + 1
        block_end = pointer + loc - 1

        while pointer < block_end:
            transmitter(pointer[0])
            pointer = pointer + 1

        if pointer >= end:
            break

        pointer = pointer - (loc == block_size)


class TestCobs(unittest.TestCase):
    """ Test suite for the COBS library. This suite compares the barebones
    cobs_send() library against the Python Package Index's 'cobs.cobs'
    module. """

    # pylint: disable=missing-docstring

    def setUp(self):
        """ Configures the test-runner. """
        self.fifo = Queue(mode='string')

    def _run_test(self, message):
        """ Uses the local COBS encoder to encode a packet, and compares it
        to the locally-encoded equivalent. """

        cobs_send(message, len(message), self.fifo.push)
        packet = self.fifo.dump()
        self.assertEqual(packet, cobs.cobs.encode(message))

    def test_empty(self):
        """ Tests an empty packet. """
        self._run_test("")

    def test_one_null(self):
        """ Tests a packet consisting of a single zero. """
        self._run_test("\x00")

    def test_one_char(self):
        """ Tests a packet consisting of a single non-null character. """
        self._run_test("\x01")

    def test_hello(self):
        """ Tests a short no-null packet. """
        self._run_test("hello")

    def test_short_with_null(self):
        """ Tests a short packet with a null in it. """
        self._run_test("hel\x00lo")

    def test_long(self):
        """ Tests a long packet with no nulls in it. """
        self._run_test(254 * 'a' + 'b' + 253 * 'c')

    def test_long_middle_null(self):
        """ Tests a long packet with a zero in various locations. """
        for block in [0, 1, 2, 252, 253, 254, 255]:
            self._run_test(block * 'a' + '\x00' + 253 * 'c')

    def test_all_null(self):
        """ Tests an all-null packet of various lengths. """
        for block in range(250, 259):
            self._run_test(block * '\x00')

    def test_random_data(self):
        """ This test sweeps the COBS transmitter through a variety of
        different message lengths. Messages are randomly generated, but
        will generally have approximately 25% zeros in them. Each message
        length is swept through several passes. """

        lengths = [64, 254, 255, 256, 257, 509, 510, 511, 512, 513, 514]

        for _ in range(16):
            for length in lengths:
                message = bytearray(length)
                for slot in range(length):
                    if random.random() >= 0.25:
                        message[slot] = 1

                self._run_test(str(message))

if __name__ == "__main__":
    unittest.main()
