#
# Generates Control files into 16-bit ROM
#

# Control signal definitions

# ALU
ZERO = 0x00
A = 0x01
B = 0x02
negA = 0x03
negB = 0x04
Ainc = 0x05
Binc = 0x06
Adec = 0x07
Bdec = 0x08
AplusB = 0x09
AplusBinc = 0x0A
AsubB = 0x0B
#    A-Bspecial = 0x0C
BsubA = 0x0D
AsubBdec = 0x0E
BsubAdec = 0x0F
AmulBlo = 0x10
AmulBhi = 0x11
AdivB = 0x12
AmodB = 0x13
#    A<<B       = 0x14
#    A>>BL      = 0x15
#    A>>BA      = 0x16
#    AROLB      = 0x17
#    ARORB      = 0x18
AandB = 0x19
AorB = 0x1A
AxorB = 0x1B
notA = 0x1C
notB = 0x1D
AdivB10 = 0x1E
AremB10 = 0x1F

# DB load
IRload = 0x01 << 5
Aload = 0x02 << 5
Bload = 0x03 << 5
Cload = 0x04 << 5
Dload = 0x05 << 5
MEMload = 0x06 << 5
AHload = 0x06 << 5
ALload = 0x06 << 5
IOload = 0x07 << 5
PCload = 0x08 << 5
Tload = 0x09 << 5
BANKload = 0x0a << 5
AH2load = 0x0b << 5
AL2load = 0x0c << 5

# DB Assert
MEMresult = 0x00 << 9
ALUresult = 0x01 << 9
IOresult = 0x02 << 9
IOctrl = 0x03 << 9
EXTresult = 0x04 << 9
KEYresult = 0x05 << 9


# Other
ARena = 1 << 12
PCinc = 1 << 13
uReset = 1 << 14
CDena = 1 << 15
Spare = 1 << 16

C = A | CDena
D = B | CDena

FL_C = 1
FL_V = 2
FL_Z = 4
FL_N = 8

FETCH = MEMresult | IRload | PCload

control = [0 for _ in range(256*16*64)]


def instruction(mnemonic, op, step, flags, cntrl):
    addr = step | op << 4 | flags << 12
    control[addr] = cntrl
    print(f'{opcode:02x} {mnemonic:<8} {flags_to_str(flags)} {step:02} {cntrl:04x} {cntrl:016b}')
    return step + 1


def flags_to_str(flags):
    if flags & FL_C == FL_C:
        f = 'C'
    else:
        f = 'c'
    if flags & FL_V == FL_V:
        f = 'V' + f
    else:
        f = 'v' + f
    if flags & FL_Z == FL_Z:
        f = 'Z' + f
    else:
        f = 'z' + f
    if flags & FL_N == FL_N:
        f = 'N' + f
    else:
        f = 'n' + f
    return f


for opcode in range(256):
    for flags in range(16):
        # First step is always FETCH
        bytes = 1
        ctrl = FETCH
        mnemonic = 'FETCH'
        step = instruction(mnemonic, opcode, 0, flags, ctrl)
        ctrl = 0
        if opcode == 0x00:
            mnemonic = 'NOP'
            step = instruction(mnemonic, opcode, step, flags, ctrl | uReset)
        elif opcode == 0x01:
            mnemonic = 'LDA 0'
            step = instruction(mnemonic, opcode, step, flags, ctrl | ZERO | ALUresult | Aload | uReset)
        elif opcode == 0x02:
            mnemonic = 'LDA B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | B | ALUresult | Aload | uReset)
        elif opcode == 0x03:
            mnemonic = 'LDA C'
            step = instruction(mnemonic, opcode, step, flags, ctrl | C | ALUresult | Aload | uReset)
        elif opcode == 0x04:
            mnemonic = 'LDA D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | D | ALUresult | Aload | uReset)
        elif opcode == 0x05:
            mnemonic = 'LDA A+1'
            step = instruction(mnemonic, opcode, step, flags, ctrl | Ainc | ALUresult | Aload | uReset)
        elif opcode == 0x06:
            mnemonic = 'LDA A-1'
            step = instruction(mnemonic, opcode, step, flags, ctrl | Adec | ALUresult | Aload | uReset)
        elif opcode == 0x07:
            mnemonic = 'LDA A+B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AplusB | ALUresult | Aload | uReset)
        elif opcode == 0x08:
            mnemonic = 'LDA A+B+'
            if flags & FL_C == FL_C:
                step = instruction(mnemonic, opcode, step, flags, ctrl | AplusBinc | ALUresult | Aload | uReset)
            else:
                step = instruction(mnemonic, opcode, step, flags, ctrl | AplusB | ALUresult | Aload | uReset)
        elif opcode == 0x09:
            mnemonic = 'LDA A-B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AsubB | ALUresult | Aload | uReset)
        elif opcode == 0x0a:
            mnemonic = 'LDA A-B-'
            if flags & FL_C == FL_C:
                step = instruction(mnemonic, opcode, step, flags, ctrl | AsubBdec | ALUresult | Aload | uReset)
            else:
                step = instruction(mnemonic, opcode, step, flags, ctrl | AsubB | ALUresult | Aload | uReset)

        else:
            mnemonic = 'Nop'
            step = instruction(mnemonic, opcode, step, flags, ctrl | uReset)
        print()



