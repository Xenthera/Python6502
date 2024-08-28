import random
from bdb import effective

# The cpu
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
#region opcodes
INS_LDA_IM = 0xA9
INS_LDA_ZP = 0xA5
INS_LDA_ZPX = 0xB5
INS_LDA_ABS = 0xAD
INS_LDA_ABSX = 0xBD
INS_LDA_ABSY = 0xB9
INS_LDA_INDX = 0xA1
INS_LDA_INDY = 0xB1

INS_LDX_IM = 0xA2
INS_LDX_ZP = 0xA6
INS_LDX_ZPY = 0xB6
INS_LDX_ABS = 0xAE
INS_LDX_ABSY = 0xBE

INS_LDY_IM = 0xA0
INS_LDY_ZP = 0xA4
INS_LDY_ZPX = 0xB4
INS_LDY_ABS = 0xAC
INS_LDY_ABSX = 0xBC

INS_STA_ZP = 0x85
INS_STA_ZPX = 0x95
INS_STA_ABS = 0x8D
INS_STA_ABSX = 0x9D
INS_STA_ABSY = 0x99
INS_STA_INDX = 0x81

INS_STX_ZP = 0x86
INS_STX_ABS = 0x8E

INS_STY_ZP = 0x84
INS_STY_ABS = 0x8C
INS_STY_ZPX = 0x94



INS_JSR = 0x20

#endregion

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

    # Addressing mode handling
    # Zero Page
    def addr_zero_page(self, cycles: CycleCounter, memory : Memory):
        zero_page_address = self.fetch_byte(cycles, memory)
        return zero_page_address & 0xFF

    def addr_zero_page_x(self, cycles : CycleCounter, memory : Memory):
        zero_page_address = self.fetch_byte(cycles, memory)
        zero_page_address += self.X
        cycles -= 1
        return zero_page_address & 0xFF

    def addr_zero_page_y(self, cycles : CycleCounter, memory : Memory):
        zero_page_address = self.fetch_byte(cycles, memory)
        zero_page_address += self.Y
        cycles -= 1
        return zero_page_address & 0xFF

    def addr_absolute(self, cycles : CycleCounter, memory : Memory):
        abs_addr = self.fetch_word(cycles, memory)
        return abs_addr

    def addr_absolute_x(self, cycles : CycleCounter, memory : Memory):
        abs_addr = self.fetch_word(cycles, memory)
        abs_addr_x = abs_addr + (self.X & 0xFF)
        if abs_addr >> 8 != abs_addr_x >> 8:  # page crossed
            cycles -= 1
        return abs_addr_x & 0xFFFF

    def addr_absolute_y(self, cycles : CycleCounter, memory : Memory):
        abs_addr = self.fetch_word(cycles, memory)
        abs_addr_y = abs_addr + (self.Y & 0xFF)
        if abs_addr >> 8 != abs_addr_y >> 8:  # page crossed
            cycles -= 1
        return abs_addr_y & 0xFFFF

    def LD_register_set_status(self, register):
        reg_value = getattr(self, register)
        self.Z = (reg_value == 0)
        self.N = (reg_value & 0b10000000) > 0

    def load_register(self, cycles, memory, address, register):
        setattr(self, register, self.read_byte(cycles, memory, address))
        self.LD_register_set_status(register)

    def tick(self, cycles : CycleCounter, memory : Memory):
        ins = self.fetch_byte(cycles, memory)

        if ins == INS_LDA_IM:
            self.A = self.fetch_byte(cycles, memory)
            self.LD_register_set_status("A")
        elif ins == INS_LDX_IM:
            self.X = self.fetch_byte(cycles, memory)
            self.LD_register_set_status("X")
        elif ins == INS_LDY_IM:
            self.Y = self.fetch_byte(cycles, memory)
            self.LD_register_set_status("Y")

        elif ins == INS_LDA_ZP:
            address = self.addr_zero_page(cycles, memory)
            self.load_register(cycles, memory, address, "A")
        elif ins == INS_LDX_ZP:
            address = self.addr_zero_page(cycles, memory)
            self.load_register(cycles, memory, address, "X")
        elif ins == INS_LDY_ZP:
            address = self.addr_zero_page(cycles, memory)
            self.load_register(cycles, memory, address, "Y")
        elif ins == INS_LDA_ZPX:
            address = self.addr_zero_page_x(cycles, memory)
            self.load_register(cycles, memory, address, "A")
        elif ins == INS_LDY_ZPX:
            address = self.addr_zero_page_x(cycles, memory)
            self.load_register(cycles, memory, address, "Y")
        elif ins == INS_LDX_ZPY:
            address = self.addr_zero_page_y(cycles, memory)
            self.load_register(cycles, memory, address, "X")
        elif ins == INS_LDA_ABS:
            address = self.addr_absolute(cycles, memory)
            self.load_register(cycles, memory, address, "A")
        elif ins == INS_LDX_ABS:
            address = self.addr_absolute(cycles, memory)
            self.load_register(cycles, memory, address, "X")
        elif ins == INS_LDY_ABS:
            address = self.addr_absolute(cycles, memory)
            self.load_register(cycles, memory, address, "Y")

        elif ins == INS_LDA_ABSX:
            address = self.addr_absolute_x(cycles, memory)
            self.load_register(cycles, memory, address, "A")
        elif ins == INS_LDY_ABSX:
            address = self.addr_absolute_x(cycles, memory)
            self.load_register(cycles, memory, address, "Y")

        elif ins == INS_LDA_ABSY:
            address = self.addr_absolute_y(cycles, memory)
            self.load_register(cycles, memory, address, "A")
        elif ins == INS_LDX_ABSY:
            address = self.addr_absolute_y(cycles, memory)
            self.load_register(cycles, memory, address, "X")

        elif ins == INS_LDA_INDX:
            zp_address = self.fetch_byte(cycles, memory)
            zp_address += self.X & 0xFF
            cycles -= 1
            effective_address = self.read_word(cycles, memory, zp_address)
            self.load_register(cycles, memory, effective_address, "A")
        elif ins == INS_LDA_INDY:
            zp_address = self.fetch_byte(cycles, memory)
            effective_address = self.read_word(cycles, memory, zp_address)
            effective_address_y = effective_address + self.Y & 0xFFFF
            if effective_address >> 8 != effective_address_y >> 8:  # page crossed
                cycles -= 1
            self.load_register(cycles, memory, effective_address_y, "A")
        elif ins == INS_STA_ZP:
            address = self.addr_zero_page(cycles, memory)

        elif ins == INS_JSR:
            subroutine_address = self.fetch_word(cycles, memory)
            memory.write_word( self.PC - 1, self.SP, cycles)
            self.SP += 2
            self.PC = subroutine_address
            cycles -= 1

        else:
            raise Exception("Invalid instruction: " + hex(ins))

    def execute(self, cycles : CycleCounter, memory):

        cyclesRequested = cycles.cycleCount

        while cycles.cycleCount > 0:
            self.tick(cycles, memory)

        return cyclesRequested - cycles.cycleCount
