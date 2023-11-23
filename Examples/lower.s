# Output to lower case
    NOP
start:
    JRX .
    INA
    MVB 'A'
    TST A-B
    JGE to_lower_1
prchar:
    JTX .
    OUT A
    JMP start
to_lower_1:
    MVB '['
    TST A-B
    JLT to_lower
    JMP prchar
to_lower:
    MVB 32
    LDA A+B
    JMP prchar
halt:
    BRK