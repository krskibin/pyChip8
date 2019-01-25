from random import randint

PROGRAM_COUNTER_START: int = 0x200
REGISTERS_NUM: int = 16
STACK_POINTER_START: int = 0x0

BUFFER_WIDTH: int = 64
BUFFER_HEIGHT: int = 32

PROGRAM_COUNTER_STEP: int = 2


class Processor:
    def __init__(self, memory):
        self.memory_controller = memory
        self.memory = memory.ram

        # registers
        self.registers = {'v': [], 'i': 0, 's': []}

        # special purpose registers (timers)
        self.timers = {'delay': 0, 'sound': 0}

        # pseudo-registers (pointers)
        self.pc = 0
        self.sp = 0
        self.operand = 0

        # screen
        self.buffer = None
        self.refresh_screen = False
        self.clear_buffer()

        # keyboard
        self.key_pressed = None

        # chip8 instructions
        self.instructions = {
            0x1: self.jp_addr,
            0x2: self.call_addr,
            0x3: self.se_vx_byte,
            0x4: self.sne_vx_byte,
            0x5: self.se_vx_vy,
            0x6: self.ld_vx_byte,
            0x7: self.add_vx_byte,
            0x9: self.sne_vx_vy,
            0xa: self.ld_i_addr,
            0xc: self.rnd_vx_byte,
            0xd: self.drw_vx_vy_n,

            0x0: self.sys_ops,
            0x8: self.logical_ops,
            0xf: self.rest_ops,
            0xE: self.press_ops
        }

    @property
    def x(self):
        return (self.operand & 0x0F00) >> 8

    @property
    def y(self):
        return (self.operand & 0x00F0) >> 4

    def clear_buffer(self):
        self.buffer = [[0] * 64 for _ in range(32)]

    def get_operand(self):
        return self.memory[self.pc] << 8 | self.memory[self.pc + 1]

    def extract_opcode(self):
        return (self.operand & 0xf000) >> 12

    def decrement_timers(self):
        if self.timers['delay'] > 0:
            self.timers['delay'] -= 1
        if self.timers['sound'] > 0:
            self.timers['sound'] -= 1

    def execute_instruction(self):
        self.operand = self.get_operand()
        opcode = self.extract_opcode()
        self.pc += PROGRAM_COUNTER_STEP
        self.instructions.get(opcode, lambda: print('worng opcode'))()
        self.decrement_timers()

    def reset(self):
        self.pc = PROGRAM_COUNTER_START
        self.sp = STACK_POINTER_START
        self.refresh_screen = False
        self.registers['v'] = [0] * REGISTERS_NUM
        self.registers['i'] = 0
        self.registers['s'] = [0]
        self.timers['delay'] = 0
        self.timers['sound'] = 0

        self.operand = 0
        self.key_pressed = 15

        self.clear_buffer()

    def sys_ops(self):
        if self.operand == 0x00E0:
            self.clear_buffer()

        elif self.operand == 0x00EE:
            self.pc = self.registers['s'].pop()
            self.sp -= 1

        else:
            self.pc = (self.operand & 0x0fff)

    def logical_ops(self):
        n = self.operand & 0x000F

        if n == 0x0000:
            self.registers['v'][self.x] = self.registers['v'][self.y]

        elif n == 0x0001:
            self.registers['v'][self.x] = self.registers['v'][self.x] | self.registers['v'][self.y]

        elif n == 0x0002:
            self.registers['v'][self.x] = self.registers['v'][self.x] & self.registers['v'][self.y]

        elif n == 0x0003:
            self.registers['v'][self.x] = self.registers['v'][self.x] ^ self.registers['v'][self.y]

        elif n == 0x0004:
            self.registers['v'][self.x] += self.registers['v'][self.y]
            if self.registers['v'][self.x] > 0xFF:
                self.registers['v'][0xF] = 1
            else:
                self.registers['v'][0xF] = 0
            self.registers['v'][self.x] &= 0xFF

        elif n == 0x0005:
            if self.registers['v'][self.x] < self.registers['v'][self.y]:
                self.registers['v'][0xF] = 0
            else:
                self.registers['v'][0xF] = 1
                self.registers['v'][self.x] -= self.registers['v'][self.y]
            self.registers['v'][self.x] &= 0xFF

        elif n == 0x0006:
            self.registers['v'][0xF] = self.registers['v'][self.x] & 0x01
            self.registers['v'][self.x] = self.registers['v'][self.x] >> 1

        elif n == 0x0007:
            if self.registers['v'][self.y] < self.registers['v'][self.x]:
                self.registers['v'][0xF] = 0
            else:
                self.registers['v'][0xF] = 1
                self.registers['v'][self.x] = self.registers['v'][self.y] - self.registers['v'][self.x]
                self.registers['v'][self.x] &= 0xFF

        elif n == 0x000E:
            self.registers['v'][0xF] = self.registers['v'][self.x] & 0x80
            self.registers['v'][self.x] = self.registers['v'][self.x] << 1

    def press_ops(self):
        operation = self.operand & 0x00FF

        key_to_check = self.registers['v'][self.x]
        if operation == 0x9E:
            if self.key_pressed == key_to_check:
                self.pc += PROGRAM_COUNTER_STEP

        if operation == 0xA1:
            if self.key_pressed != key_to_check:
                self.pc += PROGRAM_COUNTER_STEP

    def rest_ops(self):
        nn = self.operand & 0x00FF

        if nn == 0x0007:
            self.registers['v'][self.x] = self.timers['delay']

        elif nn == 0x000A:
            if self.key_pressed:
                self.registers['v'][self.x] = self.key_pressed
                return
            self.pc -= PROGRAM_COUNTER_STEP

        elif nn == 0x0015:
            self.timers['delay'] = self.registers['v'][self.x]

        elif nn == 0x0018:
            self.timers['sound'] = self.registers['v'][self.x]

        elif nn == 0x001E:
            self.registers['i'] += self.registers['v'][self.x]

        elif nn == 0x0029:
            self.registers['i'] = self.registers['v'][self.x] * 5

        elif nn == 0x0033:
            self.memory[self.registers['i']] = self.registers['v'][self.x] // 100
            self.memory[self.registers['i'] + 1] = (self.registers['v'][self.x] // 10) % 10
            self.memory[self.registers['i'] + 2] = (self.registers['v'][self.x] % 100) % 10

        elif nn == 0x0055:
            for n in range(self.x + 1):
                self.memory[self.registers['i'] + n] = self.registers['v'][n]

        elif nn == 0x0065:
            for n in range(self.x + 1):
                self.registers['v'][n] = self.memory[self.registers['i'] + n]

    def jp_addr(self):
        self.pc = self.operand & 0x0fff

    def call_addr(self):
        self.registers['s'].append(self.pc)
        self.sp += 1
        self.pc = self.operand & 0x0fff

    def se_vx_byte(self):
        if self.registers['v'][self.x] == self.operand & 0x00ff:
            self.pc += PROGRAM_COUNTER_STEP

    def sne_vx_byte(self):
        if self.registers['v'][self.x] != self.operand & 0x00ff:
            self.pc += PROGRAM_COUNTER_STEP

    def se_vx_vy(self):
        if self.registers['v'][self.x] == self.registers['v'][self.y]:
            self.pc += PROGRAM_COUNTER_STEP

    def ld_vx_byte(self):
        self.registers['v'][self.x] = self.operand & 0x00ff

    def add_vx_byte(self):
        self.registers['v'][self.x] += self.operand & 0x00ff
        self.registers['v'][self.x] &= 0xff

    def sne_vx_vy(self):
        if self.registers['v'][self.x] != self.registers['v'][self.y]:
            self.pc += PROGRAM_COUNTER_STEP

    def ld_i_addr(self):
        self.registers['i'] = self.operand & 0x0fff

    def rnd_vx_byte(self):
        value = self.operand & 0x00ff
        self.registers['v'][self.x] = value & Processor.get_random_number()

    def drw_vx_vy_n(self):
        x_pos = self.registers['v'][self.x]
        y_pos = self.registers['v'][self.y]

        self.registers['v'][0xf] = 0
        n = self.operand & 0x000f

        for y_index in range(n):
            bits = f"{self.memory[self.registers['i'] + y_index] :08b}"
            y_coord = (y_pos + y_index) % BUFFER_HEIGHT

            for x_index in range(8):
                x_coord = (x_pos + x_index) % BUFFER_WIDTH
                bit = int(bits[x_index])
                curr_bit = self.buffer[y_coord][x_coord]

                if bit == 1 and curr_bit == 1:
                    self.registers['v'][0xf] = self.registers['v'][0xf] | 1

                self.buffer[y_coord][x_coord] ^= bit
                self.refresh_screen = True

    @staticmethod
    def get_random_number():
        return randint(0, 0xff)
