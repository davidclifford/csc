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
    print(f'{opcode:02x} {mnemonic:<10} {flags_to_str(flags)} {step:02} {cntrl:04x} {cntrl:016b}')
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

# A reg
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
        elif opcode == 0x0b:
            mnemonic = 'LDA A*BH'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AmulBhi | ALUresult | Aload | uReset)
        elif opcode == 0x0c:
            mnemonic = 'LDA A*BL'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AmulBlo | ALUresult | Aload | uReset)
        elif opcode == 0x0d:
            mnemonic = 'LDA A/B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AdivB | ALUresult | Aload | uReset)
        elif opcode == 0x0e:
            mnemonic = 'LDA A%B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AmodB | ALUresult | Aload | uReset)
        elif opcode == 0x0f:
            mnemonic = 'LDA A&B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AandB | ALUresult | Aload | uReset)
        elif opcode == 0x10:
            mnemonic = 'LDA A|B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AorB | ALUresult | Aload | uReset)
        elif opcode == 0x11:
            mnemonic = 'LDA A^B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AxorB | ALUresult | Aload | uReset)
        elif opcode == 0x12:
            mnemonic = 'LDA ADIVB'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AdivB10 | ALUresult | Aload | uReset)
        elif opcode == 0x13:
            mnemonic = 'LDA AREMB'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AremB10 | ALUresult | Aload | uReset)
        elif opcode == 0x14:
            mnemonic = 'LDA -A'
            step = instruction(mnemonic, opcode, step, flags, ctrl | negA | ALUresult | Aload | uReset)
        elif opcode == 0x15:
            mnemonic = 'LDA !A'
            step = instruction(mnemonic, opcode, step, flags, ctrl | notA | ALUresult | Aload | uReset)
        elif opcode == 0x16:
            mnemonic = 'LDA A+1+'
            if flags & FL_C == FL_C:
                step = instruction(mnemonic, opcode, step, flags, ctrl | Ainc | ALUresult | Aload | uReset)
            else:
                step = instruction(mnemonic, opcode, step, flags, ctrl | A | ALUresult | Aload | uReset)
        elif opcode == 0x17:
            mnemonic = 'LDA A-1-'
            if flags & FL_C == FL_C:
                step = instruction(mnemonic, opcode, step, flags, ctrl | Adec | ALUresult | Aload | uReset)
            else:
                step = instruction(mnemonic, opcode, step, flags, ctrl | A | ALUresult | Aload | uReset)

# B reg
        elif opcode == 0x21:
            mnemonic = 'LDB 0'
            step = instruction(mnemonic, opcode, step, flags, ctrl | ZERO | ALUresult | Bload | uReset)
        elif opcode == 0x22:
            mnemonic = 'LDB A'
            step = instruction(mnemonic, opcode, step, flags, ctrl | A | ALUresult | Bload | uReset)
        elif opcode == 0x23:
            mnemonic = 'LDB C'
            step = instruction(mnemonic, opcode, step, flags, ctrl | C | ALUresult | Bload | uReset)
        elif opcode == 0x24:
            mnemonic = 'LDB D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | D | ALUresult | Bload | uReset)
        elif opcode == 0x25:
            mnemonic = 'LDB B+1'
            step = instruction(mnemonic, opcode, step, flags, ctrl | Binc | ALUresult | Bload | uReset)
        elif opcode == 0x26:
            mnemonic = 'LDB B-1'
            step = instruction(mnemonic, opcode, step, flags, ctrl | Bdec | ALUresult | Bload | uReset)
        elif opcode == 0x27:
            mnemonic = 'LDB A+B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AplusB | ALUresult | Bload | uReset)
        elif opcode == 0x28:
            mnemonic = 'LDB A+B+'
            if flags & FL_C == FL_C:
                step = instruction(mnemonic, opcode, step, flags, ctrl | AplusBinc | ALUresult | Bload | uReset)
            else:
                step = instruction(mnemonic, opcode, step, flags, ctrl | AplusB | ALUresult | Bload | uReset)
        elif opcode == 0x29:
            mnemonic = 'LDB B-A'
            step = instruction(mnemonic, opcode, step, flags, ctrl | BsubA | ALUresult | Bload | uReset)
        elif opcode == 0x2a:
            mnemonic = 'LDB B-A-'
            if flags & FL_C == FL_C:
                step = instruction(mnemonic, opcode, step, flags, ctrl | BsubAdec | ALUresult | Bload | uReset)
            else:
                step = instruction(mnemonic, opcode, step, flags, ctrl | BsubA | ALUresult | Bload | uReset)
        elif opcode == 0x2b:
            mnemonic = 'LDB A*BH'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AmulBhi | ALUresult | Bload | uReset)
        elif opcode == 0x2c:
            mnemonic = 'LDB A*BL'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AmulBlo | ALUresult | Bload | uReset)
        elif opcode == 0x2d:
            mnemonic = 'LDB A/B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AdivB | ALUresult | Bload | uReset)
        elif opcode == 0x2e:
            mnemonic = 'LDB A%B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AmodB | ALUresult | Bload | uReset)
        elif opcode == 0x2f:
            mnemonic = 'LDB A&B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AandB | ALUresult | Bload | uReset)
        elif opcode == 0x30:
            mnemonic = 'LDB A|B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AorB | ALUresult | Bload | uReset)
        elif opcode == 0x31:
            mnemonic = 'LDB A^B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AxorB | ALUresult | Bload | uReset)
        elif opcode == 0x32:
            mnemonic = 'LDB ADIVB'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AdivB10 | ALUresult | Bload | uReset)
        elif opcode == 0x33:
            mnemonic = 'LDB AREMB'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AremB10 | ALUresult | Bload | uReset)
        elif opcode == 0x34:
            mnemonic = 'LDB -B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | negB | ALUresult | Bload | uReset)
        elif opcode == 0x35:
            mnemonic = 'LDB !B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | notB | ALUresult | Bload | uReset)
        elif opcode == 0x36:
            mnemonic = 'LDB B+1+'
            if flags & FL_C == FL_C:
                step = instruction(mnemonic, opcode, step, flags, ctrl | Binc | ALUresult | Bload | uReset)
            else:
                step = instruction(mnemonic, opcode, step, flags, ctrl | B | ALUresult | Bload | uReset)
        elif opcode == 0x37:
            mnemonic = 'LDB B-1-'
            if flags & FL_C == FL_C:
                step = instruction(mnemonic, opcode, step, flags, ctrl | Bdec | ALUresult | Bload | uReset)
            else:
                step = instruction(mnemonic, opcode, step, flags, ctrl | B | ALUresult | Bload | uReset)

# C reg
        elif opcode == 0x41:
            mnemonic = 'LDC 0'
            step = instruction(mnemonic, opcode, step, flags, ctrl | ZERO | ALUresult | Cload | uReset)
        elif opcode == 0x42:
            mnemonic = 'LDC B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | B | ALUresult | Cload | uReset)
        elif opcode == 0x43:
            mnemonic = 'LDC A'
            step = instruction(mnemonic, opcode, step, flags, ctrl | A | ALUresult | Cload | uReset)
        elif opcode == 0x44:
            mnemonic = 'LDC D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | D | ALUresult | Cload | uReset)
        elif opcode == 0x45:
            mnemonic = 'LDC C+1'
            step = instruction(mnemonic, opcode, step, flags, ctrl | Ainc | CDena | ALUresult | Cload | uReset)
        elif opcode == 0x46:
            mnemonic = 'LDC C-1'
            step = instruction(mnemonic, opcode, step, flags, ctrl | Adec | CDena | ALUresult | Cload | uReset)
        elif opcode == 0x47:
            mnemonic = 'LDC C+D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AplusB | CDena | ALUresult | Cload | uReset)
        elif opcode == 0x48:
            mnemonic = 'LDC C+D+'
            if flags & FL_C == FL_C:
                step = instruction(mnemonic, opcode, step, flags, ctrl | AplusBinc | CDena | ALUresult | Cload | uReset)
            else:
                step = instruction(mnemonic, opcode, step, flags, ctrl | AplusB | CDena | ALUresult | Cload | uReset)
        elif opcode == 0x49:
            mnemonic = 'LDC C-D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AsubB | CDena | ALUresult | Cload | uReset)
        elif opcode == 0x4a:
            mnemonic = 'LDC C-D-'
            if flags & FL_C == FL_C:
                step = instruction(mnemonic, opcode, step, flags, ctrl | AsubBdec | CDena | ALUresult | Cload | uReset)
            else:
                step = instruction(mnemonic, opcode, step, flags, ctrl | AsubB | CDena | ALUresult | Cload | uReset)
        elif opcode == 0x4b:
            mnemonic = 'LDC C*DH'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AmulBhi | CDena | ALUresult | Cload | uReset)
        elif opcode == 0x4c:
            mnemonic = 'LDC C*DL'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AmulBlo | CDena | ALUresult | Cload | uReset)
        elif opcode == 0x4d:
            mnemonic = 'LDC C/D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AdivB | CDena | ALUresult | Cload | uReset)
        elif opcode == 0x4e:
            mnemonic = 'LDC C%D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AmodB | CDena | ALUresult | Cload | uReset)
        elif opcode == 0x4f:
            mnemonic = 'LDC C&D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AandB | CDena | ALUresult | Cload | uReset)
        elif opcode == 0x50:
            mnemonic = 'LDC C|D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AorB | CDena | ALUresult | Cload | uReset)
        elif opcode == 0x51:
            mnemonic = 'LDC C^D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AxorB | CDena | ALUresult | Cload | uReset)
        elif opcode == 0x52:
            mnemonic = 'LDC CDIVD'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AdivB10 | CDena | ALUresult | Cload | uReset)
        elif opcode == 0x53:
            mnemonic = 'LDC CREMD'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AremB10 | CDena | ALUresult | Cload | uReset)
        elif opcode == 0x54:
            mnemonic = 'LDC -C'
            step = instruction(mnemonic, opcode, step, flags, ctrl | negA | CDena | ALUresult | Cload | uReset)
        elif opcode == 0x55:
            mnemonic = 'LDC !C'
            step = instruction(mnemonic, opcode, step, flags, ctrl | notA | CDena | ALUresult | Cload | uReset)
        elif opcode == 0x56:
            mnemonic = 'LDC C+1+'
            if flags & FL_C == FL_C:
                step = instruction(mnemonic, opcode, step, flags, ctrl | Ainc | CDena | ALUresult | Aload | uReset)
            else:
                step = instruction(mnemonic, opcode, step, flags, ctrl | A | CDena | ALUresult | Aload | uReset)
        elif opcode == 0x57:
            mnemonic = 'LDC C-1-'
            if flags & FL_C == FL_C:
                step = instruction(mnemonic, opcode, step, flags, ctrl | Adec | CDena | ALUresult | Aload | uReset)
            else:
                step = instruction(mnemonic, opcode, step, flags, ctrl | A | CDena | ALUresult | Aload | uReset)
# D reg
        elif opcode == 0x61:
            mnemonic = 'LDD 0'
            step = instruction(mnemonic, opcode, step, flags, ctrl | ZERO | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x62:
            mnemonic = 'LDD A'
            step = instruction(mnemonic, opcode, step, flags, ctrl | A | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x63:
            mnemonic = 'LDD B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | B | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x64:
            mnemonic = 'LDD C'
            step = instruction(mnemonic, opcode, step, flags, ctrl | C | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x65:
            mnemonic = 'LDD D+1'
            step = instruction(mnemonic, opcode, step, flags, ctrl | Binc | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x66:
            mnemonic = 'LDD D-1'
            step = instruction(mnemonic, opcode, step, flags, ctrl | Bdec | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x67:
            mnemonic = 'LDD C+D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AplusB | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x68:
            mnemonic = 'LDD C+D+'
            if flags & FL_C == FL_C:
                step = instruction(mnemonic, opcode, step, flags, ctrl | AplusBinc | CDena | ALUresult | Dload | uReset)
            else:
                step = instruction(mnemonic, opcode, step, flags, ctrl | AplusB | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x69:
            mnemonic = 'LDD D-C'
            step = instruction(mnemonic, opcode, step, flags, ctrl | BsubA | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x6a:
            mnemonic = 'LDD D-C-'
            if flags & FL_C == FL_C:
                step = instruction(mnemonic, opcode, step, flags, ctrl | BsubAdec | CDena | ALUresult | Dload | uReset)
            else:
                step = instruction(mnemonic, opcode, step, flags, ctrl | BsubA | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x6b:
            mnemonic = 'LDD D*CH'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AmulBhi | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x6c:
            mnemonic = 'LDD D*CL'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AmulBlo | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x6d:
            mnemonic = 'LDD C/D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AdivB | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x6e:
            mnemonic = 'LDD C%D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AmodB | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x6f:
            mnemonic = 'LDD C&D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AandB | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x70:
            mnemonic = 'LDD C|D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AorB | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x71:
            mnemonic = 'LDD C^D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AxorB | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x72:
            mnemonic = 'LDD CDIVD'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AdivB10 | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x73:
            mnemonic = 'LDD CREMD'
            step = instruction(mnemonic, opcode, step, flags, ctrl | AremB10 | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x74:
            mnemonic = 'LDD -D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | negB | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x75:
            mnemonic = 'LDD !D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | notB | CDena | ALUresult | Dload | uReset)
        elif opcode == 0x76:
            mnemonic = 'LDD D+1+'
            if flags & FL_C == FL_C:
                step = instruction(mnemonic, opcode, step, flags, ctrl | Binc | CDena | ALUresult | Bload | uReset)
            else:
                step = instruction(mnemonic, opcode, step, flags, ctrl | B | CDena | ALUresult | Bload | uReset)
        elif opcode == 0x77:
            mnemonic = 'LDD D-1-'
            if flags & FL_C == FL_C:
                step = instruction(mnemonic, opcode, step, flags, ctrl | Bdec | CDena | ALUresult | Bload | uReset)
            else:
                step = instruction(mnemonic, opcode, step, flags, ctrl | B | CDena | ALUresult | Bload | uReset)
# A op B -> MEM
        elif opcode == 0x80:
            mnemonic = 'STO 0'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | ZERO | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x81:
            mnemonic = 'STO A'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | A | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x82:
            mnemonic = 'STO B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | B | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x83:
            mnemonic = 'STO C'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | C | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x84:
            mnemonic = 'STO D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | D | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x85:
            mnemonic = 'STO A+1'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | Ainc | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x86:
            mnemonic = 'STO A-1'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | Adec | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x87:
            mnemonic = 'STO A+B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AplusB | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x88:
            mnemonic = 'STO A+B+'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            if flags & FL_C == FL_C:
                step = instruction(mnemonic, opcode, step, flags, ctrl | AplusBinc | ALUresult | MEMload | ARena | uReset)
            else:
                step = instruction(mnemonic, opcode, step, flags, ctrl | AplusB | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x89:
            mnemonic = 'STO A-B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AsubB | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x8a:
            mnemonic = 'STO A-B-'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            if flags & FL_C == FL_C:
                step = instruction(mnemonic, opcode, step, flags, ctrl | AsubBdec | ALUresult | MEMload | ARena | uReset)
            else:
                step = instruction(mnemonic, opcode, step, flags, ctrl | AsubB | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x8b:
            mnemonic = 'STO A*BH'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AmulBhi | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x8c:
            mnemonic = 'STO A*BL'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AmulBlo | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x8d:
            mnemonic = 'STO A/B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AdivB | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x8e:
            mnemonic = 'STO A%B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AmodB | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x8f:
            mnemonic = 'STO A&B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AandB | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x90:
            mnemonic = 'STO A|B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AorB | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x91:
            mnemonic = 'STO A^B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AxorB | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x92:
            mnemonic = 'STO ADIVB'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AdivB10 | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x93:
            mnemonic = 'STO AREMB'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AremB10 | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x94:
            mnemonic = 'STO -A'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | negA | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0x95:
            mnemonic = 'STO !A'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | notA | ALUresult | MEMload | ARena | uReset)

# C op D -> MEM
        elif opcode == 0xa0:
            mnemonic = 'STO -D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | negB | CDena | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0xa1:
            mnemonic = 'STO !D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | notB | CDena | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0xa2:
            mnemonic = 'STO D+1'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | Binc | CDena | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0xa3:
            mnemonic = 'STO D-1'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | Bdec | CDena | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0xa5:
            mnemonic = 'STO C+1'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | Ainc | CDena | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0xa6:
            mnemonic = 'STO C-1'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | Adec | CDena | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0xa7:
            mnemonic = 'STO C+D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AplusB | CDena | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0xa8:
            mnemonic = 'STO C+D+'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            if flags & FL_C == FL_C:
                step = instruction(mnemonic, opcode, step, flags, ctrl | AplusBinc | CDena | ALUresult | MEMload | ARena | uReset)
            else:
                step = instruction(mnemonic, opcode, step, flags, ctrl | AplusB | CDena | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0xa9:
            mnemonic = 'STO C-D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AsubB | CDena | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0xaa:
            mnemonic = 'STO C-D-'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            if flags & FL_C == FL_C:
                step = instruction(mnemonic, opcode, step, flags, ctrl | AsubBdec | CDena | ALUresult | MEMload | ARena | uReset)
            else:
                step = instruction(mnemonic, opcode, step, flags, ctrl | AsubB | CDena | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0xab:
            mnemonic = 'STO C*BH'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AmulBhi | CDena | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0xac:
            mnemonic = 'STO C*BL'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AmulBlo | CDena | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0xad:
            mnemonic = 'STO C/D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AdivB | CDena | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0xae:
            mnemonic = 'STO C%D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AmodB | CDena | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0xaf:
            mnemonic = 'STO C&D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AandB | CDena | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0xb0:
            mnemonic = 'STO C|D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AorB | CDena | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0xb1:
            mnemonic = 'STO C^D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AxorB | CDena | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0xb2:
            mnemonic = 'STO CDIVD'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AdivB10 | CDena | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0xb3:
            mnemonic = 'STO CREMD'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | AremB10 | CDena | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0xb4:
            mnemonic = 'STO -C'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | negA | CDena | ALUresult | MEMload | ARena | uReset)
        elif opcode == 0xb5:
            mnemonic = 'STO !C'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | notA | CDena | ALUresult | MEMload | ARena | uReset)
# Load constants
        elif opcode == 0xc0:
            mnemonic = 'MOV A'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | Aload | PCinc | uReset)
        elif opcode == 0xc1:
            mnemonic = 'MOV B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | Bload | PCinc | uReset)
        elif opcode == 0xc2:
            mnemonic = 'MOV C'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | Cload | PCinc | uReset)
        elif opcode == 0xc3:
            mnemonic = 'MOV D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | Dload | PCinc | uReset)
# Load from abs address
        elif opcode == 0xc4:
            mnemonic = 'LDA'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | Aload | PCinc | uReset)
        elif opcode == 0xc5:
            mnemonic = 'LDB'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | Bload | PCinc | uReset)
        elif opcode == 0xc6:
            mnemonic = 'LDC'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | Cload | PCinc | uReset)
        elif opcode == 0xc7:
            mnemonic = 'LDD'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | Dload | PCinc | uReset)

# Load from index address
        elif opcode == 0xc8:
            mnemonic = 'LDA_,B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ARena | AHload)
            step = instruction(mnemonic, opcode, step, flags, ctrl | ALUresult | B | ARena | ALload)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ARena | Aload | uReset)
        elif opcode == 0xc9:
            mnemonic = 'LDB_,B'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ARena | AHload)
            step = instruction(mnemonic, opcode, step, flags, ctrl | ALUresult | B | ARena | ALload)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ARena | Bload | uReset)
        elif opcode == 0xca:
            mnemonic = 'LDC_,D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ARena | AHload)
            step = instruction(mnemonic, opcode, step, flags, ctrl | ALUresult | B | CDena | ARena | ALload)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ARena | Cload | uReset)
        elif opcode == 0xcb:
            mnemonic = 'LDD_,D'
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ALload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | AHload | PCinc)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ARena | AHload)
            step = instruction(mnemonic, opcode, step, flags, ctrl | ALUresult | B | CDena | ARena | ALload)
            step = instruction(mnemonic, opcode, step, flags, ctrl | MEMresult | ARena | Dload | uReset)

# Unused op, set to Pseudo NOP
        else:
            mnemonic = 'nop'
            step = instruction(mnemonic, opcode, step, flags, ctrl | uReset)
        print()



