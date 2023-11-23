    NOP
int2hex:
    LOA num
    MVB 16
    LDD A/B
    LDC A%B
    LDA D
    MVB 10
    TST A-B
    JLT .digit1
    MVB 7
    LDA A+B
.digit1:
    MVB '0'
    LDA A+B
    OUT A

    MVD 10
    TST C-D
    JLT .digit2
    MVD 7
    LDC C+D
.digit2:
    MVD '0'
    LDC C+D
    OUT C

    BRK

num: db $9f