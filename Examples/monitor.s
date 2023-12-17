# Monitor ROM for the Clifford Small Computer
# 2nd Dec 20223
# Inspired by Warren Toomey's CSCvon8
main:
    db (6)
reset:
    MVB welcome
.loop:
    LXA >welcome,B
    JPZ A Prompt
    OUT A LDB B+1
    JMP .loop
Prompt:
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
    STX A cmdline,D
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
    JEQ Prompt
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
    JMP Prompt

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
    JSR Hex2Int16
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
    JSR Hex2Int8
; Store number in mem poined to by __addr (little endian)
    LOA __num
    LOB __addr
    STI A __addr+1,B
.next:
    LOA __addr
    LOB __addr+1
    LDA A+1
    LDB B+
    STO A __addr
    STO B __addr+1
    JMP .loop
.end:
    CHR '\n'
    JMP Prompt

dump_command:
    CHR 'D'
    JMP Prompt
video_command:
    CHR 'V'
    JMP Prompt
run_command:
    CHR 'R'
    JMP Prompt
usage_cmd:
    MVB usage
.loop:
    LXA >usage B
    JPZ A Prompt
    JRX .
    OUT A
    LDB B+1
    JMP .loop

Hex2Int16:
    STO 0 __num
    STO 0 __num+1
    LOA __hex
    MVB $20
    LDA A|B
    MVB '0'
    LDA A-B
    MVB 10
    TST A-B
    JLT .digit
    MVB 39
    LDA A-B
.digit:
    MVB 16
    STO A*B __num+1

    LOA __hex+1
    MVB $20
    LDA A|B
    MVB '0'
    LDA A-B
    MVB 10
    TST A-B
    JLT .digit2
    MVB 39
    LDA A-B
.digit2:
    LOB __num+1
    STO A|B __num+1

    LOA __hex+2
    MVB $20
    LDA A|B
    MVB '0'
    LDA A-B
    MVB 10
    TST A-B
    JLT .digit3
    MVB 39
    LDA A-B
.digit3:
    MVB 16
    STO A*B __num

    LOA __hex+3
    MVB $20
    LDA A|B
    MVB '0'
    LDA A-B
    MVB 10
    TST A-B
    JLT .digit4
    MVB 39
    LDA A-B
.digit4:
    LOB __num
    STO A|B __num
    RTS Hex2Int16

Hex2Int8:
    STO 0 __num
    LOA __hex
    MVB $20
    LDA A|B
    MVB '0'
    LDA A-B
    MVB 10
    TST A-B
    JLT .digit
    MVB 39
    LDA A-B
.digit:
    MVB 16
    STO A*B __num
    LOA __hex+1
    MVB $20
    LDA A|B
    MVB '0'
    LDA A-B
    MVB 10
    TST A-B
    JLT .digit2
    MVB 39
    LDA A-B
.digit2:
    LOB __num
    STO A|B __num
    RTS Hex2Int8

endprg:

PAG
welcome: db "\e[2J\e[HCSC Monitor, Revision: 1.00, 02/12/2023\nType ? for help\n"
usage: db "Usage: D dump, V video dump, C change, R run, X clear/reset, ? help\n"

ORG $FD00
cmdline: db (16)
__addr: dw
__hex: db (4)
__int16: dw
__num: dw


exp Prompt
exp Hex2Int8
exp Hex2Int16
exp __addr
exp __hex
exp __int16
exp __num

