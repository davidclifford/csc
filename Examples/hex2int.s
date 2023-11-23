    NOP
digit1:
    LOB hex1
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
    LOB hex2
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

hex1: db '0'
hex2: db '7'

org $8000
num:  db $00