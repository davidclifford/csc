start:
    NOP
    CHR 'A'
    JSR printb
ret:
    CHR 'C'
    JSR printd
    CHR 'E'
    JSR printd
    CHR 'F'
    JSR printb
    CHR 'G'
    HLT

printb:
    CHR 'B'
    RTS printb

printd:
    CHR 'D'
    RTS printd
end:
