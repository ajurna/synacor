import struct
from pathlib import Path
from typing import List
from vm import VirtualMachine, VirtualMachineDis


commands = Path('bot_commands.txt').open().readlines()

if __name__ == '__main__':
    vm = VirtualMachineDis()
    vm.import_file(Path('challenge.bin'))
    vm.add_commands(commands)
    vm.run()

