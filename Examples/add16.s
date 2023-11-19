    NOP
start:
    MVA $F0
    MVB $7A
    LDA A+B
    MVC $12
    MVD $34
    LDC C+D+
    OUT C
    OUT A
    BRK
end: