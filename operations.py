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
    a = memory[p_c+1] - 32768
    b = num_or_value_from_reg(memory[p_c+2], regs)
    regs[a] = b
    # print(a,b,regs)
    return memory, p_c + 3, regs, st


def noop(memory, p_c, regs, st):
    return memory, p_c+1, regs, st


def jmp(memory, p_c, regs, st):
    a = num_or_value_from_reg(memory[p_c + 1], regs)
    return memory, a, regs, st


def jt(memory, p_c, regs, st):
    a = num_or_value_from_reg(memory[p_c+1], regs)
    b = num_or_value_from_reg(memory[p_c+2], regs)
    dest = p_c + 3
    if a != 0:
        dest = b
    return memory, dest, regs, st


def jf(memory, p_c, regs, st):
    a = num_or_value_from_reg(memory[p_c+1], regs)
    b = num_or_value_from_reg(memory[p_c+2], regs)
    dest = p_c + 3
    if a == 0:
        dest = b
    return memory, dest, regs, st


def do_quit(*args):
    print()
    print(args[1])
    quit()


def eq(memory, p_c, regs, st):
    a = memory[p_c + 1]
    b = num_or_value_from_reg(memory[p_c + 2], regs)
    c = num_or_value_from_reg(memory[p_c + 3], regs)
    # print(memory[p_c], memory[p_c+1], memory[p_c+2], memory[p_c+3])
    if b == c:
        result = 1
    else:
        result = 0

    if a > 32767:
        regs[a - 32768] = result
    else:
        memory[a] = result
    return memory, p_c+4, regs, st


def push(memory, p_c, regs, st):
    a = num_or_value_from_reg(memory[p_c + 1], regs)
    st.append(a)
    return memory, p_c+2, regs, st


def pop(memory, p_c, regs, st):
    a = memory[p_c+1]
    result = st.pop()
    if a > 32767:
        regs[a - 32768] = result
    else:
        memory[a] = result
    return memory, p_c+2, regs, st


def gt(memory, p_c, regs, st):
    a = memory[p_c+1]
    b = num_or_value_from_reg(memory[p_c+2], regs)
    c = num_or_value_from_reg(memory[p_c+3], regs)
    result = 0
    if b > c:
        result = 1
    if a > 32767:
        regs[a - 32768] = result
    else:
        memory[a] = result
    return memory, p_c+4, regs, st


def and_opr(memory, p_c, regs, st):
    a = memory[p_c+1]
    b = num_or_value_from_reg(memory[p_c+2], regs)
    c = num_or_value_from_reg(memory[p_c+3], regs)
    result = b & c
    if a > 32767:
        regs[a - 32768] = result
    else:
        memory[a] = result
    return memory, p_c+4, regs, st


def or_opr(memory, p_c, regs, st):
    a = memory[p_c+1]
    b = num_or_value_from_reg(memory[p_c+2], regs)
    c = num_or_value_from_reg(memory[p_c+3], regs)
    result = b | c
    if a > 32767:
        regs[a - 32768] = result
    else:
        memory[a] = result
    return memory, p_c+4, regs, st


def not_opr(memory, p_c, regs, st):
    a = memory[p_c + 1]
    b = num_or_value_from_reg(memory[p_c + 2], regs)
    result = ~b % 32768
    if a > 32767:
        regs[a - 32768] = result
    else:
        memory[a] = result
    return memory, p_c+3, regs, st


def call(memory, p_c, regs, st):
    a = num_or_value_from_reg(memory[p_c + 1], regs)
    st.append(p_c+2)
    return memory, a, regs, st


def mult(memory, p_c, regs, st):
    a = memory[p_c + 1]
    b = num_or_value_from_reg(memory[p_c + 2], regs)
    c = num_or_value_from_reg(memory[p_c + 3], regs)
    result = (b * c) % 32768
    if a > 32767:
        regs[a - 32768] = result
    else:
        memory[a] = result
    return memory, p_c + 4, regs, st


def mod(memory, p_c, regs, st):
    a = memory[p_c + 1]
    b = num_or_value_from_reg(memory[p_c + 2], regs)
    c = num_or_value_from_reg(memory[p_c + 3], regs)
    result = b % c
    if a > 32767:
        regs[a - 32768] = result
    else:
        memory[a] = result
    return memory, p_c + 4, regs, st


def rmem(memory, p_c, regs, st):
    a = memory[p_c + 1]
    b = num_or_value_from_reg(memory[p_c + 2], regs)
    result = memory[b]
    regs[a - 32768] = result
    return memory, p_c+3, regs, st


def wmem(memory, p_c, regs, st):
    a = num_or_value_from_reg(memory[p_c+1], regs)
    b = num_or_value_from_reg(memory[p_c+2], regs)
    result = b
    if a > 32767:
        regs[a - 32768] = result
    else:
        memory[a] = result
    return memory, p_c+3, regs, st


def ret(memory, p_c, regs, st):
    dest = st.pop()
    return memory, dest, regs, st


def in_opr(memory, p_c, regs, st):
    return memory, p_c+1, regs, st

operations = {
    0: do_quit,
    1: set_opr,
    2: push,
    3: pop,
    4: eq,
    5: gt,
    6: jmp,
    7: jt,
    8: jf,
    9: add,
    10: mult,
    11: mod,
    12: and_opr,
    13: or_opr,
    14: not_opr,
    15: rmem,
    16: wmem,
    17: call,
    18: ret,
    19: out,
    20: in_opr,
    21: noop,
}