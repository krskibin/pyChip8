from .opcode_table import OPCODE_TABLE


class Disassembler:
    def __init__(self, memory):
        self.memory: bytearray = memory
        self.pc: int = 0x0
        self.args_func_table: dict = {
            0x0000: self.get_nnn_args,
            0x00E0: self.get_no_args,
            0x00EE: self.get_no_args,
            0x1000: self.get_nnn_args,
            0x2000: self.get_nnn_args,
            0x3000: self.get_xkk_args,
            0x4000: self.get_xya_args,
            0x5000: self.get_xkk_args,
            0x6000: self.get_xkk_args,
            0x7000: self.get_xkk_args,
            0x8000: self.get_xya_args,
            0x8001: self.get_xya_args,
            0x8002: self.get_xya_args,
            0x8003: self.get_xya_args,
            0x8004: self.get_xya_args,
            0x8005: self.get_xya_args,
            0x8006: self.get_xya_args,
            0x8007: self.get_xya_args,
            0x800E: self.get_xya_args,
            0x9000: self.get_xya_args,
            0xA000: self.get_i3n_args,
            0xB000: self.get_nnn_args,
            0xC000: self.get_xkk_args,
            0xD000: self.get_xyn_args,
            0xE09E: self.get_xaa_args,
            0xE0A1: self.get_xaa_args,
            0xF007: self.get_xa1_args,
            0xF00A: self.get_xa2_args,
            0xF015: self.get_xa3_args,
            0xF018: self.get_xa4_args,
            0xF01E: self.get_xa5_args,
            0xF029: self.get_xa6_args,
            0xF033: self.get_xa7_args,
            0xF055: self.get_xa8_args,
            0xF065: self.get_xa9_args
        }

    def get_opcode(self) -> int:
        return self.memory[self.pc] << 8 | self.memory[self.pc + 1]

    @staticmethod
    def mask_opcode(opcode: int) -> int:
        if (opcode & 0xF000) in [0x0000, 0xE000, 0xF000]:
            opcode &= 0xF0FF
        elif (opcode & 0xF000) in [0x8000]:
            opcode &= 0xF00F
        else:
            opcode &= 0xF000
        return opcode

    @staticmethod
    def lookup_opcode(opcode) -> str:
        return OPCODE_TABLE.get(opcode, "????")

    def find_args(self, opcode):
        masked_opcode = Disassembler.mask_opcode(opcode)
        return self.args_func_table.get(masked_opcode, self.__unhandled)(opcode)

    def disassembly(self):
        opcode = self.get_opcode()
        args = self.find_args(opcode)
        lookup_opcode = Disassembler.lookup_opcode(Disassembler.mask_opcode(opcode))
        print(f'{hex(self.pc)}:  {hex(opcode)[2:]}\t{lookup_opcode}\t{args}')

    def __unhandled(self, *args):
        return '????'

    def get_nnn_args(self, opcode):
        nnn = hex(opcode & 0xFFF)[2:]
        return f'  \t{nnn}'

    def get_no_args(self, *args):
        return ''

    def get_xkk_args(self, opcode):
        x = opcode >> 8 & 0x0f
        kk = opcode & 0x00ff
        return f'V{x:x}\t{hex(kk)}'

    def get_xya_args(self, opcode):
        x = hex(opcode & 0x0f00)[2]
        y = hex(opcode & 0x00f0)[2]
        return f'V{x}, V{y}'

    def get_i3n_args(self, opcode):
        nnn = hex(opcode & 0xfff)[2:]
        return f'I,\t{nnn}'

    def get_xaa_args(self, opcode):
        x = hex(opcode & 0x0f00)[2]
        return f'V{x}'

    def get_xyn_args(self, opcode):
        x = hex(opcode & 0x0f00)[2]
        y = hex(opcode & 0x00f0)[2]
        n = opcode & 0x000f
        return f'V{x}, V{y}  {n:x}'

    def get_xa1_args(self, opcode):
        x = hex(opcode & 0x0f00)[2]
        return f'V{x}, DT'

    def get_xa2_args(self, opcode):
        x = hex(opcode & 0x0f00)[2]
        return f'V{x}, K'

    def get_xa3_args(self, opcode):
        x = hex(opcode & 0x0f00)[2]
        return f'DT, V{x}'

    def get_xa4_args(self, opcode):
        x = hex(opcode & 0x0f00)[2]
        return f'ST, V{x}'

    def get_xa5_args(self, opcode):
        x = hex(opcode & 0x0f00)[2]
        return f'I, V{x}'

    def get_xa6_args(self, opcode):
        x = hex(opcode & 0x0f00)[2]
        return f'F, V{x}'

    def get_xa7_args(self, opcode):
        x = hex(opcode & 0x0f00)[2]
        return f'B, V{x}'

    def get_xa8_args(self, opcode):
        x = hex(opcode & 0x0f00)[2]
        return f'[I], V{x}'

    def get_xa9_args(self, opcode):
        x = hex(opcode & 0x0f00)[2]
        return f'V{x}, [I]'

    def get_unh_args(self, *args):
        return f'unhandled'
