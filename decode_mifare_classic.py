#!/usr/bin/env python

import re
import struct
import sys

regex = re.compile(r'Block \d+:((?: [0-9A-F]{2})+)')

sector_struct = struct.Struct('<16s16s16s6s3cc6s')

class Sector:
    @staticmethod
    def get_access_bits(offset, access_byte_0, access_byte_1, access_byte_2):
        control = (
                bool((0x10 << offset) & access_byte_1) << 2 |
                bool((0x01 << offset) & access_byte_2) << 1 |
                bool((0x10 << offset) & access_byte_2) << 0
                )
        not_control = (
                bool((0x01 << offset) & access_byte_0) << 2 |
                bool((0x10 << offset) & access_byte_0) << 1 |
                bool((0x01 << offset) & access_byte_1) << 0
                )

        return control, control == 0x07 & ~not_control

    def __init__(self, block_0, block_1, block_2, key_a, access_byte_0, access_byte_1, access_byte_2, user_data, key_b):
        self.block_0 = block_0
        self.block_1 = block_1
        self.block_2 = block_2
        self.key_a = key_a
        self.user_data = user_data
        self.key_b = key_b

        access_byte_0 = int.from_bytes(access_byte_0, 'little')
        access_byte_1 = int.from_bytes(access_byte_1, 'little')
        access_byte_2 = int.from_bytes(access_byte_2, 'little')

        self.control_0, self.valid_0 = self.get_access_bits(0, access_byte_0, access_byte_1, access_byte_2)
        self.control_1, self.valid_1 = self.get_access_bits(1, access_byte_0, access_byte_1, access_byte_2)
        self.control_2, self.valid_2 = self.get_access_bits(2, access_byte_0, access_byte_1, access_byte_2)
        self.control_3, self.valid_3 = self.get_access_bits(3, access_byte_0, access_byte_1, access_byte_2)

    def __str__(self):
        return f'''block 0: {self.block_0.hex()}
block 1: {self.block_1.hex()}
block 2: {self.block_2.hex()}
key a: {self.key_a.hex()}
key b: {self.key_b.hex()}
user data: {self.user_data.hex()}
control 0: {format(self.control_0, '03b')} (valid: {self.valid_0})
control 1: {format(self.control_1, '03b')} (valid: {self.valid_1})
control 2: {format(self.control_2, '03b')} (valid: {self.valid_2})
control 3: {format(self.control_3, '03b')} (valid: {self.valid_3})'''

def main():
    def generate_lines():
        for line in sys.stdin:
            line = line.strip()
            if match := regex.fullmatch(line):
                yield bytes.fromhex(match.group(1))

    data = b''.join(generate_lines())
    sectors = list(Sector(*t) for t in sector_struct.iter_unpack(data))
    for index, sector in enumerate(sectors):
        print('sector', index)
        print(sector)
        print()

if __name__ == '__main__':
    main()
