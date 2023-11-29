    NOP
digit1:
    LOB hex
    MVA $3f
    LDA A+B
    JPN A .hex
    LDA B
    JMP .digit
.hex:
    MVB $0a
    LDA A+B
.digit:
    MVB 16
    STO A*Blo num

digit2:
    LOB hex+1
    MVA $3f
    LDA A+B
    JPN A .hex
    LDA B
    JMP .digit
.hex:
    MVB $0a
    LDA A+B
.digit:
    MVB $0F
    LDB A&B
    LOA num
    LDA A|B
    STO A num

    LOA num
    OUT A
    BRK

hex: dw '45'
num: equ $f000

    EXP hex
    EXP num
