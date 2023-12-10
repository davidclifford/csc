# Monitor ROM for the Clifford Small Computer
# 2nd Dec 20223
# Inspired by Warren Toomey's CSCvon8
main:
    db (6)
reset:
    MVB welcome
.loop:
    LXA >welcome,B
    JPZ A prompt
    OUT A LDB B+1
    JMP .loop
prompt:
    CHR '>'
    CHR ' '
    MVD cmdline
.key:
    INA
    JPZ A .key
    MVB 8
    TST A-B
    JEQ .bs
    OUT A
    STI A cmdline,D
    LDD D+1
    MVB '\n'
    TST A-B
    JNE .key
    JMP do_command
.bs:
    MVC cmdline
    TST C-D
    JEQ .key
    CHR 8
    CHR ' '
    CHR 8
    LDD D-1
    JMP .key

# Do commands
do_command:
    LOA cmdline
# New line
    MVB '\n'
    TST A-B
    JEQ prompt
# Help ?
    MVB '?'
    TST A-B
    JEQ usage_cmd
# Letter command (change to lower case)
    MVB $20
    LDA A|B
# C Change
    MVB 'c'
    TST A-B
    JEQ change_command
# D Dump
    MVB 'd'
    TST A-B
    JEQ dump_command
# V Video Dump
    MVB 'v'
    TST A-B
    JEQ video_command
# R Run
    MVB 'r'
    TST A-B
    JEQ run_command
# X eXit command
    MVB 'x'
    TST A-B
    JEQ reset
    JMP prompt

change_command:
    STO 0 __addr
    STO 0 __addr+1
    MVD cmdline
    LDD D+1
    LXA >cmdline,D
    STO A __hex
    LDD D+1
    LXA >cmdline,D
    STO A __hex+1
    LDD D+1
    LXA >cmdline,D
    STO A __hex+2
    LDD D+1
    LXA >cmdline,D
    STO A __hex+3
;    JSR Hex2Int16
; Store addess
    LOA __num
    STO A __addr
    LOA __num+1
    STO A __addr+1
; Read in bytes and store at address
.loop:
    JRX .
    INA
    JTX .
    OUT A
    MVB '!'
    TST A-B
    JLT .loop
    MVB 'Z'
    TST A-B
    JEQ .end
    MVB 'z'
    TST A-B
    JEQ .end
    STO A __hex
.loop1:
    JRX .
    INA
    JTX .
    OUT A
    MVB '!'
    TST A-B
    JLT .loop1
    MVB 'Z'
    TST A-B
    JEQ .end
    MVB 'z'
    TST A-B
    JEQ .end
    STO A __hex+1
; Convert Hex to Byte
;    JSR Hex2Int8
; Store number in mem poined to by __addr (little endian)
    LOA __num
    LOB __addr
    STX A __addr+1,B
.next:
    LOA __addr
    LOB __addr+1
    STO A+1 __addr
    STO B+ __addr+1
    JMP .loop
.end:
    JMP prompt

dump_command:
    CHR 'D'
    JMP prompt
video_command:
    CHR 'V'
    JMP prompt
run_command:
    CHR 'R'
    JMP prompt
usage_cmd:
    MVB usage
.loop:
    LXA >usage B
    JPZ A prompt
    JRX .
    OUT A
    LDB B+1
    JMP .loop

Hex2Int16:
    RTS Hex2Int16
Hex2Int8:
;    RTS Hex2Int8

endprg:

PAG
welcome: db "\e[2J\e[HCSC Monitor, Revision: 1.00, 02/12/2023\nType ? for help\n"
usage: db "Usage: D dump, V video dump, C change, R run, X clear/reset, ? help\n"

ORG $FC00
cmdline: db (16)
__addr: dw
__hex: db (4)
__int16: dw
__num: db

exp prompt
