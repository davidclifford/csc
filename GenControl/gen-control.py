#
# Generates Control files into 16-bit ROM
#
from enum import Enum


class ALUop(Enum):
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


class DBLoad(Enum):
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


class DBAssert(Enum):
    MEMresult = 0x00 << 9
    ALUresult = 0x01 << 9
    IOresult = 0x02 << 9
    EXTreult = 0x03 << 9


class Other(Enum):
    ARena = 1 << 11
    PCinc = 1 << 12
    uReset = 1 << 13
    CDena = 1 << 14
    Spare = 1 << 15


print(f'{ALUop.AremB10.value:016b}')
print(f'{DBLoad.IRload.value:016b}')
print(f'{DBLoad.IOload.value:016b}')
print(f'{DBLoad.AL2load.value:016b}')
print(f'{DBAssert.EXTreult.value:016b}')
print(f'{Other.ARena.value:016b}')
print(f'{Other.PCinc.value:016b}')
print(f'{Other.uReset.value:016b}')
print(f'{Other.CDena.value:016b}')
print(f'{Other.Spare.value:016b}')


