#!/usr/bin/env python3

class CoefficientTable(object):
    """ Demonstration class for byte-at-a-time and nibble-at-a-time
    CRC calculation methods. """

    @staticmethod
    def reverse_bits(data, width):
        """ Reverses a CRC polynomial. """
        return int(bin(data)[2:].zfill(width)[::-1],2)

    @staticmethod
    def print_hex(data, width=8):
        """ Prints hexadecimal numbers to the screen in a nicely-formatted
        block. """
        if type(data) == str:
            data = bytearray(data.encode())

        for x in range(0,len(data), 8):
            for y in data[x:x+8]:
                format_string = "%%0%dX " % (width / 4)
                print(format_string % y, end="")
            print("")
    
    def __init__(self, crc_width=8, poly=0x31, chunk_width=8):
        """ Initializes a CoefficientTable for a given CRC polynomial
        and CRC width.
        
        The table can be created for half-byte nibbles or for full-byte chunks
        (by specifying chunk_width to be 4 or 8). Depending on the selected
        implementation, either a half-byte or full-byte algorithm wil be
        consistently used as an example. """

        assert chunk_width in [4, 8]
        self.chunk_width = chunk_width
        self.crc_width = crc_width
        self.poly = poly
        self.table = [None] * (2**self.chunk_width)
        self.populate_table()

    def populate_table(self):
        """ Uses the initialized CRC polynomial to populate a lookup table
        for use in table-based CRC calculation algorithms. """
        
        for i in range(2**self.chunk_width):
            if self.chunk_width == 8:
                crc = i
            elif self.chunk_width == 4:
                crc = i << 4
            else:
                raise ValueError("Unsupported chunk width.")

            for j in range(8):
                crc = (crc >> 1) ^ (-int(crc & 1) & self.poly)

            self.table[i] = crc
    
    def calculate_crc(self, data, starting_value = 0x00):
        """ Calculates the CRC of a block of data (starting with an 
        initial value for the CRC register. This function uses a table-driven
        approach. """

        crc = starting_value
        if type(data) == str:
            data = bytearray(data.encode())

        if self.chunk_width == 8:
            for x in data:
                crc = (crc >> 8) ^ self.table[(crc ^ x) & 0xFF]
        elif self.chunk_width == 4:
            for x in data:
                crc = self.table[(crc ^ x) & 0x0F] ^ (crc >> 4)
                crc = self.table[(crc ^ (x >> 4)) & 0x0F] ^ (crc >> 4)
        else:
            raise ValueError("Unsupported chunk width.")

        return crc

class OneWireCRC(object):
    def __init__(self, chunk_width = 8):
        poly = CoefficientTable.reverse_bits(0x31, 8)
        self.table = CoefficientTable(8, poly, chunk_width)

    def calculate_crc(self, data, starting_value = 0x00):
        return self.table.calculate_crc(data, starting_value)
        

class Maxim16CRC(object):
    def __init__(self, chunk_width = 8):
        poly = CoefficientTable.reverse_bits(0x8005, 16)
        self.table = CoefficientTable(16, poly, chunk_width)

    def calculate_crc(self, data, starting_value = 0x00):
        result = self.table.calculate_crc(data, starting_value)
        result = result ^ 0xFFFF
        return result
        

def main():
    myCRC = OneWireCRC(8)
    CoefficientTable.print_hex(myCRC.table.table)
    CoefficientTable.print_hex("hello")
    print("0x%02X" % myCRC.calculate_crc("hello"))
    print("-----------------------------------------")

    myCRC = OneWireCRC(4)
    CoefficientTable.print_hex(myCRC.table.table)
    CoefficientTable.print_hex("hello")
    print("0x%02X" % myCRC.calculate_crc("hello"))
    print("-----------------------------------------")
    
    myCRC = Maxim16CRC(8)
    CoefficientTable.print_hex(myCRC.table.table, 16)
    CoefficientTable.print_hex("hello")
    print("0x%04X" % myCRC.calculate_crc("hello"))
    print("-----------------------------------------")

    myCRC = Maxim16CRC(4)
    CoefficientTable.print_hex(myCRC.table.table, 16)
    CoefficientTable.print_hex("hello")
    print("0x%04X" % myCRC.calculate_crc("hello"))
    print("-----------------------------------------")

if __name__ == "__main__":
    main()
