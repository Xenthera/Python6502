from CPU import *
import copy
class Test6502:

    mem = Memory()
    cpu = Cpu6502()

    def VerifyUnmodifiedFlagsLDA(self, cpuCopy):
        assert self.cpu.C == cpuCopy.C
        assert self.cpu.I == cpuCopy.I
        assert self.cpu.D == cpuCopy.D
        assert self.cpu.B == cpuCopy.B
        assert self.cpu.V == cpuCopy.V

    def test_LDA_Imm(self):
        self.cpu.reset(self.mem)
        self.mem[0xFFFC] = INS_LDA_IM
        self.mem[0xFFFD] = 0x84

        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(2), self.mem)
        assert cyclesUsed == 2

        assert self.cpu.A == 0x84
        assert self.cpu.Z == False
        assert self.cpu.N == True
        self.VerifyUnmodifiedFlagsLDA(cpuCopy)


    def test_LDA_ZP(self):
        self.cpu.reset(self.mem)
        self.mem[0xFFFC] = INS_LDA_ZP
        self.mem[0xFFFD] = 0x42
        self.mem[0x0042] = 0x37
        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(3), self.mem)
        assert cyclesUsed == 3

        assert self.cpu.A == 0x37
        assert self.cpu.Z == False
        assert self.cpu.N == False
        self.VerifyUnmodifiedFlagsLDA(cpuCopy)

    def test_LDA_ZPX(self):
        self.cpu.reset(self.mem)

        self.cpu.X = 5

        self.mem[0xFFFC] = INS_LDA_ZPX
        self.mem[0xFFFD] = 0x42
        self.mem[0x0047] = 0x37
        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(4), self.mem)
        assert cyclesUsed == 4

        assert self.cpu.A == 0x37
        assert self.cpu.Z == False
        assert self.cpu.N == False
        self.VerifyUnmodifiedFlagsLDA(cpuCopy)

    def test_LDA_ZPX_Wrap(self):
        self.cpu.reset(self.mem)

        self.cpu.X = 0xFF

        self.mem[0xFFFC] = INS_LDA_ZPX
        self.mem[0xFFFD] = 0x80
        self.mem[0x007F] = 0x37
        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(4), self.mem)
        assert cyclesUsed == 4

        assert self.cpu.A == 0x37
        assert self.cpu.Z == False
        assert self.cpu.N == False
        self.VerifyUnmodifiedFlagsLDA(cpuCopy)



