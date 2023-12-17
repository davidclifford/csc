import numpy as np
# 00 - 0f with carry bit (bit 0)
A1 = 0x00
Ainc = 0x01
B1 = 0x02
Binc = 0x03
A2 = 0x04
Adec = 0x05
B2 = 0x06
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

CD = 0x20
USE_CARRY = 0x40
RESERVED_FOR_LATER__NOT_IN_USE = 0x80

opcodes = {
    A1: 'A',
    Ainc: 'A+1',
    B1: 'B',
    Binc: 'B+1',
    A2: 'AA',
    Adec: 'A-1',
    B2: 'BB',
    Bdec: 'B-1',
    ApB: 'A+B',
    ApBp1: 'A+B+1',
    AmB: 'A-B',
    AmBm1: 'A-B-1',
    BmA: 'B-A',
    BmAm1: 'B-A-1',
    Zero: '0',
    One: '1',

    ABLo: 'A*B',
    ABHi: 'A*Bhi',
    AdivB: 'A/B',
    AmodB: 'A%B',
    AorB: 'A|B',
    AandB: 'A&B',
    AxorB: 'A^B',
    Adiv10B: 'AB/10',
    Amod10B: 'AB%10',
    notA: '!A',
    notB: '!B',
    negA: '-A',
    negB: '-B',

    CD | A1: 'C',
    CD | Ainc: 'C+1',
    CD | B1: 'D',
    CD | Binc: 'D+1',
    CD | A2: 'CC',
    CD | Adec: 'C-1',
    CD | B2: 'DD',
    CD | Bdec: 'D-1',
    CD | ApB: 'C+D',
    CD | ApBp1: 'C+D+1',
    CD | AmB: 'C-D',
    CD | AmBm1: 'C-D-1',
    CD | BmA: 'D-C',
    CD | BmAm1: 'D-C-1',

    CD | ABLo: 'C*D',
    CD | ABHi: 'C*Dhi',
    CD | AdivB: 'C/D',
    CD | AmodB: 'C%D',
    CD | AorB: 'C|D',
    CD | AandB: 'C&D',
    CD | AxorB: 'C^D',
    CD | Adiv10B: 'CD/10',
    CD | Amod10B: 'CD%10',
    CD | notA: '!C',
    CD | notB: '!D',
    CD | negA: '-C',
    CD | negB: '-D',

    USE_CARRY | A1: 'A+',
    USE_CARRY | B1: 'B+',
    USE_CARRY | A2: 'A-',
    USE_CARRY | B2: 'B-',
    USE_CARRY | ApB: 'A+B+',
    USE_CARRY | AmB: 'A-B-',
    USE_CARRY | BmA: 'B-A-',
    USE_CARRY | Zero: 'CY',

    USE_CARRY | CD | A1: 'C+',
    USE_CARRY | CD | B1: 'D+',
    USE_CARRY | CD | A2: 'C-',
    USE_CARRY | CD | B2: 'D-',
    USE_CARRY | CD | ApB: 'C+D+',
    USE_CARRY | CD | AmB: 'C-D-',
    USE_CARRY | CD | BmA: 'D-C-',
}

#  Generate ALU opcodes for assembler

with open('aluopcodes', 'w') as aluops_file:
    for op, mnemonic in opcodes.items():
        print(f'{op:02x} {mnemonic}')
        aluops_file.write(f'{op:02x} {mnemonic}\n')

op = ['A', 'A+1', 'B', 'B+1', 'A', 'A-1', 'B', 'B-1']
op += ['A+B', 'A+B+1', 'A-B', 'A-B-1', 'B-A', 'B-A-1', 'ZERO', 'ONE']
op += ['A*B', 'A*Bh', 'A/B', 'A%B', 'A|B', 'A&B', 'A^B', 'AB/10']
op += ['AB%10', '!A', '!B', '-A', '-B', 'Spare1', 'Spare2', 'Spare3']

FL_C = 0x100
FL_V = 0x200
FL_Z = 0x400
FL_N = 0x800

alu_rom = [0 for _ in range(256*256*32)]
alu = 0


def flags_to_string(flags):
    f = ''
    f += 'N' if flags & FL_N == FL_N else '-'
    f += 'Z' if flags & FL_Z == FL_Z else '-'
    f += 'V' if flags & FL_V == FL_V else '-'
    f += 'C' if flags & FL_C == FL_C else '-'
    return f


debug = True
if debug: debug_file = open('alu_debug', 'w')

print('Calculating ALU ops...')
for alu_op in range(32):
    for a in range(256):
        for b in range(256):
            addr = alu_op << 16 | a << 8 | b
            aa = a
            bb = b
            alu = 0
            if alu_op == A1 or alu_op == A2:
                bb = 0
                alu = a
            elif alu_op == B1 or alu_op == B2:
                aa = 0
                alu = b
            elif alu_op == Ainc:
                bb = 1
                alu = (a + 1) & 0x1ff
            elif alu_op == Adec:
                bb = 0xff
                alu = (a - 1) & 0x1ff
            elif alu_op == Binc:
                aa = 1
                alu = (b + 1) & 0x1ff
            elif alu_op == Bdec:
                aa = 0xff
                alu = (b - 1) & 0x1ff
            elif alu_op == ApB:
                alu = (a + b) & 0x1ff
            elif alu_op == AmB:
                alu = (a - b) & 0x1ff
            elif alu_op == BmA:
                alu = (b - a) & 0x1ff
            elif alu_op == ApBp1:
                alu = (a + b + 1) & 0x1ff
            elif alu_op == AmBm1:
                alu = (a - b - 1) & 0x1ff
            elif alu_op == BmAm1:
                alu = (b - a - 1) & 0x1ff
            elif alu_op == Zero:
                alu = 0
            elif alu_op == One:
                alu = 1

            elif alu_op == ABLo:
                alu = (a*b) & 0xff
                if (a*b) > 255:
                    alu |= FL_C
            elif alu_op == ABHi:
                alu = ((a*b) >> 8) & 0xff
                if alu > 0:
                    alu |= FL_C
            elif alu_op == AdivB:
                if b == 0:
                    alu = FL_V
                else:
                    alu = (a//b) & 0xff
            elif alu_op == AmodB:
                if b == 0:
                    alu = FL_V
                else:
                    alu = (a % b) & 0xff
            elif alu_op == AandB:
                alu = (a & b) & 0xff
            elif alu_op == AorB:
                alu = (a | b) & 0xff
            elif alu_op == AxorB:
                alu = (a ^ b) & 0xff
            elif alu_op == notA:
                alu = (a ^ 0xff) & 0xff
            elif alu_op == notB:
                alu = (b ^ 0xff) & 0xff
            elif alu_op == negA:
                alu = (-a) & 0xff
            elif alu_op == negB:
                alu = (-b) & 0xff

            elif alu_op == Adiv10B:
                alu = int((a + (b * 256)) // 10) & 0xff if b < 10 else 0
            elif alu_op == Amod10B:
                alu = int((a + (b * 256)) % 10) & 0xff if b < 10 else 0


# Set N, Z and V flags
            if alu & 0xff == 0:
                alu |= FL_Z
            if alu & 0x80 == 0x80:
                alu |= FL_N
            if alu_op < Zero and alu & 0x80 == 0x80 and (aa & 0x08) != 0x08 and (bb & 0x08) != 0x08:
                alu |= FL_V
            if alu_op < Zero and alu & 0x80 != 0x80 and (aa & 0x08) == 0x08 and (bb & 0x08) == 0x08:
                alu |= FL_V
            alu_rom[addr] = alu

            fl = flags_to_string(alu)
            # print(f'A={a} B={b} {op[alu_op]} = {alu&0xff} FL={fl}')
            if debug: debug_file.write(f'OP={alu_op:02x} A={a} B={b} {op[alu_op]} = {alu&0xff} FL={fl}\n')
    print(f'Calculating OP {op[alu_op]}')

if debug: debug_file.close()

print('Writing binary file to alu.bin')
with open('../Sim/alu.bin', 'wb') as rom_f:
    for b in alu_rom:
        ui16 = np.uint16(b)
        rom_f.write(ui16)

