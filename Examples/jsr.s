start:
    NOP
    CHR 'A'
    JSR printb
ret:
    CHR 'C'
    BRK

printb:
    CHR 'B'
    RTS printb
end:
