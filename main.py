import struct
from pathlib import Path
from typing import List
from operations import operations


def import_file(file: Path) -> List:
    st = struct.Struct('<H')
    return [i[0] for i in st.iter_unpack(file.open('rb').read())]


if __name__ == '__main__':
    registers = [0, 0, 0, 0, 0, 0, 0, 0]
    counter = 0
    stack = []
    program = import_file(Path('challenge.bin'))
    # program = [9, 32768, 32769, 4, 19, 32768]
    print(program)
    while True:
        operation = operations[program[counter]]
        program, counter, registers, stack = operation(program, counter, registers, stack)
        # print(registers)
