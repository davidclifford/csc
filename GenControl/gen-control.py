import numpy as np
#
# Generates Control files into 16-bit ROM
#

# Control signal definitions

# ALU OP
# 00 - 0f with carry bit (bit 0)
A = 0x00
Ainc = 0x01
B = 0x02
Binc = 0x03
A = 0x04
Adec = 0x05
B = 0x06
Bdec = 0x07
ApB = 0x08
ApBp1 = 0x09
AmB = 0x0a
AmBm1 = 0x0b
BmA = 0x0c
BmAm1 = 0x0d
Zero = 0x0e
One = 0x0f

# 10 - 1f without carry
ABLo = 0x10
ABHi = 0x11
AdivB = 0x12
AmodB = 0x13
AorB = 0x14
AandB = 0x15
AxorB = 0x16
Adiv10B = 0x17
Amod10B = 0x18
notA = 0x19
notB = 0x1a
negA = 0x1b
negB = 0x1c
spare1 = 0x1d
spare2 = 0x1e
spare3 = 0x1f

CDsel = 0x20  # AB or CD
UseCarry = 0x40
Unused = 0x80

# DB load (4-bits)
IRload = 0x01 << 0
Aload = 0x02 << 0
Bload = 0x03 << 0
Cload = 0x04 << 0
Dload = 0x05 << 0
MEMload = 0x06 << 0
AHload = 0x07 << 0
ALload = 0x08 << 0
IOload = 0x09 << 0
BANKload = 0x0a << 0
ALUopload = 0x0b << 0

# DB Assert (2-bits)
MEMresult = 0x00 << 4
ALUresult = 0x01 << 4
IOresult = 0x02 << 4
EXTresult = 0x03 << 4

# Jump Logic (3-bits)
JP_None = 0x0 << 6
JP_ALU_Z = 0x1 << 6
JP_ALU_N = 0x2 << 6
JP_Tx = 0x3 << 6
JP_Rx = 0x4 << 6
JP_Always = 0x5 << 6

# Other (9-12 spare)
ARena = 1 << 13
PCinc = 1 << 14
uReset = 1 << 15

FL_C = 1
FL_V = 2
FL_Z = 4
FL_N = 8

# Jump logic
FETCH = MEMresult | IRload | PCinc

control = [0 for _ in range(256*16*64)]


def instruction(mnemonic, op, step, flags, cntrl):
    addr = step | op << 4 | flags << 12
    cntrl ^= (ARena | uReset)  # Flip ARena and uReset as they are active low
    control[addr] = cntrl
    print(f'{opcode:02x} {mnemonic:<10} {flags_to_str(flags)} {step:02} {cntrl:04x} {cntrl:016b}')
    return step + 1


def flags_to_str(flags):
    f = ''
    f += 'N' if flags & FL_N == FL_N else '-'
    f += 'Z' if flags & FL_Z == FL_Z else '-'
    f += 'V' if flags & FL_V == FL_V else '-'
    f += 'C' if flags & FL_C == FL_C else '-'
    return f


op_f = open('opcodes', 'w')

for opcode in range(256):
    for flags in range(16):
        # First step is always FETCH
        num_bytes = 1
        aluop = 0
        ctrl = FETCH
        mnemonic = 'FETCH'
        step = instruction(mnemonic, opcode, 0, flags, ctrl)
        ctrl = 0
        if opcode == 0x00:
            mnemonic = 'NOP'
            step = instruction(mnemonic, opcode, step, flags, ctrl | uReset)
# Reg = Immediate
        elif opcode == 0x01:
            mnemonic = 'MVA'
            num_bytes = 2
            ctrl = MEMresult | PCinc | Aload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x02:
            mnemonic = 'MVB'
            num_bytes = 2
            ctrl = MEMresult | PCinc | Bload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x03:
            mnemonic = 'MVC'
            num_bytes = 2
            ctrl = MEMresult | PCinc | Cload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x04:
            mnemonic = 'MVD'
            num_bytes = 2
            ctrl = MEMresult | PCinc | Dload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x05:
            mnemonic = 'BNK'
            num_bytes = 2
            ctrl = MEMresult | PCinc | BANKload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x11:
            mnemonic = 'LDA'
            num_bytes = 2
            aluop = 1
            ctrl = MEMresult | PCinc | ALUopload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ALUresult | Aload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x12:
            mnemonic = 'LDB'
            num_bytes = 2
            aluop = 1
            ctrl = MEMresult | PCinc | ALUopload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ALUresult | Bload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x13:
            mnemonic = 'LDC'
            num_bytes = 2
            aluop = 1
            ctrl = MEMresult | PCinc | ALUopload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ALUresult | Cload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x14:
            mnemonic = 'LDD'
            num_bytes = 2
            aluop = 1
            ctrl = MEMresult | PCinc | ALUopload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ALUresult | Dload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x15:
            mnemonic = 'STO'
            num_bytes = 4
            aluop = 1
            ctrl = MEMresult | PCinc | ALUopload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ALUresult | ARena | MEMload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

# Indexed loads
        elif opcode == 0x16:
            mnemonic = 'LXA'
            num_bytes = 3
            aluop = 2
            ctrl = MEMresult | PCinc | ALUopload  # e.g. B
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ALUresult | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ARena | MEMresult | Aload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x17:
            mnemonic = 'LXB'
            num_bytes = 3
            aluop = 2
            ctrl = MEMresult | PCinc | ALUopload  # e.g. B
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ALUresult | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ARena | MEMresult | Bload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x18:
            mnemonic = 'LXC'
            num_bytes = 3
            aluop = 2
            ctrl = MEMresult | PCinc | ALUopload  # e.g. B
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ALUresult | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ARena | MEMresult | Cload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x19:
            mnemonic = 'LXD'
            num_bytes = 3
            aluop = 2
            ctrl = MEMresult | PCinc | ALUopload  # e.g. B
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ALUresult | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ARena | MEMresult | Dload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

# Indexed indirect
        elif opcode == 0x1a:
            mnemonic = 'LIA'
            num_bytes = 4
            aluop = 2
            ctrl = MEMresult | PCinc | ALUopload  # e.g. B
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | ARena | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ALUresult | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | ARena | Aload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x1b:
            mnemonic = 'LIB'
            num_bytes = 4
            aluop = 2
            ctrl = MEMresult | PCinc | ALUopload  # e.g. B
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | ARena | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ALUresult | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | ARena | Bload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x1c:
            mnemonic = 'LIC'
            num_bytes = 4
            aluop = 2
            ctrl = MEMresult | PCinc | ALUopload  # e.g. B
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | ARena | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ALUresult | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | ARena | Cload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x1d:
            mnemonic = 'LID'
            num_bytes = 4
            aluop = 2
            ctrl = MEMresult | PCinc | ALUopload  # e.g. B
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | ARena | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ALUresult | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | ARena | Dload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

# Jump instructions
        elif opcode == 0x20:
            mnemonic = 'JMP'
            num_bytes = 3
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ARena | JP_Always | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x21:
            mnemonic = 'JTX'
            num_bytes = 3
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ARena | JP_Tx | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x22:
            mnemonic = 'JRX'
            num_bytes = 3
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ARena | JP_Rx | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x23:
            mnemonic = 'JPZ'  # e.g. JPZ A ot JPZ D
            aluop = 1
            num_bytes = 4
            ctrl = MEMresult | PCinc | ALUopload # [A,B], [AB,CD]
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ARena | ALUresult | JP_ALU_Z | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x24:
            mnemonic = 'JPN'  # e.g. JPN A ot JPN D
            aluop = 1
            num_bytes = 4
            ctrl = MEMresult | PCinc | ALUopload # [A,B], [AB,CD]
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ARena | ALUresult | JP_ALU_N | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x25:
            mnemonic = 'JEQ'  # Jump if result is Zero
            aluop = 1
            num_bytes = 4
            ctrl = MEMresult | PCinc | ALUopload  # A-B or B-A etc
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            if flags & FL_Z == FL_Z:
                ctrl = ARena | JP_Always | uReset
            else:
                ctrl = uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x26:
            mnemonic = 'JNE'  # Jump if result is Not Zero
            aluop = 1
            num_bytes = 4
            ctrl = MEMresult | PCinc | ALUopload  # A-B or B-A etc
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            if flags & FL_Z == FL_Z:
                ctrl = uReset
            else:
                ctrl = ARena | JP_Always | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x27:
            mnemonic = 'JGE'  # Jump if no carry
            aluop = 1
            num_bytes = 4
            ctrl = MEMresult | PCinc | ALUopload  # A-B or B-A etc
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            if flags & FL_C == FL_C:
                ctrl = uReset
            else:
                ctrl = ARena | JP_Always | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x28:
            mnemonic = 'JLT'  # Jump if carry
            aluop = 1
            num_bytes = 4
            ctrl = MEMresult | PCinc | ALUopload  # A-B or B-A etc
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            if flags & FL_C == FL_C:
                ctrl = ARena | JP_Always | uReset
            else:
                ctrl = uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x29:
            mnemonic = 'JPN'  # Jump if negative
            aluop = 1
            num_bytes = 4
            ctrl = MEMresult | PCinc | ALUopload  # A-B or B-A etc
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            if flags & FL_N == FL_N:
                ctrl = ARena | JP_Always | uReset
            else:
                ctrl = uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x2a:
            mnemonic = 'JPP'  # Jump if positive
            aluop = 1
            num_bytes = 4
            ctrl = MEMresult | PCinc | ALUopload  # A-B or B-A etc
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            if flags & FL_N == FL_N:
                ctrl = uReset
            else:
                ctrl = ARena | JP_Always | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x2b:
            mnemonic = 'JPV'  # Jump if overflow
            aluop = 1
            num_bytes = 4
            ctrl = MEMresult | PCinc | ALUopload  # A-B or B-A etc
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            if flags & FL_V == FL_V:
                ctrl = ARena | JP_Always | uReset
            else:
                ctrl = uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x2a:
            mnemonic = 'JNV'  # Jump if no overflow
            aluop = 1
            num_bytes = 4
            ctrl = MEMresult | PCinc | ALUopload  # A-B or B-A etc
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            if flags & FL_V == FL_V:
                ctrl = uReset
            else:
                ctrl = ARena | JP_Always | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)


# I/O in Register
        elif opcode == 0x30:
            mnemonic = 'INA'
            ctrl = IOresult | Aload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x31:
            mnemonic = 'INB'
            ctrl = IOresult | Aload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x32:
            mnemonic = 'INC'
            ctrl = IOresult | Aload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x33:
            mnemonic = 'IND'
            ctrl = IOresult | Aload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)
# I/O in Memory
        elif opcode == 0x34:
            mnemonic = 'INM'
            num_bytes = 3
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = IOresult | ARena | MEMload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)
# I/O out ALU op
        elif opcode == 0x35:
            mnemonic = 'OUT'
            num_bytes = 2
            aluop = 1
            ctrl = MEMresult | PCinc | ALUopload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ALUresult | IOload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

# I/O out immediate
        elif opcode == 0x36:
            mnemonic = 'CHR'
            num_bytes = 2
            ctrl = MEMresult | PCinc | IOload | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0xff:
            mnemonic = 'BRK'
            ctrl = uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

# JSR and RTS
        elif opcode == 0x40:
            mnemonic = 'JSR'  # 12 steps - destroys D
            num_bytes = 9 # OP stklow stkhi pclow alu=D stklow+1 pchi jplo jhi
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | Dload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALUopload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ARena | ALUresult | MEMload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | Dload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ARena | ALUresult | MEMload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ARena | JP_Always | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        elif opcode == 0x41:
            mnemonic = 'RTS' # 11 Steps - destroys C and D
            num_bytes = 6  # OP stklo stkhi stklo+1 ALU=D ALU=C
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ARena | MEMresult | Dload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ARena | MEMresult | Cload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALUopload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ALUresult | ALload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = MEMresult | PCinc | ALUopload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ALUresult | AHload
            step = instruction(mnemonic, opcode, step, flags, ctrl)
            ctrl = ARena | JP_Always | uReset
            step = instruction(mnemonic, opcode, step, flags, ctrl)

        # Unused op, set to Pseudo NOP
        else:
            mnemonic = f'X{opcode:02x}'
            step = instruction(mnemonic, opcode, step, flags, ctrl | uReset)
        print()

    op_f.write(f'{opcode:02x} {mnemonic} {aluop} {num_bytes}\n')
op_f.close()

with open('../Sim/control.bin', 'wb') as rom_f:
    for b in control:
        ui16 = np.uint16(b)
        rom_f.write(ui16)

