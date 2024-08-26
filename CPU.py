import random
from bdb import effective


class Memory:
    MAX_SIZE = 1024 * 64
    data = [0] * MAX_SIZE

    def initialize(self):
        for i in range(self.MAX_SIZE):
            self.data[i] = 0

    def __getitem__(self, key):
        return self.data[key] & 0xFF

    def __setitem__(self, key, value):
        self.data[key] = value

    def write_word(self, value, address, cycles):
        self.data[address] = value & 0xFF
        self.data[address + 1] = (value >> 8) & 0xFF
        cycles -= 2


# Used because python ints are immutable when passed into function :(
class CycleCounter:
    def __init__(self, count):
        self.cycleCount = count
    # -= overload
    def __isub__(self, other):
        self.cycleCount -= other
        return self
    def __str__(self):
        return str(self.cycleCount)

asm_mnemonic = {0xA9 : "LDA(IMM)",
                0xA5 : "LDA(ZP)",
                0xB5 : "LDA(ZPX)",
                0x20 : "JSR"}
# opcodes
INS_LDA_IM = 0xA9
INS_LDA_ZP = 0xA5
INS_LDA_ZPX = 0xB5
INS_LDA_ABS = 0xAD
INS_LDA_ABSX = 0xBD
INS_LDA_ABSY = 0xB9
INS_LDA_INDX = 0xA1
INS_LDA_INDY = 0xB1
INS_JSR = 0x20

class Cpu6502:

    def __init__(self):
        self.CLOCK_TIME = 1 / 1000.0  # time in ms

        # Registers
        self.A = 0
        self.X = 0
        self.Y = 0

        # program counter
        self.PC = 0

        # stack pointer
        self.SP = 0

        # flags
        self.C = False
        self.Z = False
        self.I = False
        self.D = False
        self.B = False
        self.V = False
        self.N = False

        # address bus
        self.address = 0


    def reset(self, memory):
        self.PC = 0xFFFC
        self.SP = 0xFF
        self.C = self.Z = self.I = self.D = self.B = self.V = self.N = 0
        self.A = self.X = self.Y = 0
        memory.initialize()

    def fetch_byte(self, cycles: CycleCounter, memory: Memory):
        byte_data = memory[self.PC] & 0xFF
        self.PC += 1
        cycles -= 1
        return byte_data & 0xFF

    def fetch_word(self, cycles: CycleCounter, memory: Memory):

        # Little endian
        word_data = memory[self.PC] & 0xFF
        self.PC += 1
        word_data |= memory[self.PC] << 8
        self.PC += 1

        cycles -= 2

        return word_data & 0xFFFF

    def read_byte(self, cycles : CycleCounter, memory : Memory, address):
        byte_data = memory[address & 0xFFFF] & 0xFF
        cycles -= 1
        return byte_data & 0xFF

    def read_word(self, cycles : CycleCounter, memory : Memory, address):
        low = self.read_byte(cycles, memory, address)
        high = self.read_byte(cycles, memory, address + 1)

        word_data = low | (high << 8)
        return word_data & 0xFFFF

    def LDA_set_status(self):
        self.Z = (self.A == 0)
        self.N = (self.A & 0b10000000) > 0

    def tick(self, cycles : CycleCounter, memory):
        ins = self.fetch_byte(cycles, memory)

        if ins == INS_LDA_IM:
            value = self.fetch_byte(cycles, memory)
            self.A = value
            self.LDA_set_status()

        elif ins == INS_LDA_ZP:
            zero_page_address = self.fetch_byte(cycles, memory)
            self.A = self.read_byte(cycles, memory, zero_page_address)
            self.LDA_set_status()

        elif ins == INS_LDA_ZPX:
            zero_page_address = self.fetch_byte(cycles, memory)
            zero_page_address += self.X
            cycles -= 1
            self.A = self.read_byte(cycles, memory, zero_page_address & 0xFF)
            self.LDA_set_status()

        elif ins == INS_LDA_ABS:
            abs_addr = self.fetch_word(cycles, memory)
            self.A = self.read_byte(cycles, memory, abs_addr)
            self.LDA_set_status()

        elif ins == INS_LDA_ABSX:
            abs_addr = self.fetch_word(cycles, memory)
            abs_addr_x = abs_addr + (self.X & 0xFF)
            self.A = self.read_byte(cycles, memory, abs_addr_x)
            if abs_addr >> 8 != abs_addr_x >> 8:  # page crossed
                cycles -= 1
            self.LDA_set_status()

        elif ins == INS_LDA_ABSY:
            abs_addr = self.fetch_word(cycles, memory)
            abs_addr_y = abs_addr + (self.Y & 0xFF)
            self.A = self.read_byte(cycles, memory, abs_addr_y)
            if abs_addr >> 8 != abs_addr_y >> 8:  # page crossed
                cycles -= 1
            self.LDA_set_status()

        elif ins == INS_LDA_INDX:
            zp_address = self.fetch_byte(cycles, memory)
            zp_address += self.X & 0xFF
            cycles -= 1
            effective_address = self.read_word(cycles, memory, zp_address)
            self.A = self.read_byte(cycles, memory, effective_address)
        elif ins == INS_LDA_INDY:
            zp_address = self.fetch_byte(cycles, memory)
            effective_address = self.read_word(cycles, memory, zp_address)
            effective_address_y = effective_address + self.Y & 0xFFFF
            self.A = self.read_byte(cycles, memory, effective_address_y)
            if effective_address >> 8 != effective_address_y >> 8:  # page crossed
                cycles -= 1

        elif ins == INS_JSR:
            subroutine_address = self.fetch_word(cycles, memory)
            memory.write_word( self.PC - 1, self.SP, cycles)
            self.SP += 2
            self.PC = subroutine_address
            cycles -= 1

        else:
            raise Exception("Invalid instruction: " + hex(ins))
            # print("Instruction not handled: " + hex(ins))

    def execute(self, cycles : CycleCounter, memory):

        cyclesRequested = cycles.cycleCount

        while cycles.cycleCount > 0:
            self.tick(cycles, memory)

        return cyclesRequested - cycles.cycleCount
    # def decode(self, opcode):
    #     high_nibble = opcode >> 4
    #     low_nibble = opcode & 0x0F
    #     if low_nibble == 8:
    #         # SB1 Logic
    #         pass
    #     elif low_nibble == 0xA and high_nibble > 7:
    #         # SB2 Logic
    #         pass
    #     else:
    #         # Groups G1-G3
    #         # aaa bbb cc
    #         aaa = (opcode & 0b11100000) >> 5  # Operation
    #         bbb = (opcode & 0b00011100) >> 2  # Addressing mode
    #         cc = opcode & 0b00000011  # Group number
    #
    #         if cc == 1:
    #             # G1 address decoding and opcode logic
    #             pass
    #         elif cc == 2:
    #             # G2 address decoding and opcode logic
    #             pass
    #         elif cc == 3:
    #             # xxy 100 00
    #             if bbb == 4:
    #                 # Conditional branching logic
    #                 pass
    #             elif bbb == 0 and not (aaa & 0x4):
    #                 # I/S logic
    #                 pass
    #             else:
    #                 # G3 address decoding and opcode logic
    #                 pass

