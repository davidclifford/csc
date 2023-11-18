import sys
import re
import os


def usage():
    print("Usage casm <source.s>")
    exit(0)


def parse_number(num):
    try:
        if num.startswith('$'):
            return int(num[1:], 16)
        if num.isdigit():
            return int(num)
        if num.startswith('%'):
            return int(num[1:], 2)
        if num.startswith('.'):
            if num == '.':
                return PC
            num = last_label + num
        if num in label:
            return label[num]
        if num.startswith('<'):
            return parse_number(num[1:]) & 0xff
        if num.startswith('>'):
            return (parse_number(num[1:]) >> 8) & 0xff
    except ValueError:
        pass
    print(f'Expected a number but found {num} on line {line_count}')
    exit(1)


try:
    with open('opcodes') as file:
        opcode_lines = file.readlines()
except (FileNotFoundError, IndexError):
    exit("opcodes not found")
opcodes = {}
for op in opcode_lines:
    o = op.lstrip().rstrip().split(' ')
    opcode = int(o[0], 16)
    mnemonic = o[1].lower()
    needs_alu = int(o[2])
    num_bytes = int(o[3])
    opcodes[mnemonic] = {'opcode': opcode, 'needs_alu': needs_alu, 'num_bytes': num_bytes}
# print(opcodes)

try:
    with open('aluopcodes') as file:
        aluop_lines = file.readlines()
except (FileNotFoundError, IndexError):
    exit("aluopcodes not found")
aluops = {}
for op in aluop_lines:
    aluop = op.lstrip().rstrip().split(' ')
    opcode = int(aluop[0], 16)
    function = aluop[1].lower()
    aluops[function] = opcode
print(aluops)

try:
    filename = sys.argv[1]
    file = open(filename)
    lines = file.readlines()
    file.close()
except FileNotFoundError:
    exit(f"Source file {sys.argv[1]} not found")
except IndexError:
    usage()
    exit()

PC = 0
label = {}
last_label = ''
line_count = 0
mem = bytearray([0 for _ in range(0x8000)])
################
#  FIRST PASS  #
################
print('--- First Pass ---')
for line in lines:
    line_count += 1
    ln = line.lstrip().rstrip().replace(',', ' ')
    if len(ln) == 0:
        continue
    if ln.startswith('#'):
        continue

    # Find labels
    if ln.split(' ')[0].endswith(":"):
        lab1 = ln.split(':')[0]
        if lab1.startswith('.'):
            lab = last_label + lab1
        else:
            lab = lab1
        if lab in label:
            print(f'Label {lab} already exists, line {line_count}')
            exit(1)
        label[lab] = PC
        if not lab1.startswith('.'):
            last_label = lab
        ln = ln[len(lab1)+1:].lstrip()
        if len(ln) == 0:
            continue

    tokens = ln.split(' ')
    op = tokens[0].lower()
    if op == 'org':
        PC = parse_number(tokens[1])
        continue

    if op == 'db' or op == 'dw':
        first_param = tokens[1]
        if op == 'dw':
            PC = (PC+1) & 0xFFFE
        if first_param.startswith('"') or first_param.startswith("'"):
            quote = first_param[0]
            first_param = ln.split(quote)[1]
            PC += len(first_param)
            if quote == '"':
                PC += 1
        if first_param.startswith('('):
            if not first_param.endswith(')'):
                print(f'Missing closing ) on line {line_count} ')
                exit(1)
            PC += parse_number(first_param[1:-1])
        else:
            PC += (1 if op == 'db' else 2)
        continue

    if op == 'pag':
        PC = (PC+255) & 0xFF00
        continue

    if op == 'equ':
        label[last_label] = parse_number(tokens[1])
        continue

    if op not in opcodes:
        print(f'Unknown opcode {tokens[0]} on line {line_count}')
        exit(1)
    # print(f'PC {PC:04x} {op}')
    PC += opcodes[op]['num_bytes']

for lab in label:
    print(f'Label {lab}: {label[lab]:04x}')

###############
# SECOND PASS #
###############
print('--- Second Pass ---')
PC = 0
line_count = 0
last_label = ''
for line in lines:
    line_count += 1

    ln = line.lstrip().rstrip().replace(',', ' ')
    if len(ln) == 0:
        continue
    if ln.startswith('#'):
        continue

    # Skip over labels
    if ln.split(' ')[0].endswith(":"):
        lab = ln.split(':')[0]
        if not lab.startswith('.'):
            last_label = lab
        ln = ln[len(ln.split(':')[0])+1:].lstrip()
        if len(ln) == 0:
            continue
    print(f'Line {line_count:6} PC = {PC:04x} : {ln}')

    tokens = ln.split(' ')
    op = tokens[0].lower()
    first_param = second_param = third_param = None
    if len(tokens) > 1:
        first_param = tokens[1]
    if len(tokens) > 2:
        second_param = tokens[2]
    if len(tokens) > 3:
        third_param = tokens[3]
    if op == 'equ':
        continue
    if op == 'org':
        PC = parse_number(first_param)
        continue
    if op == 'pag':
        PC = (PC+255) & 0xff00
        continue
    if op == 'db' or op == 'dw':
        quote = tokens[1][0]
        if quote == '"' or quote == "'":
            first_param = ln.split(quote)[1]
            for c in first_param:
                mem[PC] = ord(c)
                PC += 1
            if quote == '"':
                mem[PC] = 0
                PC += 1
        else:
            if op == 'db':
                mem[PC] = parse_number(first_param) & 0xff
                PC += 1
            else:
                mem[PC] = parse_number(first_param) & 0xff
                PC += 1
                mem[PC] = (parse_number(first_param) >> 8) & 0xff
                PC += 1
        continue

    # OP CODES
    if op not in opcodes:
        print(f'Opcode {op} not found on line {line_count}')
        exit(1)

    opcode = opcodes[op]['opcode']
    needs_alu = opcodes[op]['needs_alu']
    num_bytes = opcodes[op]['num_bytes']
    param_size = num_bytes - int(needs_alu>0) - 1

    mem[PC] = opcode
    PC += 1

    print(f'Opcode {op.upper()} = {opcode:02x}, alu {needs_alu}, param_size {param_size}')
    if needs_alu > 0:
        if needs_alu == 1:
            aluop = first_param.lower()
            first_param = second_param
        else:
            aluop = second_param.lower()
        print(f'ALU OP {aluop}')
        if not aluop or aluop not in aluops:
            print(f'Missing ALU Operation on line {line_count}')
            exit(0)
        mem[PC] = aluops[aluop]
        PC += 1

    if first_param:
        print(f'1st {first_param}')
        if param_size == 1:
            mem[PC] = parse_number(first_param) & 0xff
            PC += 1
        else:
            mem[PC] = parse_number(first_param) & 0xff
            PC += 1
            mem[PC] = (parse_number(first_param) >> 8) & 0xff
            PC += 1

print('--- Writing to file ---')
with open('instr.bin', 'wb') as file:
    file.write(mem)

