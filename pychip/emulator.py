"""
Emulator main module
"""
import argparse

from screen import Screen
from memory import Memory
from processor import Processor
from disassembler import Disassembler

DEFAULT_FREQUENCY = 1

def run_dasm(memory):
    memory_size = len(memory.ram)
    dasm = Disassembler(memory)

    for _ in range(0, memory_size):
        dasm.disassembly()


def main_loop(*args, **kwargs):
    is_dasm = args[0]["disassembler"]
    rom_name = args[0]["roms"]
    frequency = args[0]["dly"] or DEFAULT_FREQUENCY
    screen_resolution = args[0]["res"]

    if kwargs.get('additional'):
        screen_resolution = kwargs['additional'][0]
        rom_name = kwargs['additional'][1]

    mem = Memory()

    if is_dasm and not rom_name:
        print("Please select rom file")
        return

    if rom_name:
        mem.load_rom(rom_name)

        if is_dasm:
            run_dasm(mem)
            return

    proc = Processor(mem)
    proc.reset()

    screen = Screen()
    if not screen.window.file_name:
        screen.window.no_file()

    if screen_resolution:
        screen.init_display(proc, res=screen_resolution)
    else:
        screen.init_display(proc)
    screen.draw_pixel()

    screen.window.file_name = rom_name

    def execute_program():
        proc.execute_instruction()
        screen.draw_pixel()
        if screen.window.is_sound.get():
            screen.play_sound()

        if screen.window.res:
            new_resolution = screen.window.res
            screen.window.destroy()
            main(new_resolution, screen.window.file_name)

        screen.window.after(frequency, execute_program)

    execute_program()
    screen.window.mainloop()


def main(*arg):
    parser = argparse.ArgumentParser(description="Chip8 emulator")
    parser.add_argument('-f', '--file', help='use to provide roms file ', dest="roms", type=str)
    parser.add_argument('-d', '--disassembler', action="store_true", help="run disassembler for given roms file")
    parser.add_argument('-r', '--res', help='set CHIP-8 screen resolution', dest="res", type=str)
    parser.add_argument('-t', '--time', help='set emulation delay time', dest="dly", type=int)
    parser.add_argument('-s', '--sound', help='set sound on/off', dest='snd', type=bool)

    args = parser.parse_args()
    main_loop(vars(args), additional=arg)


if __name__ == '__main__':
    main()
