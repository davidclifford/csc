import re
import argparse

arg_parser = argparse.ArgumentParser(description='asm')
arg_parser.add_argument('-m', dest='monitor', action='store_true', help='use as monitor')
arg_parser.add_argument(type=str, dest='filename')
args = arg_parser.parse_args()
filename = args.filename

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
    num_args = int(o[4])
    opcodes[mnemonic] = {'opcode': opcode, 'needs_alu': needs_alu, 'num_bytes': num_bytes, 'num_args': num_args}
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
# print(aluops)

try:
    file = open(filename)
    src = file.read() + "\0"
    file.close()
except (FileNotFoundError, IndexError):
    exit("USAGE: asm.py [-m] <filename>")

ep = 0
line = 1
PC = 0x8000
stack_ptr = 0xfa00
if args.monitor:
    PC = 0
    stack_ptr = 0xfb00
start_addr = 0x10000
end_addr = 0
label = {}
last_label = ''
return_addrs = {}
exports = {}
newline = False
mem = bytearray([0 for _ in range(0x10000)])


def find_token():  # SKIP WHITESPACES AND COMMENTS, COUNT LINES AND RETURN ELEMENT LENGTH
    global ep, line, src, newline
    newline = False
    while ep < len(src):
        if src[ep] == '"':
            m = re.match(r'"(.*?)(?<!\\)"', src[ep:])
            if not m:
                return 1
            return m.end()
        if src[ep] == "'":
            m = re.match(r"'(.*?)(?<!\\)'", src[ep:])
            if not m:
                return 1
            return m.end()
        if src[ep] == '\n':
            ep += 1
            line += 1
            newline = True
        elif m := re.match(r"[ ,\r\t]+|[;#][^\n\0]*", src[ep:]):
            ep += m.end()  # skip whitespaces & comments
        else:
            m = re.match(r"'[^'\n\0]*'|[^ ,;\t\n\r\0]*", src[ep:])
            return m.end() if m else None  # length


def error(message):
    err_mess = f'ERROR: {message}, on line {line}'
    # print(err_mess)
    exit(err_mess)


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
                error(f'Missing closing quote {qu}')
            if len(num) == 1:
                return 32
            if len(num) > 3:
                if num[1] == '\\':
                    special = num[2]
                    return get_special_char(special)
                else:
                    error(f'Only compound characters starting with \\ allowed')
                    return 0
            return ord(num[1:2]) & 0xff
    except ValueError:
        pass
    error(f'Expected a number but found {num}')


##############
# First Pass #
##############
print('--- First Pass ---')
while size := find_token():
    if PC < start_addr:
        start_addr = PC
    if PC > end_addr:
        end_addr = PC

    op = src[ep:ep+size]
    token = op.lower()
    # print(f'{line}: {PC:04x} {size} {token} {newline}')
    if size == 0:
        break

    # Labels
    elif token.endswith(":"):
        lab = op[:-1]
        if token.startswith('.'):
            lab = last_label + lab
        else:
            last_label = lab
        if lab in label:
            error(f'Label {lab} already exists')
        label[lab] = PC

    elif token == 'exp':
        ep += size
        size = find_token()
    elif token == 'imp':
        ep += size
        size = find_token()
    elif token == 'org':
        ep += size
        size = find_token()
        addr = src[ep:ep+size]
        if start_addr == 0x8000 and PC == 0x8000:
            start_addr = parse_number(addr)
        PC = parse_number(addr)

    # DB and DW
    elif token == 'db' or token == 'dw':
        if token == 'dw':
            PC = (PC+1) & 0xFFFE
        ep += size
        size = find_token()
        while not newline:
            token = src[ep:ep+size]
            # print(f'DB/W [{token}]')
            if token.startswith("'") or token.startswith('"'):
                for c in token[1:-1]:
                    if c != '\\':
                        PC += 1
                if token.endswith('"'):
                    PC += 1
            elif token.startswith('('):
                if not token.endswith(')'):
                    error('Missing closing )')
                PC += parse_number(token[1:-1])
            else:
                PC += (1 if op.lower() == 'db' else 2)
            ep += size
            size = find_token()
        ep -= size

    elif token == 'pag':
        PC = (PC+255) & 0xFF00

    elif token == 'equ':
        ep += size
        size = find_token()
        token = src[ep:ep+size]
        label[last_label] = parse_number()

    elif token in opcodes:
        PC += opcodes[token]['num_bytes']
        # Consume trailing arguments
        num_args = opcodes[token]['num_args']
        print(f'--- OP {op} num_args {num_args}')
        for _ in range(num_args):
            ep += size
            size = find_token()
            print(f'param {src[ep:ep+size]}')

    else:
        error(f'Unknown opcode {op}')

    ep += size

print('--- Labels: ---')
for l in label:
    print(f'\t{l} = {label[l]:04x}')

#################
# Second Pass 2 #
#################
print(r'--- Second pass ---')
ep = 0
PC = 0 if args.monitor else 0x8000
line = 1
last_label = ''
while size := find_token():
    # Skip over labels
    op = src[ep:ep+size]
    token = op.lower()
    ep += size
    print(f'{line} PC: {PC:04x}, OP {token}')
    if token.endswith(':'):
        if not token.startswith('.'):
            last_label = op[:-1]
    elif token == 'equ' or token == 'imp':
        ep += size
        size = find_token()
    elif token == 'exp':
        size = find_token()
        param = src[ep:ep+size]
        exports[param] = label[param]
        if label[param] in return_addrs:
            exports[param+'_ret'] = return_addrs[label[param]]
        ep += size
    elif token == 'org':
        size = find_token()
        param = src[ep:ep+size]
        PC = parse_number(param)
        ep += size
    elif token == 'pag':
        PC = (PC+255) & 0xff00
    elif token == 'db' or token == 'dw':
        if token == 'dw':
            PC = (PC+1) & 0xfffe
        newline = False
        size = find_token()
        while not newline:
            param = src[ep:ep + size]
            ep += size
            if param.startswith('"') or param.startswith("'"):
                quote = param[0]
                string = param[1:-1]
                special = False
                for c in string:
                    if c == '\\':
                        special = True
                    else:
                        if special:
                            c = get_special_char(c)
                            special = False
                        else:
                            c = ord(c)
                        mem[PC] = c
                        PC += 1
                if quote == '"':
                    mem[PC] = 0
                    PC += 1
            elif param.startswith('('):
                PC += parse_number(param[1:-1])
            else:
                if token == 'db':
                    mem[PC] = parse_number(param) & 0xff
                    PC += 1
                else:
                    mem[PC] = parse_number(param) & 0xff
                    PC += 1
                    mem[PC] = (parse_number(param) >> 8) & 0xff
                    PC += 1
            size = find_token()
    elif op == 'jsr':  # OP stklow stkhi pclow alu=D [stklow+1] pchi jplo jhi
        mem[PC] = opcodes[op]
        PC += 1
        size = find_token()
        param = src[ep:ep + size]
        ep += size
        jump_addr = parse_number(param)
        if not args.monitor and jump_addr < 0x8000:
            param = src[ep:ep + size]
            ep += size
            ret_addr = parse_number(param)
        elif jump_addr not in return_addrs:
            stack_ptr -= 2
            return_addrs[jump_addr] = stack_ptr
            ret_addr = stack_ptr
        else:
            ret_addr = return_addrs[jump_addr]
        addr = PC + 8
        mem[PC] = ret_addr & 0xff
        PC += 1
        mem[PC] = (ret_addr >> 8) & 0xff
        PC += 1
        mem[PC] = addr & 0xff
        PC += 1
        mem[PC] = aluops['d']
        PC += 1
        mem[PC] = (ret_addr + 1) & 0xff
        PC += 1
        mem[PC] = (addr >> 8) & 0xff
        PC += 1
        mem[PC] = jump_addr & 0xff
        PC += 1
        mem[PC] = (jump_addr >> 8) & 0xff
        PC += 1
        print(f'Return address {addr:04x} stored at {ret_addr:04x}')
    elif op == 'rts':  # OP stklo stkhi stklo+1 ALU=D ALU=C
        size = find_token()
        param = src[ep:ep + size]
        ep += size
        jump_addr = parse_number(param)
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

    # Store Reg at address indexed by Index-reg
    elif token == 'stx':  # OP ALUopStore LowByte Highbyte ALUopIndx (swap alu ops byte stream)
        mem[PC] = opcodes[token]['opcode']
        PC += 1
        size = find_token();  reg = src[ep:ep+size]; ep += size
        size = find_token();  addr = src[ep:ep+size]; ep += size
        size = find_token();  index = src[ep:ep+size]; ep += size
        print(f'--- {reg} {addr} {index}')
        aluopStore = aluops[reg.lower()]
        lowByte = parse_number(addr) & 0xff
        highByte = (parse_number(addr) >> 8) & 0xff
        aluopIndex = aluops[index.lower()]
        mem[PC] = aluopIndex; PC += 1
        mem[PC] = lowByte; PC += 1
        mem[PC] = highByte; PC += 1
        mem[PC] = aluopStore; PC += 1
    elif token == 'sti':  # OP ALUopStore Highbyte ALUopIndx (swap alu ops in byte stream)
        mem[PC] = opcodes[token]['opcode']
        PC += 1
        size = find_token();  reg = src[ep:ep+size]; ep += size
        size = find_token();  addr = src[ep:ep+size]; ep += size
        size = find_token();  index = src[ep:ep+size]; ep += size
        mem[PC] = aluops[index.lower()]
        PC += 1
        mem[PC] = (parse_number(addr) >> 8) & 0xff
        PC += 1
        mem[PC] = aluops[reg.lower()]
        PC += 1
    # All other opcodes
    elif token not in opcodes:
        error(f'Opcode {op} not found')
    else:
        opcode = opcodes[token]['opcode']
        needs_alu = opcodes[token]['needs_alu']
        num_bytes = opcodes[token]['num_bytes']
        num_args = opcodes[token]['num_args']
        param_size = num_bytes - int(needs_alu > 0) - 1
        param1 = param2 = param3 = None
        if num_args > 0:
            size = find_token()
            param1 = src[ep:ep+size]
            ep += size
        if num_args > 1:
            size = find_token()
            param2 = src[ep:ep+size]
            ep += size
        if num_args > 2:
            size = find_token()
            param3 = src[ep:ep+size]
            ep += size
        print(f'OP {token}, code {opcode}, p1 {param1}, p2 {param2}, p3 {param3}')
        mem[PC] = opcode
        PC += 1
        if needs_alu > 0:
            aluop = None
            if needs_alu == 1:
                aluop = param1.lower()
                param1 = param2
            else:
                aluop = param2.lower()
            if aluop:
                if aluop not in aluops:
                    error(f'Unknown alu op {aluop}')
            else:
                error(f'Missing alu op')
            mem[PC] = aluops[aluop]
            PC += 1
        if param1:
            if param_size == 1:
                mem[PC] = parse_number(param1) & 0xff
                PC += 1
            else:
                mem[PC] = parse_number(param1) & 0xff
                PC += 1
                mem[PC] = (parse_number(param1) >> 8) & 0xff
                PC += 1

print(f'--- Start {start_addr:04x}, End {end_addr:04x} ---')
if exports:
    exp_filename = filename[:-2] + '.h'
    print(f'--- Writing Exports to {exp_filename}---')
    with open(exp_filename, 'w') as file:
        for ex in exports:
            print(f'\t{ex}: ${exports[ex]:04x}')
            file.write(f'{ex}: EQU ${exports[ex]:04x}')

if args.monitor:
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
