import time

class Cpu6502:
    CLOCK_TIME = 1 / 1000.0  # time in ms

    # Registers
    a = 0
    x = 0
    y = 0

    # program counter
    pc = 0

    # stack pointer
    sp = 0

    # flags
    C = False
    Z = False
    I = False
    D = False
    B = False
    V = False
    N = False

    # address bus
    address = 0

    memory = [0] * 0x10000

    def read_byte(self, address):
        time.sleep(self.CLOCK_TIME)
        return self.memory[address] & 0xFF

    def write_byte(self, address, value):
        time.sleep(self.CLOCK_TIME)
        self.memory[address] = value & 0xFF

    # Fetch little endian address
    def read_address(self, offset):
        val = self.read_byte(offset + 1)
        val <<= 8
        val |= self.read_byte(offset)
        return val

    def decode(self, opcode):
        high_nibble = opcode >> 4
        low_nibble = opcode & 0x0F
        if low_nibble == 8:
            # SB1 Logic
            pass
        elif low_nibble == 0xA and high_nibble > 7:
            # SB2 Logic
            pass
        else:
            # Groups G1-G3
            # aaa bbb cc
            aaa = (opcode & 0b11100000) >> 5  # Operation
            bbb = (opcode & 0b00011100) >> 2  # Addressing mode
            cc = opcode & 0b00000011  # Group number

            if cc == 1:
                # G1 address decoding and opcode logic
                pass
            elif cc == 2:
                # G2 address decoding and opcode logic
                pass
            elif cc == 3:
                # xxy 100 00
                if bbb == 4:
                    # Conditional branching logic
                    pass
                elif bbb == 0 and not (aaa & 0x4):
                    # I/S logic
                    pass
                else:
                    # G3 address decoding and opcode logic
                    pass


def main():
    cpu = Cpu6502()

    print(cpu)


if(__name__ == "__main__"):
    main()
