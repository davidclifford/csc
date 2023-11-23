    NOP
    MVC 0
start:
    MVA 119
    STO A y
yloop:
    MVB 159
xloop:
    STX C y B
    LDB B-1
    JGE xloop
    LOB y
    STO B-1 y
    JGE yloop
wait:
    LDC C+1
    INA
    JPZ A wait
    MVB 'q'
    JPZ A-B end
    JMP start
end:
    BRK

    org $8000
y: DB 0
