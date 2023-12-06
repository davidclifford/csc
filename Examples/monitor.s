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
    CHR 'C'
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
endprg:
PAG
welcome: db "\e[2J\e[HCSC Monitor, Revision: 1.00, 02/12/2023\nType ? for help\n"
usage: db "Usage: D dump, V video dump, C change, R run, X clear/reset, ? help\n"

ORG $FC00
cmdline: db (16)

exp prompt
