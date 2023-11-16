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
    except ValueError:
        pass
    print(f'Expected a number but found {num}')
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
    needs_alu = bool([2])
    num_bytes = int(o[3])
    opcodes[mnemonic] = {'opcode': opcode, 'needs_alu': needs_alu, 'num_bytes': num_bytes}
print(opcodes)

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
line_count = 0
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
        lab = ln.split(':')[0]
        if lab in label:
            print(f'Label {lab} already exists')
            exit(1)
        label[lab] = PC
        ln = ln[len(lab)+1:].lstrip()
        if len(ln) == 0:
            continue

    tokens = ln.split(' ')
    op = tokens[0].lower()
    if op == 'org':
        PC = parse_number(tokens[1])
        continue

    if op == 'db':
        string = tokens[1]
        if string.startswith('"') or string.startswith("'"):
            quote = string[0]
            string = ln.split(quote)[1]
            PC += len(string)
            if quote == '"':
                PC += 1
        continue

    if op not in opcodes:
        print(f'Unknown opcode {tokens[0]} on line {line_count}')
        exit(1)
    # print(f'PC {PC:04x} {op}')
    PC += opcodes[op]['num_bytes']

for lab in label:
    print(f'Label {lab}: {label[lab]:04x}')
