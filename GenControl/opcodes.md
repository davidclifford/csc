# OPCODES

### Glossary

addr = address

dd = data

aluop = ALU operation

index = ALU operation

r = Register A,B,C or D

&gt; = Top 8 bits of address

< = Bottom 8 bits of address

---
### Instructions
LOr addr : LOAD ABS register addressed by absolute address addr e.g. LOD $1234

LXr addr, >aluop : LOAD INDEXED register from address >addr|aluop

LIr addr, aluop : LOAD INDIRECT INDEXED register from address [addr]|aluop

STO aluop addr : STORE ABS aluop to absolute address addr e.g. STO A $1234

STX aluop >addr, index : STORE INDEXED aluop to address >addr|index

STI aluop addr, index : STORE INDIRECT INDEXED aluop to address [addr]|aluop



