import pytest
from pychip.disassembler import Disassembler


@pytest.fixture(scope="function")
def dasm(request):
    mem = bytearray(b'\x6f\x22\x00\x00\x00')
    return Disassembler(mem)


@pytest.mark.usefixtures('dasm')
class TestDisassembler:
    mask_params = ([0xFDEE, 0xF0EE], [0xE337, 0xE037],
                       [0x0ABC, 0x00BC], [0x8DCA, 0x800A], [0xAACE, 0xA000])
    lookup_params = ([0x00E0, "CLS "], [0x00EE, "RET "], [0x0000, "SYS "],
                     [0x1000, "JP  "], [0x2000, "CALL"], [0x3000, "SE  "],
                     [0x4000, "SNE "], [0x5000, "SE  "], [0x6000, "LD  "],
                     [0x7000, "ADD "], [0x8000, "LD  "], [0x8001, "OR  "],
                     [0x8002, "AND "], [0x8003, "XOR "], [0x8004, "ADD "],
                     [0x8005, "SUB "], [0x8006, "SHR "], [0x8007, "SUBN"],
                     [0x800E, "SHL "], [0x9000, "SNE "], [0xA000, "LD  "],
                     [0xB000, "JP  "], [0xC000, "RND "], [0xD000, "DRW "],
                     [0xE09E, "SKP "], [0xE0A1, "SKNP"], [0xF007, "LD  "],
                     [0xF00A, "LD  "], [0xF015, "LD  "], [0xF018, "LD  "],
                     [0xF01E, "ADD "], [0xF029, "LD  "], [0xF033, "LD  "],
                     [0xF055, "LD  "], [0xF065, "LD  "])

    def test_opcode(self, dasm):
        assert dasm.get_opcode() == 0x6f22

    @pytest.mark.parametrize(("opcode", "expected"), mask_params)
    def test_opcode_mask(self, opcode, expected, dasm):
        assert dasm.mask_opcode(opcode) == expected

    @pytest.mark.parametrize(("opcode", "expected"), lookup_params)
    def test_lookup_opcode(self, opcode, expected, dasm):
        assert dasm.lookup_opcode(opcode) == expected

    def test_find_args(self, dasm):
        assert dasm.find_args(0x6f22) == 'Vf\t0x22'

    def test_disassembly(self, dasm):
        dasm.disassembly()

    def test_get_nnn_args(self, dasm):
        assert dasm.get_nnn_args(0x0ADC) == "  \tadc"
        assert dasm.get_nnn_args(0x0123) == "  \t123"

    def test_get_no_args(self, dasm):
        assert dasm.get_no_args() == ''

    def test_get_unh_args(self, dasm):
        assert dasm.get_unh_args(0x1ADC) == "unhandled"

    def test_get_xkk_args(self, dasm):
        assert dasm.get_xkk_args(0x23cd) == "V3\t0xcd"

    def test_get_xya_args(self, dasm):
        assert dasm.get_xya_args(0xfdac) == "Vd, Va"

    def test_get_i3n_args(self, dasm):
        assert dasm.get_i3n_args(0xdaec) == "I,\taec"

    def test_get_xaa_args(self, dasm):
        assert dasm.get_xaa_args(0xcdea) == "Vd"

    def test_get_xyn_args(self, dasm):
        assert dasm.get_xyn_args(0xacda) == "Vc, Vd  a"

    def test_get_xa1_args(self, dasm):
        assert dasm.get_xa1_args(0xdcea) == "Vc, DT"

    def test_get_xa2_args(self, dasm):
        assert dasm.get_xa2_args(0xfeaa) == "Ve, K"

    def test_get_xa3_args(self, dasm):
        assert dasm.get_xa3_args(0xfcea) == "DT, Vc"

    def test_get_xa4_args(self, dasm):
        assert dasm.get_xa4_args(0xf1ea) == "ST, V1"

    def test_get_xa5_args(self, dasm):
        assert dasm.get_xa5_args(0xf2ea) == "I, V2"

    def test_get_xa6_args(self, dasm):
        assert dasm.get_xa6_args(0xcdea) == "F, Vd"

    def test_get_xa7_args(self, dasm):
        assert dasm.get_xa7_args(0xc5ea) == "B, V5"

    def test_get_xa8_args(self, dasm):
        assert dasm.get_xa8_args(0xc6da) == "[I], V6"

    def test_get_xa9_args(self, dasm):
        assert dasm.get_xa9_args(0x6dea) == "Vd, [I]"
