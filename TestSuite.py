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

    def test_LDA_Imm_zero_flag(self):
        self.cpu.reset(self.mem)
        self.cpu.A = 0x44
        self.mem[0xFFFC] = INS_LDA_IM
        self.mem[0xFFFD] = 0x0

        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(2), self.mem)
        assert cyclesUsed == 2

        assert self.cpu.A == 0x0
        assert self.cpu.Z == True
        assert self.cpu.N == False
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

    def test_no_execution_given_zero_cyces(self):

        cyclesUsed = self.cpu.execute(CycleCounter(0), self.mem)
        assert cyclesUsed == 0

    def test_execute_more_cycles_if_required(self):
        self.cpu.reset(self.mem)
        self.mem[0xFFFC] = INS_LDA_IM
        self.mem[0xFFFD] = 0x84

        cyclesUsed = self.cpu.execute(CycleCounter(1), self.mem)
        assert cyclesUsed == 2

    def test_LDA_Abs(self):
        self.cpu.reset(self.mem)

        self.cpu.X = 0xFF

        self.mem[0xFFFC] = INS_LDA_ABS
        self.mem[0xFFFD] = 0x80
        self.mem[0xFFFE] = 0x44  # 0x4480
        self.mem[0x4480] = 0x37
        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(4), self.mem)
        assert cyclesUsed == 4

        assert self.cpu.A == 0x37
        assert self.cpu.Z == False
        assert self.cpu.N == False
        self.VerifyUnmodifiedFlagsLDA(cpuCopy)

    def test_LDA_Abs_X(self):
        self.cpu.reset(self.mem)

        self.cpu.X = 1

        self.mem[0xFFFC] = INS_LDA_ABSX
        self.mem[0xFFFD] = 0x80
        self.mem[0xFFFE] = 0x44
        self.mem[0x4481] = 0x37
        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(4), self.mem)
        assert cyclesUsed == 4

        assert self.cpu.A == 0x37
        assert self.cpu.Z == False
        assert self.cpu.N == False
        self.VerifyUnmodifiedFlagsLDA(cpuCopy)

    def test_LDA_Abs_X_page_crossed(self):
        self.cpu.reset(self.mem)

        self.cpu.X = 0xFF

        self.mem[0xFFFC] = INS_LDA_ABSX
        self.mem[0xFFFD] = 0x02
        self.mem[0xFFFE] = 0x44  # 0x4402
        self.mem[0x4501] = 0x37  # 0x4402 + 0xFF = page boundary crossed
        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(5), self.mem)
        assert cyclesUsed == 5

        assert self.cpu.A == 0x37
        assert self.cpu.Z == False
        assert self.cpu.N == False
        self.VerifyUnmodifiedFlagsLDA(cpuCopy)

    def test_LDA_Abs_Y(self):
        self.cpu.reset(self.mem)

        self.cpu.Y = 1

        self.mem[0xFFFC] = INS_LDA_ABSY
        self.mem[0xFFFD] = 0x80
        self.mem[0xFFFE] = 0x44  # 0x4480
        self.mem[0x4481] = 0x37
        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(4), self.mem)
        assert cyclesUsed == 4

        assert self.cpu.A == 0x37
        assert self.cpu.Z == False
        assert self.cpu.N == False
        self.VerifyUnmodifiedFlagsLDA(cpuCopy)

    def test_LDA_Abs_Y_page_crossed(self):
        self.cpu.reset(self.mem)

        self.cpu.Y = 0xFF

        self.mem[0xFFFC] = INS_LDA_ABSY
        self.mem[0xFFFD] = 0x02
        self.mem[0xFFFE] = 0x44  # 0x4402
        self.mem[0x4501] = 0x37  # 0x4402 + 0xFF = page boundary crossed
        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(5), self.mem)
        assert cyclesUsed == 5

        assert self.cpu.A == 0x37
        assert self.cpu.Z == False
        assert self.cpu.N == False
        self.VerifyUnmodifiedFlagsLDA(cpuCopy)

    def test_LDA_Ind_X(self):
        self.cpu.reset(self.mem)

        self.cpu.X = 0x04

        self.mem[0xFFFC] = INS_LDA_INDX
        self.mem[0xFFFD] = 0x02
        self.mem[0x0006] = 0x00  # 0x2 + 0x4
        self.mem[0x0007] = 0x80  # 0x8000, remember, little endian
        self.mem[0x8000] = 0x37
        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(6), self.mem)
        assert cyclesUsed == 6

        assert self.cpu.A == 0x37
        assert self.cpu.Z == False
        assert self.cpu.N == False
        self.VerifyUnmodifiedFlagsLDA(cpuCopy)

    def test_LDA_Ind_Y(self):
        self.cpu.reset(self.mem)

        self.cpu.Y = 0x04

        self.mem[0xFFFC] = INS_LDA_INDY
        self.mem[0xFFFD] = 0x02
        self.mem[0x0002] = 0x00
        self.mem[0x0003] = 0x80  # 0x8000
        self.mem[0x8004] = 0x37  # 0x8000 + 0x4
        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(5), self.mem)
        assert cyclesUsed == 5

        assert self.cpu.A == 0x37
        assert self.cpu.Z == False
        assert self.cpu.N == False
        self.VerifyUnmodifiedFlagsLDA(cpuCopy)

    def test_LDA_Ind_Y_page_crossed(self):
        self.cpu.reset(self.mem)

        self.cpu.Y = 0xFF

        self.mem[0xFFFC] = INS_LDA_INDY
        self.mem[0xFFFD] = 0x02
        self.mem[0x0002] = 0x02
        self.mem[0x0003] = 0x80  # 0x8000
        self.mem[0x8101] = 0x37  # 0x8000 + 0xFF
        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(6), self.mem)
        assert cyclesUsed == 6

        assert self.cpu.A == 0x37
        assert self.cpu.Z == False
        assert self.cpu.N == False
        self.VerifyUnmodifiedFlagsLDA(cpuCopy)

