import pytest
from unittest import mock
from pychip.processor import Processor


@pytest.fixture(scope="function")
def proc(request):
    screen = mock.MagicMock()
    processor = Processor(screen)
    processor.reset()
    return processor


class TestProcessor:
    module_name = "pychip.processor.Processor"

    memory_params = ([b'\xdf\x43', 0xdf43], [b'\x4f\xdd', 0x4fdd], [b'\xaf\x12', 0xaf12],
                      [b'\xcf\xee', 0xcfee], [b'\x8f\xfa', 0x8ffa], [b'\xfd\x3e', 0xfd3e],)
    extract_params = ([0x0523, 0x0], [0x1fcd, 0x1], [0x2cde, 0x2], [0x3436, 0x3],
                      [0x4523, 0x4], [0x5fcd, 0x5], [0x6cde, 0x6], [0x7436, 0x7],
                      [0x8523, 0x8], [0xafcd, 0xa], [0xbcde, 0xb], [0xc436, 0xc],
                      [0xd523, 0xd], [0xefcd, 0xe], [0xfcde, 0xf])
    jp_addr_params = ([0x0001, 0x001], [0x0fff, 0xfff])

    def test_processor_reset(self, proc):
        assert proc.pc == 0x200
        assert proc.sp == 0x0
        assert proc.registers == {"v": [0] * 16, "i": 0, "s": [0]}

    @pytest.mark.parametrize(("memory", "expected"), memory_params)
    def test_get_operand(self, memory, expected, proc):
        proc.pc, proc.memory = 0, memory
        assert proc.get_operand() == expected

    @pytest.mark.parametrize(("operand", "expected"), extract_params)
    def test_extract_opcode(self, operand, expected, proc):
        proc.operand = operand
        assert proc.extract_opcode() == expected

    def test_execute_instruction(self, proc):
        proc.operand = 44
        proc.pc = 0
        proc.execute_instruction()
        assert proc.pc == 2

    @pytest.mark.parametrize(("operand", "expected"), jp_addr_params)
    def test_jp_addr(self, operand, expected, proc):
        proc.operand = operand
        proc.pc = 0
        proc.jp_addr()
        assert proc.pc == expected

    def test_call_adr(self, proc):
        proc.operand = 0x2cde
        proc.pc = 0x2cde
        proc.call_addr()
        assert proc.registers['s'][proc.sp] == 0x2cde
        assert proc.sp == 0x1
        assert proc.pc == 0xcde

    @pytest.mark.parametrize(("operand", "expected", "progress"), ([0x2cde, 0xde, 2], [0x2def, 0xfe, 0]))
    def test_se_vx_byte(self, proc, operand, expected, progress):
        proc.operand = operand
        before_pc = proc.pc
        proc.registers['v'][proc.x] = expected
        proc.se_vx_byte()
        assert proc.pc == before_pc + progress

    @pytest.mark.parametrize(("operand", "expected", "progress"), ([0x2cde, 0xde, 0], [0x2def, 0xfe, 2]))
    def test_sne_vx_byte(self, proc, operand, expected, progress):
        proc.operand = operand
        before_pc = proc.pc
        proc.registers['v'][proc.x] = expected
        proc.sne_vx_byte()
        assert proc.pc == before_pc + progress

    @pytest.mark.parametrize(("operand", "reg1", 'reg2', "progress"), ([0x3353, 0xde, 0xde, 2],
                                                                       [0x3353, 0xce, 0xfe, 0]))
    def test_se_vx_vy(self, proc, operand, reg1, reg2, progress):
        proc.operand = operand
        before_pc = proc.pc
        proc.registers['v'][proc.x] = reg1
        proc.registers['v'][proc.y] = reg2
        proc.se_vx_vy()
        assert proc.pc == before_pc + progress

    @pytest.mark.parametrize(("operand", "reg1", 'reg2', "progress"),
                             ([0x3353, 0xde, 0xde, 0], [0x3353, 0xce, 0xfe, 2]))
    def test_se_vx_vy(self, proc, operand, reg1, reg2, progress):
        proc.operand = operand
        before_pc = proc.pc
        proc.registers['v'][proc.x] = reg1
        proc.registers['v'][proc.y] = reg2
        proc.sne_vx_vy()
        assert proc.pc == before_pc + progress

    @pytest.mark.parametrize(("operand", "expected",), ([0x43de, 0xde], [0x43ce, 0xce]))
    def test_ld_vx_byte(self, proc, operand, expected):
        proc.operand = operand
        proc.ld_vx_byte()
        assert proc.registers['v'][proc.x] == expected

    @pytest.mark.parametrize(("operand", "expected",), ([0x43de, 0xde], [0x43ce, 0xce]))
    def test_add_vx_byte(self, proc, operand, expected):
        proc.operand = operand
        proc.registers['v'][proc.x] = 1
        proc.add_vx_byte()
        assert proc.registers['v'][proc.x] == expected + 1

    @pytest.mark.parametrize(("operand", "expected",), ([0x43de, 0x3de], [0xade5, 0xde5]))
    def test_ld_i_addr(self, proc, operand, expected):
        proc.operand = operand
        proc.ld_i_addr()
        assert proc.registers['i'] == expected

    @pytest.mark.parametrize(("operand", "randint", "expected",), ([0xddea, 224, 0xe0], [0xdcab, 43, 0x2b]))
    def test_rn_vx_byte(self, proc, operand, randint, expected):
        proc.operand = operand
        with mock.patch(f"{self.module_name}.get_random_number") as mock_random_number:
            mock_random_number.return_value = randint
            proc.rnd_vx_byte()
            assert proc.registers['v'][proc.x] == expected

    def test_drw_vx_vy_n(self, proc):
        proc.i = 0
        proc.operand = 0x4354
        proc.memory = [0xce, 0xfd, 0x12, 0x32, 0x41]
        proc.drw_vx_vy_n()
        assert proc.buffer[0][0] == 1

    @pytest.mark.parametrize(("operand", "vy_value",), ([0x43d0, 0x32], [0xade0, 0x43]))
    def test_logical_ops_0(self, proc, operand, vy_value):
        proc.operand = operand
        proc.registers['v'][proc.x] = 0x1
        proc.registers['v'][proc.y] = vy_value
        proc.logical_ops()
        assert proc.registers['v'][proc.x] == vy_value

    @pytest.mark.parametrize(("operand", "vx_value", "vy_value",), ([0x43d1, 0x32, 0x42], [0xade1, 0x43, 0x42]))
    def test_logical_ops_1(self, proc, operand, vx_value, vy_value):
        proc.operand = operand
        proc.registers['v'][proc.x] = vx_value
        proc.registers['v'][proc.y] = vy_value
        proc.logical_ops()
        assert proc.registers['v'][proc.x] == vx_value | vy_value

    @pytest.mark.parametrize(("operand", "vx_value", "vy_value",), ([0x45d2, 0x32, 0x42], [0xade2, 0x43, 0x42]))
    def test_logical_ops_2(self, proc, operand, vx_value, vy_value):
        proc.operand = operand
        proc.registers['v'][proc.x] = vx_value
        proc.registers['v'][proc.y] = vy_value
        proc.logical_ops()
        assert proc.registers['v'][proc.x] == vx_value & vy_value

    @pytest.mark.parametrize(("operand", "vx_value", "vy_value",), ([0x43d3, 0x32, 0x42], [0xade3, 0x43, 0x42]))
    def test_logical_ops_3(self, proc, operand, vx_value, vy_value):
        proc.operand = operand
        proc.registers['v'][proc.x] = vx_value
        proc.registers['v'][proc.y] = vy_value
        proc.logical_ops()
        assert proc.registers['v'][proc.x] == vx_value ^ vy_value

    @pytest.mark.parametrize(("operand", "vx_value", "vy_value",), ([0x42d4, 0x32, 0x42], [0xade4, 0x43, 0x42]))
    def test_logical_ops_4(self, proc, operand, vx_value, vy_value):
        proc.operand = operand
        proc.registers['v'][proc.x] = vx_value
        proc.registers['v'][proc.y] = vy_value
        proc.logical_ops()
        assert proc.registers['v'][proc.x] == vx_value + vy_value
        assert proc.registers['v'][proc.x] != vx_value + vy_value + 0xff

    @pytest.mark.parametrize(("operand", "vx_value", "vy_value",), ([0x41d5, 0x32, 0x42], [0xade5, 0x43, 0x42]))
    def test_logical_ops_5(self, proc, operand, vx_value, vy_value):
        proc.operand = operand
        proc.registers['v'][proc.x] = vx_value
        proc.registers['v'][proc.y] = vy_value
        proc.logical_ops()
        if vx_value > vy_value:
            assert proc.registers['v'][proc.x] == vx_value - vy_value
            assert proc.registers['v'][0xf] == 1
        else:
            assert proc.registers['v'][proc.x] == vx_value
            assert proc.registers['v'][0xf] == 0

    @pytest.mark.parametrize(("operand", "vx_value", "expected"), ([0x41d6, 0x32, 0x19], [0xade6, 0x43, 0x21]))
    def test_logical_ops_6(self, proc, operand, vx_value, expected):
        proc.operand = operand
        proc.registers['v'][proc.x] = vx_value
        proc.logical_ops()
        assert proc.registers['v'][proc.x] == expected

    @pytest.mark.parametrize(("operand", "vx_value", "vy_value",), ([0x41d7, 0x32, 0x42], [0xade7, 0x43, 0x42]))
    def test_logical_ops_7(self, proc, operand, vx_value, vy_value):
        proc.operand = operand
        proc.registers['v'][proc.x] = vx_value
        proc.registers['v'][proc.y] = vy_value
        proc.logical_ops()
        if vy_value > vx_value:
            expected = vy_value - vx_value
            expected &= 0xFF
            assert proc.registers['v'][proc.x] == expected
        else:
            assert proc.registers['v'][proc.x] == vx_value

    @pytest.mark.parametrize(("operand", "vx_value", "expected"), ([0x41e, 0x32, 0x64], [0xadee, 0x43, 0x86]))
    def test_logical_ops_e(self, proc, operand, vx_value, expected):
        proc.operand = operand
        proc.registers['v'][proc.x] = vx_value
        proc.logical_ops()
        assert proc.registers['v'][proc.x] == expected

    @pytest.mark.parametrize(("operand", "vx_value", "key_value", "progress"),
                             ([0x439e, 0xc, 0xc, 2], [0xad9e, 0xd, 0x6, 0]))
    def test_press_ops_9e(self, proc, operand, vx_value, key_value, progress):
        proc.operand = operand
        proc.registers['v'][proc.x] = vx_value
        proc.key_pressed = key_value
        proc.press_ops()
        assert proc.pc == 512 + progress

    @pytest.mark.parametrize(("operand", "vx_value", "key_value", "progress"),
                             ([0x43a1, 0xc, 0xc, 0], [0xada1, 0xd, 0x6, 2]))
    def test_press_ops_ee(self, proc, operand, vx_value, key_value, progress):
        proc.operand = operand
        proc.registers['v'][proc.x] = vx_value
        proc.key_pressed = key_value
        proc.press_ops()
        assert proc.pc == 512 + progress

    def test_sys_ops(self, proc):
        proc.operand = 0x00e0
        proc.buffer[5][5] = 1
        proc.sys_ops()
        assert proc.buffer[5][5] == 0

    def test_sys_ops(self, proc):
        proc.operand = 0x00ee
        proc.registers['s'] = [0xdef]
        proc.sys_ops()
        assert proc.buffer[5][5] == 0
