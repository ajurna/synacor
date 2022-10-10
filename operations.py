def num_or_value_from_reg(n, regs):
    if n > 32767:
        return regs[n - 32768]
    return n


def out(memory, p_c, regs, st):
    a = num_or_value_from_reg(memory[p_c+1], regs)
    print(chr(a), end='')
    return memory, p_c + 2, regs, st


def add(memory, p_c, regs, st):
    a = memory[p_c+1]
    b = num_or_value_from_reg(memory[p_c+2], regs)
    c = num_or_value_from_reg(memory[p_c+3], regs)
    result = (b + c) % 32768
    if a > 32767:
        regs[a - 32768] = result
    else:
        memory[a] = result
    return memory, p_c + 4, regs, st


def set_opr(memory, p_c, regs, st):
    a = num_or_value_from_reg(memory[p_c+1], regs)
    b = num_or_value_from_reg(memory[p_c+2], regs)
    regs[a] = b
    print(a,b,regs)
    return memory, p_c + 3, regs, st


def noop(memory, p_c, regs, st):
    return memory, p_c+1, regs, st


def jmp(memory, p_c, regs, st):
    a = num_or_value_from_reg(memory[p_c + 1], regs)
    return memory, a, regs, st


def jt(memory, p_c, regs, st):
    a = num_or_value_from_reg(memory[p_c+1], regs)
    b = num_or_value_from_reg(memory[p_c+2], regs)
    print('jt', a, b, end='')
    dest = p_c + 3
    if a != 0:
        dest = b
    return memory, dest, regs, st


def jf(memory, p_c, regs, st):
    a = num_or_value_from_reg(memory[p_c+1], regs)
    b = num_or_value_from_reg(memory[p_c+2], regs)
    print('jf', a, b, end='')
    dest = p_c + 3
    if a == 0:
        dest = b
    return memory, dest, regs, st


def do_quit(*args):
    print()
    print(args[1])
    quit()

operations = {
    0: do_quit,
    1: set_opr,
    6: jmp,
    7: jt,
    8: jf,
    9: add,
    19: out,
    21: noop,
}