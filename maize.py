#!/usr/bin/env python

import sys
import cobs.cobs
import ctypes
import unittest
import random
import subprocess


class PyQueue(object):
    """ This class is used to provide an interface for Maize's
    transmitter/receiver libraries. """

    def __init__(self):
        self.reset()

    def reset(self):
        self.buffer = ''

    def load(self, char):
        self.buffer += char

    def dump(self):
        answer = self.buffer
        self.reset()
        return answer


class RemoteImplementation(object):
    """ This class provides encode()/decode() methods that use the
    library-under-test. """

    def __init__(self):
        self.queue = PyQueue()
        self._tx_type = ctypes.CFUNCTYPE(None, ctypes.c_char)
        self._tx = self._tx_type(self.queue.load)
        self._maize = ctypes.cdll.LoadLibrary("libmaize.so")

    def encode(self, packet):
        self.queue.reset()
        self._maize.tx_packet(packet, len(packet), self._tx)
        return self.queue.dump()

    def decode(self, packet):
        raise NotImplementedError("This function is not yet implemented.")


class ReferenceImplementation(object):
    """ This class provides encode()/decode() methods that use the
    PyPI's 'cobs' library. """
     
    def __init__(self):
        pass

    def encode(self, packet):
        return '\x00' + cobs.cobs.encode(packet) + '\x00'

    def decode(self, packet):
        if(packet[0] == '\x00'):
            packet = packet[1:]

        if(packet[-1] == '\x00'):
            packet = packet[:-1]

        return cobs.cobs.decode(packet)


class NoZerosTestCase(unittest.TestCase):
    """ This test-case verifies the behavior of the Maize library when
    given packets that have no null-characters. """

    def setUp(self):
        self.myRemote = RemoteImplementation()
        self.myReference = ReferenceImplementation()

    def tearDown(self):
        pass

    def arb_size(self, length):
        print("Running test: null-free packet of length %d" % length)
        packet = [chr(random.randint(1, 255)) for x in range(length)]
        packet = ''.join(packet)
        remote = self.myRemote.encode(packet)
        reference = self.myReference.encode(packet)
        try:
            self.assertEqual(remote, reference)
        except Exception as err:
            print(
                "remote [%s] != expected [%s]" %
                (repr(remote), repr(reference)))
            raise err

    def runTest(self):
        test_lengths = [0, 1, 2]
        test_lengths += list(range(253, 258))
        test_lengths += list(range(509, 514))

        for x in test_lengths:
            self.arb_size(x)


class AllZerosTestCase(unittest.TestCase):
    """ This test-case verifies the behavior of the Maize library when
    given packets that completely made of null-characters. """
    
    def setUp(self):
        self.myRemote = RemoteImplementation()
        self.myReference = ReferenceImplementation()

    def tearDown(self):
        pass

    def arb_size(self, length):
        print("Running test: all-null packet of length %d" % length)
        packet = '\x00' * length
        packet = ''.join(packet)
        remote = self.myRemote.encode(packet)
        reference = self.myReference.encode(packet)
        try:
            self.assertEqual(remote, reference)
        except Exception as err:
            print(
                "remote [%s] != expected [%s] (orig: [%s])" %
                (repr(remote), repr(reference), repr(packet)))
            raise err

    def runTest(self):
        test_lengths = [0, 1, 2]
        test_lengths += list(range(253, 258))
        test_lengths += list(range(509, 514))

        for x in test_lengths:
            self.arb_size(x)


class SomeZerosTestCase(unittest.TestCase):
    """ This test-case verifies the encoding of a set of a randomly-
    generated set of packets.
    
    There are no guarantees for which (if any) bytes in the source packet
    will be null-characters, but the test keeps the random range to within
    1/16 of the packet size (or a minimum of 4). That means that a packet
    of 512B will probably have numerous zeros with a very high probability.
    
    Various packet sizes are tested. Each test is repeated 512 times with
    new random values each time. """
   
    def setUp(self):
        self.myRemote = RemoteImplementation()
        self.myReference = ReferenceImplementation()

    def tearDown(self):
        pass

    def arb_size(self, length):
        rand_max = max(int(length / 16), 4)
        packet = [chr(random.randint(0, rand_max)) for x in range(length)]
        packet = ''.join(packet)
        remote = self.myRemote.encode(packet)
        reference = self.myReference.encode(packet)
        try:
            self.assertEqual(remote, reference)
        except Exception as err:
            print(
                "remote [%s] != expected [%s]" %
                (repr(remote), repr(reference)))
            raise err

    def runTest(self):
        test_lengths = [0, 1, 2]
        test_lengths += list(range(253, 258))
        test_lengths += list(range(509, 514))

        for x in test_lengths:
            print("Running test: random packet of length %d" % x)
            for y in range(512):
                self.arb_size(x)


class NicksTestCase(unittest.TestCase):
    """ This test-case verifies the encoding of a set of specially-made
    test vectors. 
    
    The test vectors insert null-characters at various places near the
    256B and 512B boundaries (each location gets a full sweep of 5 bits
    starting at N-3). Other null characters in-between blocks are also
    cycled.
    
    This test case should be sufficient to cover all of the 'dark 
    corners' of the COBS encoding method. """   
     
    def setUp(self):
        self.myRemote = RemoteImplementation()
        self.myReference = ReferenceImplementation()
        sys.stdout.write("\nPreparing test vectors...")
        sys.stdout.flush()
        self.make_vectors()
        print("done")

    def tearDown(self):
        pass

    def make_vectors(self):
        sub_patterns = []
        self.vectors = []

        for x in range(32):
            block = bin(x)[2:].zfill(5)
            block = block.replace('0', '\x00')
            block = block.replace('1', '.')
            sub_patterns.append(block)

        zero_locs = [[], [64], [300]]
        zero_locs += [[520], [64, 300], [64, 300, 520]]
        zero_locs += [[300, 520], [64, 520]]

        for sub_a in sub_patterns:
            for sub_b in sub_patterns:
                for other_zeros in zero_locs:
                    new_vector = bytearray('.' * 540)
                    new_vector[252:257] = sub_a
                    new_vector[508:513] = sub_b
                    for zero in other_zeros:
                        new_vector[zero] = '\x00'
                    self.vectors.append(str(new_vector))

    def runTest(self):
        count = 0
        L = float(len(self.vectors))
        old_percent = -1
        for vector in self.vectors:
            count = count + 1
            new_percent = int((float(count) / L) * 100)
            if new_percent != old_percent:
                sys.stdout.write("\r    \r%d%%" % new_percent)
                sys.stdout.flush()
                old_percent = new_percent

            remote = self.myRemote.encode(vector)
            reference = self.myReference.encode(vector)
            try:
                self.assertEqual(remote, reference)
            except Exception as err:
                print(
                    "remote [%s] != expected [%s]" %
                    (repr(remote), repr(reference)))
                raise err
        sys.stdout.write("Done.\n")

if __name__ == '__main__':
    subprocess.check_call(['make', 'libmaize.so'])
    unittest.main()
