#!/usr/bin/env python

import sys
import cobs.cobs
import ctypes
import unittest
import random
import subprocess

class PyQueue(object):
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
    def __init__(self):
        self.queue = PyQueue()
        self._tx_type = ctypes.CFUNCTYPE(None,ctypes.c_char)
        self._tx = self._tx_type(self.queue.load)        
        self._maize = ctypes.cdll.LoadLibrary("libmaize.so")
    
    def encode(self, packet):
        self.queue.reset()
        self._maize.tx_packet(packet, len(packet),self._tx)
        return self.queue.dump()
        
    def decode(self, packet):
        raise NotImplementedError("This function is not yet implemented.")
    
class ReferenceImplementation(object):
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
    def setUp(self):
        self.myRemote = RemoteImplementation()
        self.myReference = ReferenceImplementation()

    def tearDown(self):
        pass
    
    def arb_size(self, length):
        print("Running test: null-free packet of length %d" % length)
        packet = [chr(random.randint(1,255)) for x in range(length)]
        packet = ''.join(packet)
        remote = self.myRemote.encode(packet)
        reference = self.myReference.encode(packet)
        try:
            self.assertEqual(remote, reference)
        except Exception as err:
            print("remote [%s] != expected [%s]" % (repr(remote), repr(reference)))
            raise err
    
    def runTest(self):
        test_lengths = [0, 1, 2]
        test_lengths += list(range(253,258))
        test_lengths += list(range(509,514))

        for x in test_lengths:
            self.arb_size(x)

class ZAllZerosTestCase(unittest.TestCase):                
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
            print("remote [%s] != expected [%s] (orig: [%s])" % (repr(remote), repr(reference), repr(packet)))
            raise err

    @unittest.expectedFailure
    def runTest(self):
        test_lengths = [0,1,2]
        test_lengths += list(range(253,258))
        test_lengths += list(range(509,514))

        for x in test_lengths:
            self.arb_size(x)

if __name__ == '__main__':
    subprocess.check_call(['make', 'libmaize.so'])
    unittest.main()
    