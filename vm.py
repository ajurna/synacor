import struct
from pathlib import Path
from typing import List


class VirtualMachine:
    def __init__(self):
        self.registers = [0, 0, 0, 0, 0, 0, 0, 0]
        self.counter = 0
        self.stack = []
        self.memory = []
        self.input_buffer = []
        self.running = False
        self.command_log = Path('command.log').open('w')
        self.operations = {
            0: self.halt,
            1: self.set_opr,
            2: self.push,
            3: self.pop,
            4: self.eq,
            5: self.gt,
            6: self.jmp,
            7: self.jt,
            8: self.jf,
            9: self.add,
            10: self.mult,
            11: self.mod,
            12: self.and_opr,
            13: self.or_opr,
            14: self.not_opr,
            15: self.rmem,
            16: self.wmem,
            17: self.call,
            18: self.ret,
            19: self.out,
            20: self.in_opr,
            21: self.noop,
        }

    def run(self):
        self.running = True
        while self.running:
            self.operations[self.memory[self.counter]]()

    def dump_strings(self):
        out = []
        for x in range(len(self.memory)):
            if self.memory[x] == 19:
                out.append(chr(self.memory[x+1]))
        return ''.join(out)

    def import_file(self, file: Path):
        st = struct.Struct('<H')
        self.memory = [i[0] for i in st.iter_unpack(file.open('rb').read())]

    def add_commands(self, commands: List):
        for command in commands:
            self.input_buffer.extend(list(command))
            self.input_buffer.append('\n')

    def get_value(self, n: int) -> int:
        if n > 32767:
            return self.registers[n - 32768]
        return n

    def set_value(self, n, v):
        if n > 32767:
            self.registers[n - 32768] = v
        else:
            self.memory[n] = v

    def halt(self):
        # halt: 0
        #   stop execution and terminate the program
        self.running = False

    def set_opr(self):
        # set: 1 a b
        #   set register <a> to the value of <b>
        a, b = self.memory[self.counter+1: self.counter+3]
        b = self.get_value(b)
        self.set_value(a, b)
        self.counter += 3

    def push(self):
        # push: 2 a
        #   push <a> onto the stack
        a = self.get_value(self.memory[self.counter + 1])
        self.stack.append(a)
        self.counter += 2

    def pop(self):
        # pop: 3 a
        #   remove the top element from the stack and write it into <a>; empty stack = error
        a = self.memory[self.counter + 1]
        self.set_value(a, self.stack.pop())
        self.counter += 2

    def eq(self):
        # eq: 4 a b c
        #   set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise
        a = self.memory[self.counter + 1]
        b, c = [self.get_value(x) for x in self.memory[self.counter + 2:self.counter + 4]]
        self.set_value(a, 1 if b == c else 0)
        self.counter += 4

    def gt(self):
        # gt: 5 a b c
        #   set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise
        a = self.memory[self.counter + 1]
        b, c = [self.get_value(x) for x in self.memory[self.counter + 2:self.counter + 4]]
        self.set_value(a, 1 if b > c else 0)
        self.counter += 4

    def jmp(self):
        # jmp: 6 a
        #   jump to <a>
        a = self.memory[self.counter + 1]
        self.counter = self.get_value(a)

    def jt(self):
        # jt: 7 a b
        #   if <a> is nonzero, jump to <b>
        a, b = [self.get_value(x) for x in self.memory[self.counter+1:self.counter+3]]
        if a != 0:
            self.counter = b
        else:
            self.counter += 3

    def jf(self):
        # jf: 8 a b
        #   if <a> is zero, jump to <b>
        a, b = [self.get_value(x) for x in self.memory[self.counter + 1:self.counter + 3]]
        if a == 0:
            self.counter = b
        else:
            self.counter += 3

    def add(self):
        # add: 9 a b c
        #   assign into <a> the sum of <b> and <c> (modulo 32768)
        a, b, c = self.memory[self.counter+1: self.counter+4]
        b = self.get_value(b)
        c = self.get_value(c)
        result = (b + c) % 32768
        self.set_value(a, result)
        self.counter += 4

    def mult(self):
        # mult: 10 a b c
        #   store into <a> the product of <b> and <c> (modulo 32768)
        a = self.memory[self.counter + 1]
        b, c = [self.get_value(x) for x in self.memory[self.counter + 2:self.counter + 4]]
        self.set_value(a, (b * c) % 32768)
        self.counter += 4

    def mod(self):
        # mod: 11 a b c
        #   store into <a> the remainder of <b> divided by <c>
        a = self.memory[self.counter + 1]
        b, c = [self.get_value(x) for x in self.memory[self.counter + 2:self.counter + 4]]
        self.set_value(a, b % c)
        self.counter += 4

    def and_opr(self):
        # and: 12 a b c
        #   stores into <a> the bitwise and of <b> and <c>
        a = self.memory[self.counter + 1]
        b, c = [self.get_value(x) for x in self.memory[self.counter + 2:self.counter + 4]]
        self.set_value(a, b & c)
        self.counter += 4

    def or_opr(self):
        # or: 13 a b c
        #   stores into <a> the bitwise or of <b> and <c>
        a = self.memory[self.counter + 1]
        b, c = [self.get_value(x) for x in self.memory[self.counter + 2:self.counter + 4]]
        self.set_value(a, b | c)
        self.counter += 4

    def not_opr(self):
        # not: 14 a b
        #   stores 15-bit bitwise inverse of <b> in <a>
        a = self.memory[self.counter + 1]
        b = self.get_value(self.memory[self.counter + 2])
        self.set_value(a, ~b % 32768)
        self.counter += 3

    def rmem(self):
        # rmem: 15 a b
        #   read memory at address <b> and write it to <a>
        a = self.memory[self.counter + 1]
        b = self.get_value(self.memory[self.counter + 2])
        self.set_value(a, self.memory[b])
        self.counter += 3

    def wmem(self):
        # wmem: 16 a b
        #   write the value from <b> into memory at address <a>
        a, b = [self.get_value(x) for x in self.memory[self.counter + 1:self.counter + 3]]
        self.set_value(a, b)
        self.counter += 3

    def call(self):
        # call: 17 a
        #   write the address of the next instruction to the stack and jump to <a>
        a = self.get_value(self.memory[self.counter + 1])
        self.stack.append(self.counter + 2)
        self.counter = a

    def ret(self):
        # ret: 18
        #   remove the top element from the stack and jump to it; empty stack = halt
        self.counter = self.stack.pop()

    def out(self):
        # out: 19 a
        #   write the character represented by ascii code <a> to the terminal
        a = self.get_value(self.memory[self.counter + 1])
        print(chr(a), end='')
        self.counter += 2

    def in_opr(self):
        # in: 20 a
        #   read a character from the terminal and write its ascii code to <a>;
        #   it can be assumed that once input starts, it will continue until a
        #   newline is encountered; this means that you can safely read whole
        #   lines from the keyboard and trust that they will be fully read
        if len(self.input_buffer) == 0:
            self.input_buffer = list(input('input: '))

            self.input_buffer.append('\n')
            self.command_log.write(''.join(self.input_buffer))
        a = self.memory[self.counter + 1]
        b = ord(self.input_buffer.pop(0))
        self.set_value(a, b)
        self.counter += 2

    def noop(self):
        # noop: 21
        #   no operation
        self.counter += 1


class VirtualMachineDis(VirtualMachine):

    def __init__(self):
        super().__init__()
        self.dis_file = Path('challenge.dis').open('w')

    def run(self):
        self.running = True
        while self.running:
            try:
                self.dis_file.write(f'{self.counter} - ')
                self.operations[self.memory[self.counter]]()
            except KeyError:
                self.dis_file.write(f'{self.memory[self.counter]} - {chr(self.memory[self.counter])}')
                self.counter += 1
            except IndexError:
                self.running = False

    def get_value(self, n: int):
        if n > 32767:
            return f'reg{n-32768}'
        return n

    def halt(self):
        # halt: 0
        #   stop execution and terminate the program
        self.dis_file.write('halt\n')
        self.counter += 1

    def set_opr(self):
        # set: 1 a b
        #   set register <a> to the value of <b>
        a, b = self.memory[self.counter+1: self.counter+3]
        a = f'reg{a-32768}'
        b = self.get_value(b)
        # self.set_value(a, b)
        self.dis_file.write(f'set: {a=} {b=}\n')
        self.counter += 3

    def push(self):
        # push: 2 a
        #   push <a> onto the stack
        a = self.get_value(self.memory[self.counter + 1])
        # self.stack.append(a)
        self.dis_file.write(f'push: {a=}\n')
        self.counter += 2

    def pop(self):
        # pop: 3 a
        #   remove the top element from the stack and write it into <a>; empty stack = error
        a = self.get_value(self.memory[self.counter + 1])
        # self.set_value(a, self.stack.pop())
        self.dis_file.write(f'pop: {a=}\n')
        self.counter += 2

    def eq(self):
        # eq: 4 a b c
        #   set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise
        a = self.get_value(self.memory[self.counter + 1])
        b, c = [self.get_value(x) for x in self.memory[self.counter + 2:self.counter + 4]]
        # self.set_value(a, 1 if b == c else 0)
        self.dis_file.write(f'eq: {a=} {b=} {c=}\n')
        self.counter += 4

    def gt(self):
        # gt: 5 a b c
        #   set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise
        a = self.get_value(self.memory[self.counter + 1])
        b, c = [self.get_value(x) for x in self.memory[self.counter + 2:self.counter + 4]]
        # self.set_value(a, 1 if b > c else 0)
        self.dis_file.write(f'gt: {a=} {b=} {c=}\n')
        self.counter += 4

    def jmp(self):
        # jmp: 6 a
        #   jump to <a>
        a = self.memory[self.counter + 1]
        self.dis_file.write(f'jmp: {a=}\n')
        self.counter += 2

    def jt(self):
        # jt: 7 a b
        #   if <a> is nonzero, jump to <b>
        a, b = [self.get_value(x) for x in self.memory[self.counter+1:self.counter+3]]
        self.dis_file.write(f'jt: {a=} {b=}\n')
        self.counter += 3

    def jf(self):
        # jf: 8 a b
        #   if <a> is zero, jump to <b>
        a, b = [self.get_value(x) for x in self.memory[self.counter + 1:self.counter + 3]]
        self.dis_file.write(f'jf: {a=} {b=}\n')
        self.counter += 3

    def add(self):
        # add: 9 a b c
        #   assign into <a> the sum of <b> and <c> (modulo 32768)
        a, b, c = self.memory[self.counter+1: self.counter+4]
        a = self.get_value(a)
        b = self.get_value(b)
        c = self.get_value(c)
        self.dis_file.write(f'add: {a=} {b=} {c=}\n')
        self.counter += 4

    def mult(self):
        # mult: 10 a b c
        #   store into <a> the product of <b> and <c> (modulo 32768)
        a = self.memory[self.counter + 1]
        b, c = [self.get_value(x) for x in self.memory[self.counter + 2:self.counter + 4]]
        self.dis_file.write(f'mult: {a=} {b=} {c=}\n')
        self.counter += 4

    def mod(self):
        # mod: 11 a b c
        #   store into <a> the remainder of <b> divided by <c>
        a = self.memory[self.counter + 1]
        b, c = [self.get_value(x) for x in self.memory[self.counter + 2:self.counter + 4]]
        self.dis_file.write(f'mod: {a=} {b=} {c=}\n')
        self.counter += 4

    def and_opr(self):
        # and: 12 a b c
        #   stores into <a> the bitwise and of <b> and <c>
        a = self.memory[self.counter + 1]
        b, c = [self.get_value(x) for x in self.memory[self.counter + 2:self.counter + 4]]
        self.dis_file.write(f'and: {a=} {b=} {c=}\n')
        self.counter += 4

    def or_opr(self):
        # or: 13 a b c
        #   stores into <a> the bitwise or of <b> and <c>
        a = self.memory[self.counter + 1]
        b, c = [self.get_value(x) for x in self.memory[self.counter + 2:self.counter + 4]]
        self.dis_file.write(f'or: {a=} {b=} {c=}\n')
        self.counter += 4

    def not_opr(self):
        # not: 14 a b
        #   stores 15-bit bitwise inverse of <b> in <a>
        a = self.memory[self.counter + 1]
        b = self.get_value(self.memory[self.counter + 2])
        self.dis_file.write(f'not: {a=} {b=}\n')
        self.counter += 3

    def rmem(self):
        # rmem: 15 a b
        #   read memory at address <b> and write it to <a>
        a = self.memory[self.counter + 1]
        b = self.get_value(self.memory[self.counter + 2])
        self.dis_file.write(f'rmem: {a=} {b=}\n')
        self.counter += 3

    def wmem(self):
        # wmem: 16 a b
        #   write the value from <b> into memory at address <a>
        a, b = [self.get_value(x) for x in self.memory[self.counter + 1:self.counter + 3]]
        self.dis_file.write(f'wmem: {a=} {b=}\n')
        self.counter += 3

    def call(self):
        # call: 17 a
        #   write the address of the next instruction to the stack and jump to <a>
        a = self.get_value(self.memory[self.counter + 1])
        self.dis_file.write(f'call: {a=}\n')
        self.counter += 2

    def ret(self):
        # ret: 18
        #   remove the top element from the stack and jump to it; empty stack = halt
        self.dis_file.write(f'ret\n')
        self.counter += 1

    def out(self):
        # out: 19 a
        #   write the character represented by ascii code <a> to the terminal
        self.dis_file.write('out: ')
        while True:

            a = super().get_value(self.memory[self.counter + 1])
            print(chr(a), end='')
            self.dis_file.write(chr(a))
            self.counter += 2
            if self.memory[self.counter] != 19:
                break
        self.dis_file.write('\n')

    def in_opr(self):
        # in: 20 a
        #   read a character from the terminal and write its ascii code to <a>;
        #   it can be assumed that once input starts, it will continue until a
        #   newline is encountered; this means that you can safely read whole
        #   lines from the keyboard and trust that they will be fully read
        # if len(self.input_buffer) == 0:
        #     self.input_buffer = list(input('input: '))
        #
        #     self.input_buffer.append('\n')
        #     self.command_log.write(''.join(self.input_buffer))
        a = self.memory[self.counter + 1]
        # b = ord(self.input_buffer.pop(0))
        # self.set_value(a, b)
        self.dis_file.write(f'in: {a=}\n')
        self.counter += 2

    def noop(self):
        # noop: 21
        #   no operation
        self.dis_file.write(f'noop:\n')
        self.counter += 1