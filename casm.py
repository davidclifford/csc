import sys
import re
import os


def usage():
    print("Usage casm <source.s>")
    exit(0)


def get_special_char(special):
    if special == 'n':
        return 10
    if special == 'r':
        return 13
    if special == '0':
        return 0
    if special == 't':
        return 9
    if special == 'e':
        return 27
    if special == 'b':
        return 8
    return special


def parse_number(num):
    if '+' in num:
        nums = num.split('+')
        n1 = parse_number(nums[0])
        n2 = parse_number(nums[1])
        return n1+n2
    if '-' in num:
        nums = num.split('-')
        n1 = parse_number(nums[0])
        n2 = parse_number(nums[1])
        return n1-n2
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
        if num.startswith('"') or num.startswith("'"):
            qu = num[0]
            if not num.endswith(qu):
                print(f'Missing closing quote {qu} on line {line_count}')
            if len(num) == 1:
                return 32
            if len(num) > 3:
                if num[1] == '\\':
                    special = num[2]
                    return get_special_char(special)
                else:
                    print(f'Only compound characters starting with \\ allowed, on line {line_count}')
                    return 0
            return ord(num[1:2]) & 0xff
    except ValueError:
        pass
    print(f'Expected a number but found {num} on line {line_count}')
    exit(1)


try:
    with open('GenControl/opcodes') as file:
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
    with open('GenControl/aluopcodes') as file:
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

# options & filename
PC = 0x8000
filename = None
monitor = False
for arg in sys.argv:
    print(arg)
    if arg.startswith('-'):
        if arg[1] == 'm':
            monitor = True
            PC = 0
    else:
        filename = arg

try:
    file = open(filename)
    lines = file.readlines()
    file.close()
except FileNotFoundError:
    exit(f"Source file {filename} not found")
except IndexError:
    usage()
    exit()

label = {}
last_label = ''
line_count = 0
return_addrs = {}
stack_ptr = 0xff00-2
exports = {}
start_addr = 0x10000
end_addr = 0

mem = bytearray([0 for _ in range(0x10000)])
################
#  FIRST PASS  #
################
print('--- First Pass ---')
for line in lines:
    if PC < start_addr:
        start_addr = PC
    if PC > end_addr:
        end_addr = PC

    line_count += 1
    ln = line.lstrip().rstrip()
    if len(ln) == 0:
        continue
    if ln.startswith('#') or ln.startswith(';') or ln.startswith('//'):
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

    if op == 'imp':
        import_filename = tokens[1]
        try:
            with open(import_filename) as file:
                import_lines = file.readlines()
        except (FileNotFoundError, IndexError):
            print(f"Import file {import_filename} not found on line {line_count}")
            exit(1)
        for imp_line in import_lines:
            if len(imp_line.rstrip().lstrip()) == 0:
                continue
            imp_labels = imp_line.split()
            if len(imp_labels) != 3:
                print(f'Incorrectly formatted import file')
                exit(1)
            if not imp_labels[0].endswith(':'):
                print(f'Import label missing, found {imp_labels[0]}')
                exit(1)
            if not imp_labels[1].lower() == 'equ':
                print(f'Expected EQU keyword bit found {imp_labels[1]}')
                exit(1)
            labl = imp_labels[0].split(':')[0]
            if labl in label:
                print(f'Existing label "{labl}" found in import file {import_filename}')
                exit(1)
            label[labl] = parse_number(imp_labels[2])
        continue

    if op == 'exp':
        continue

    if op == 'org':
        if start_addr == 0x8000 and PC == 0x8000:
            start_addr = parse_number(tokens[1])
        PC = parse_number(tokens[1])
        continue

    if op == 'db' or op == 'dw':
        first_param = tokens[1] if len(tokens) > 1 else '0'
        if op == 'dw':
            PC = (PC+1) & 0xFFFE
        if first_param.startswith('"') or first_param.startswith("'"):
            quote = first_param[0]
            first_param = ln.split(quote)[1]
            for c in first_param:
                if c != '\\':
                    PC += 1
            if quote == '"':
                PC += 1
            continue
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
PC = 0 if monitor else 0x8000
line_count = 0
last_label = ''
for line in lines:
    line_count += 1

    ln = line.lstrip().rstrip()
    if len(ln) == 0:
        continue
    if ln.startswith('#') or ln.startswith(';') or ln.startswith('//'):
        continue

    # Skip over labels
    if ln.split(' ')[0].endswith(":"):
        lab = ln.split(':')[0]
        if not lab.startswith('.'):
            last_label = lab
        ln = ln[len(ln.split(':')[0])+1:].lstrip()
        if len(ln) == 0:
            continue
    print(f'-- Line {line_count:6} PC = {PC:04x} : {ln}')

    tokens = ln.split(' ')
    op = tokens[0].lower()
    first_param = second_param = third_param = None
    if len(tokens) > 1:
        first_param = tokens[1]
    if len(tokens) > 2:
        second_param = tokens[2]
    if len(tokens) > 3:
        third_param = tokens[3]
    print(f'-- First {first_param}, Second {second_param}, Third {third_param}')

    if op == 'exp':
        if first_param:
            exports[first_param] = label[first_param]
        continue
    if op == 'equ' or op == 'imp':
        continue
    if op == 'org':
        PC = parse_number(first_param)
        continue
    if op == 'pag':
        PC = (PC+255) & 0xff00
        continue
    if op == 'db' or op == 'dw':
        first_param = tokens[1] if len(tokens) > 1 else '0'
        quote = first_param[0]
        if quote == '"' or quote == "'":
            first_param = ln.split(quote)[1]
            chptr = 0
            while chptr < len(first_param):
                c = first_param[chptr]
                if c == '\\':
                    chptr += 1
                    c = get_special_char(first_param[chptr])
                else:
                    c = ord(c)
                mem[PC] = c
                PC += 1
                chptr += 1
            if quote == '"':
                mem[PC] = 0
                PC += 1
            continue
        elif quote == '(':
            if op == 'db':
                PC += parse_number(first_param[1:-1])
            else:
                PC += 2*parse_number(first_param[1:-1])
            continue
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
    param_size = num_bytes - int(needs_alu > 0) - 1

    mem[PC] = opcode
    PC += 1

    if op == 'jsr':  # OP stklow stkhi pclow alu=D stklow+1 pchi jplo jhi
        jump_addr = parse_number(first_param)
        if jump_addr not in return_addrs:
            stack_ptr += 2
            if stack_ptr > 0xffff:
                print(f'Error: Run out of return addresses on line {line_count}')
                exit(1)
            return_addrs[jump_addr] = stack_ptr
        else:
            stack_ptr = return_addrs[jump_addr]
        addr = PC + 8
        mem[PC] = stack_ptr & 0xff
        PC += 1
        mem[PC] = (stack_ptr >> 8) & 0xff
        PC += 1
        mem[PC] = addr & 0xff
        PC += 1
        mem[PC] = aluops['d']
        PC += 1
        mem[PC] = (stack_ptr + 1) & 0xff
        PC += 1
        mem[PC] = (addr >> 8) & 0xff
        PC += 1
        mem[PC] = jump_addr & 0xff
        PC += 1
        mem[PC] = (jump_addr >> 8) & 0xff
        PC += 1
        print(f'Return address {addr:04x} stored at {stack_ptr:04x}')
        continue

    if op == 'rts':  # OP stklo stkhi stklo+1 ALU=D ALU=C
        jump_addr = parse_number(first_param)
        stk_ptr = return_addrs[jump_addr]
        mem[PC] = stk_ptr & 0xff
        PC += 1
        mem[PC] = (stk_ptr >> 8) & 0xff
        PC += 1
        mem[PC] = (stk_ptr + 1) & 0xff
        PC += 1
        mem[PC] = aluops['d']
        PC += 1
        mem[PC] = aluops['c']
        PC += 1
        print(f'Returning to address stored at {stk_ptr:04x}')
        continue

    if op == 'sti':  # OP ALUopStore Highbyte ALUopIndx (swap alu ops in byte stream)
        aluopStore = aluops[first_param.lower()]
        highByte = (parse_number(second_param) >> 8) & 0xff
        aluopIndex = aluops[third_param.lower()]
        mem[PC] = aluopIndex
        PC += 1
        mem[PC] = highByte
        PC += 1
        mem[PC] = aluopStore
        PC += 1
        continue

    if op == 'stx':  # OP ALUopStore LowByte Highbyte ALUopIndx (swap alu ops byte stream)
        aluopStore = aluops[first_param.lower()]
        lowByte = parse_number(second_param) & 0xff
        highByte = (parse_number(second_param) >> 8) & 0xff
        aluopIndex = aluops[third_param.lower()]
        mem[PC] = aluopIndex
        PC += 1
        mem[PC] = lowByte
        PC += 1
        mem[PC] = highByte
        PC += 1
        mem[PC] = aluopStore
        PC += 1
        continue

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
        if param_size == 1:
            mem[PC] = parse_number(first_param) & 0xff
            PC += 1
        else:
            mem[PC] = parse_number(first_param) & 0xff
            PC += 1
            mem[PC] = (parse_number(first_param) >> 8) & 0xff
            PC += 1
if len(return_addrs) > 0:
    print('--- Return addresses ---')
    print(return_addrs)
# Write bottom 32k for ROM if monitor
if monitor:
    print('--- Writing to instr.bin ---')
    with open('./Sim/instr.bin', 'wb') as file:
        file.write(mem[:0x8000])
else:
    # Write HEX file
    print('--- Writing to hex file ---')
    hexfile = filename.split('.')[0] + '.hex'
    with open(hexfile, 'w') as f:
        for addr in range(start_addr, end_addr):
            if addr % 16 == 0:
                f.write(f'C{addr:04x} ')
            f.write(f'{mem[addr]:02x} ')
            if addr % 16 == 15:
                f.write('Z\n')
        if addr % 16 != 15:
            f.write('Z')

# Write out exports
if len(exports) > 0:
    print('--- Writing exports to header file ---')
    header = filename.split('.')[0]+'.h'
    with open(header, 'w') as f:
        for ex in exports:
            f.write(f'{ex}: EQU ${exports[ex]:04x}\n')
