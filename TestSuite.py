from CPU import *
import copy
class Test6502:

    mem = Memory()
    cpu = Cpu6502()

    def VerifyUnmodifiedFlagsLD_Register(self, cpuCopy):
        assert self.cpu.C == cpuCopy.C
        assert self.cpu.I == cpuCopy.I
        assert self.cpu.D == cpuCopy.D
        assert self.cpu.B == cpuCopy.B
        assert self.cpu.V == cpuCopy.V

#region base tests
    def LD_Reg_Imm(self, opcode, register):
        self.cpu.reset(self.mem)
        self.mem[0xFFFC] = opcode
        self.mem[0xFFFD] = 0x84

        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(2), self.mem)
        assert cyclesUsed == 2

        assert getattr(self.cpu, register) == 0x84
        assert self.cpu.Z == False
        assert self.cpu.N == True
        self.VerifyUnmodifiedFlagsLD_Register(cpuCopy)

    def LD_Reg_ZP(self, opcode, register):
        self.cpu.reset(self.mem)
        self.mem[0xFFFC] = opcode
        self.mem[0xFFFD] = 0x42
        self.mem[0x0042] = 0x37
        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(3), self.mem)
        assert cyclesUsed == 3

        assert getattr(self.cpu, register) == 0x37
        assert self.cpu.Z == False
        assert self.cpu.N == False
        self.VerifyUnmodifiedFlagsLD_Register(cpuCopy)

    def LD_Reg_ZPX(self, opcode, register):
        self.cpu.reset(self.mem)

        self.cpu.X = 5

        self.mem[0xFFFC] = opcode
        self.mem[0xFFFD] = 0x42
        self.mem[0x0047] = 0x37
        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(4), self.mem)
        assert cyclesUsed == 4

        assert getattr(self.cpu, register) == 0x37
        assert self.cpu.Z == False
        assert self.cpu.N == False
        self.VerifyUnmodifiedFlagsLD_Register(cpuCopy)

    def LD_Reg_ZPY(self, opcode, register):
        self.cpu.reset(self.mem)

        self.cpu.Y = 5

        self.mem[0xFFFC] = opcode
        self.mem[0xFFFD] = 0x42
        self.mem[0x0047] = 0x37
        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(4), self.mem)
        assert cyclesUsed == 4

        assert getattr(self.cpu, register) == 0x37
        assert self.cpu.Z == False
        assert self.cpu.N == False
        self.VerifyUnmodifiedFlagsLD_Register(cpuCopy)

    def LD_Reg_Abs(self, opcode, register):
        self.cpu.reset(self.mem)


        self.mem[0xFFFC] = opcode
        self.mem[0xFFFD] = 0x80
        self.mem[0xFFFE] = 0x44  # 0x4480
        self.mem[0x4480] = 0x37
        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(4), self.mem)
        assert cyclesUsed == 4

        assert getattr(self.cpu, register) == 0x37
        assert self.cpu.Z == False
        assert self.cpu.N == False
        self.VerifyUnmodifiedFlagsLD_Register(cpuCopy)

    def LD_Reg_Abs_X(self, opcode, register):
        self.cpu.reset(self.mem)

        self.cpu.X = 1

        self.mem[0xFFFC] = opcode
        self.mem[0xFFFD] = 0x80
        self.mem[0xFFFE] = 0x44
        self.mem[0x4481] = 0x37
        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(4), self.mem)
        assert cyclesUsed == 4

        assert getattr(self.cpu, register) == 0x37
        assert self.cpu.Z == False
        assert self.cpu.N == False
        self.VerifyUnmodifiedFlagsLD_Register(cpuCopy)

    def LD_Reg_Abs_Y(self, opcode, register):
        self.cpu.reset(self.mem)

        self.cpu.Y = 1

        self.mem[0xFFFC] = opcode
        self.mem[0xFFFD] = 0x80
        self.mem[0xFFFE] = 0x44  # 0x4480
        self.mem[0x4481] = 0x37
        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(4), self.mem)
        assert cyclesUsed == 4

        assert getattr(self.cpu, register) == 0x37
        assert self.cpu.Z == False
        assert self.cpu.N == False
        self.VerifyUnmodifiedFlagsLD_Register(cpuCopy)

    def LD_Reg_Abs_X_page_crossed(self, opcode, register):
        self.cpu.reset(self.mem)

        self.cpu.X = 0xFF

        self.mem[0xFFFC] = opcode
        self.mem[0xFFFD] = 0x02
        self.mem[0xFFFE] = 0x44  # 0x4402
        self.mem[0x4501] = 0x37  # 0x4402 + 0xFF = page boundary crossed
        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(5), self.mem)
        assert cyclesUsed == 5

        assert getattr(self.cpu, register) == 0x37
        assert self.cpu.Z == False
        assert self.cpu.N == False
        self.VerifyUnmodifiedFlagsLD_Register(cpuCopy)

    def LD_Reg_Abs_Y_page_crossed(self, opcode, register):
        self.cpu.reset(self.mem)

        self.cpu.Y = 0xFF

        self.mem[0xFFFC] = opcode
        self.mem[0xFFFD] = 0x02
        self.mem[0xFFFE] = 0x44  # 0x4402
        self.mem[0x4501] = 0x37  # 0x4402 + 0xFF = page boundary crossed
        cpuCopy = copy.deepcopy(self.cpu)

        cyclesUsed = self.cpu.execute(CycleCounter(5), self.mem)
        assert cyclesUsed == 5

        assert getattr(self.cpu, register) == 0x37
        assert self.cpu.Z == False
        assert self.cpu.N == False
        self.VerifyUnmodifiedFlagsLD_Register(cpuCopy)
#endregion

#region LD(r)_Imm
    def test_LDA_Imm(self):
        self.LD_Reg_Imm(INS_LDA_IM, "A")

    def test_LDX_Imm(self):
        self.LD_Reg_Imm(INS_LDX_IM, "X")

    def test_LDY_Imm(self):
        self.LD_Reg_Imm(INS_LDY_IM, "Y")
#endregion

#region LD(r)_ZP
    def test_LDA_ZP(self):
        self.LD_Reg_ZP(INS_LDA_ZP, "A")

    def test_LDX_ZP(self):
        self.LD_Reg_ZP(INS_LDX_ZP, "X")

    def test_LDY_ZP(self):
        self.LD_Reg_ZP(INS_LDY_ZP, "Y")
#endregion

#region LD(r)_ZP(X/Y)
    def test_LDA_ZPX(self):
        self.LD_Reg_ZPX(INS_LDA_ZPX, "A")

    def test_LDX_ZPY(self):
        self.LD_Reg_ZPY(INS_LDX_ZPY, "X")

    def test_LDY_ZPX(self):
        self.LD_Reg_ZPX(INS_LDY_ZPX, "Y")
#endregion

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
        self.VerifyUnmodifiedFlagsLD_Register(cpuCopy)

#region LD(r)_Abs
    def test_LDA_Abs(self):
        self.LD_Reg_Abs(INS_LDA_ABS, "A")

    def test_LDX_Abs(self):
        self.LD_Reg_Abs(INS_LDX_ABS, "X")

    def test_LDY_Abs(self):
        self.LD_Reg_Abs(INS_LDY_ABS, "Y")
#endregion

#region LD(r)_AbsX
    def test_LDA_Abs_X(self):
        self.LD_Reg_Abs_X(INS_LDA_ABSX, "A")

    def test_LDY_Abs_X(self):
        self.LD_Reg_Abs_X(INS_LDY_ABSX, "Y")
#endregion

# region LD(r)_AbsX_page_crossed
    def test_LDA_Abs_X_page_crossed(self):
        self.LD_Reg_Abs_X_page_crossed(INS_LDA_ABSX, "A")
    def test_LDY_Abs_X_page_crossed(self):
        self.LD_Reg_Abs_X_page_crossed(INS_LDY_ABSX, "Y")
#endregion

#region LD(r)_AbsY
    def test_LDA_Abs_Y(self):
        self.LD_Reg_Abs_Y(INS_LDA_ABSY, "A")

    def test_LDX_Abs_Y(self):
        self.LD_Reg_Abs_Y(INS_LDX_ABSY, "X")
#endregion

# region LD(r)_AbsY_page_crossed
    def test_LDA_Abs_Y_page_crossed(self):
        self.LD_Reg_Abs_Y_page_crossed(INS_LDA_ABSY, "A")
    def test_LDX_Abs_Y_page_crossed(self):
        self.LD_Reg_Abs_Y_page_crossed(INS_LDX_ABSY, "X")
# endregion

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
        self.VerifyUnmodifiedFlagsLD_Register(cpuCopy)

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
        self.VerifyUnmodifiedFlagsLD_Register(cpuCopy)

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
        self.VerifyUnmodifiedFlagsLD_Register(cpuCopy)

#region misc
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
        self.VerifyUnmodifiedFlagsLD_Register(cpuCopy)

    def test_no_execution_given_zero_cyces(self):

        cyclesUsed = self.cpu.execute(CycleCounter(0), self.mem)
        assert cyclesUsed == 0

    def test_execute_more_cycles_if_required(self):
        self.cpu.reset(self.mem)
        self.mem[0xFFFC] = INS_LDA_IM
        self.mem[0xFFFD] = 0x84

        cyclesUsed = self.cpu.execute(CycleCounter(1), self.mem)
        assert cyclesUsed == 2
#endregion