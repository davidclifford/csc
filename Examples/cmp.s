    NOP
    MVA 42
    MVB 42
    TST A-B
    JEQ equal
    JNE notequal
    CHR '-'
    BRK
equal:
    CHR 'Y'
    BRK
notequal:
    CHR 'N'
    BRK

