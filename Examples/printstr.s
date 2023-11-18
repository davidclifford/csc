    ORG $0000
start:
    NOP              0000 00
next:
    MVB string       0001 02 16
.loop:
    LXA >string,B    0003 16 02 00
    JPZ A .finish    0006 23 00 11 00
    OUT A            000a 35 00
    LDB B+1          000c 12 03
    JMP .loop        000e 20 03 00
.finish:
    JTX .
    CHR 10           0011 36 0a
    JMP next         0013 20 01 00

string: DB "Hello, World!" 0016
end:
    NOP