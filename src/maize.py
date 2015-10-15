#!/usr/bin/env python

import sys
import cobs.cobs

class printer(object):
    def __init__(self):
        self.count = 0
        self.newline = True

    def __call__(self, char, special=False):
        assert len(char) == 1
        if self.newline:
            self.decolorize()
            sys.stdout.write('%04d: ' % self.count)
            self.newline = False
    
        if char == '\x00':
            self.colorize()
            sys.stdout.write(" %02X" % ord(char))
            self.decolorize()
        elif(special):
            sys.stdout.write("\033[0;44m")
            sys.stdout.write(" %02X" % ord(char))
        else:
            sys.stdout.write(" %02X" % ord(char))
        
        self.count += 1
    
        if (self.count % 8) == 0:
            sys.stdout.write("\n")
            self.newline = True

    def colorize(self):
        sys.stdout.write('\033[0;45m')
    
    def decolorize(self):
        sys.stdout.write('\033[0;34m')        

class transmitter(object):
    def __init__(self):
        pass
        
    def __call__(self, packet):
        tx = printer()
        
        tx('\x00')
        
        for x in cobs.cobs.encode(packet):
            tx(x)
        
        tx('\x00')

def main():
    packet = [chr(x & 0xFF) for x in range(460)]
    packet = [x if x != '\x00' else '\xFF' for x in packet]
    packet[8] = '\x00'
    packet[197] = '\x00'
    packet = ''.join(packet)
    
    tx_packet = transmitter()
    tx_packet(packet)
    sys.stdout.write("\n")
    
if __name__ == "__main__":
    main()
    