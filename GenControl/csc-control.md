CSC

ALU OP (8 bits)
------
OP    - 5-bits
AB/CD - 1-bit
Use Carry - 1-bit (OR carry with bit 3 of OP)

Control Input (16-bits)
-------------
IR - 8-bits
FL - 4-bits
SQ - 4-bits

WRITE TO DB (2-bits)
----------
MEM
ALU (Also Flags SET)
IO
EXT

READ FROM DB (4-bits)
---------
None
MEM
IR
A
B
C
D
MARHi
MARlo
IO
ALUop
Bank

Jump Logic (3-bits)
----------
None (False)
ALU_Z
ALU_N
RX
TX
JUMP_FL (unconditional)


CONTROL (4-bits)
-------
PC/MAR (MARena)
PCinc
uReset
Address+1 (MARlo|$01)

13 bits

Examples
--------

JAZ: (with jump logic) 4 bytes
MEMout | IRload | PC++ (fetch next istruction)
MEMout | ALUOpLoad | PC++ (get ALU op from program stream [A])
MEMout | PCLoLoad | PC++
MEMout | PCJumpLoad | ALU_Z | PC++ | uReset (address to jump to)
Clocks: 4

NOP:
MEMout | IRload | PC++ (fetch next istruction)
uReset

LDA #42
MEMout | IRload | PC++ (fetch next istruction)
MEMout | Aload | PC++ | uReset

LDA C
MEMout | IRload | PC++ (fetch next istruction)
MEMout | ALUload | PC++  [A | AB/CD]
ALUout | Aload | uReset

LDC A+B:
MEMout | IRload | PC++ (fetch next istruction)
MEMout | ALUOpLoad | PC++ [A+B]
ALUout | Cload | uReset

LDD A+B+:
MEMout | IRload | PC++ (fetch next istruction)
MEMout | ALUOpLoad | PC++ [A+B|UseCarry]
ALUout | Dload | uReset

STO A+B
MEMout | IRload | PC++ (fetch next istruction)
MEMout | ALUOpLoad | PC++ [A+B]
MEMout | MARLoLoad | PC++
MEMout | MARHiLoad | PC++
ALUout | MARena | MEMload | uReset
