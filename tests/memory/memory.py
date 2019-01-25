import pytest
from unittest import mock
from pychip.memory import Memory


@pytest.fixture(scope="function")
def mem(request):
    filename = mock.MagicMock()
    processor = Memory(filename)
    processor.reset()
    return processor


class TestMemory:
    def test_load_fonts(self, mem):
        mem.ram = bytearray(5)
        mem.load_fonts()
        assert mem.ram == "b\0xF0b\0x90b\0x90b\0x90\b0xF1"

    def test_load_file(self, mem):
        mem.ram = bytearray(5)
        with mock.patch(f"{Memory.mem.filename}") as mock_filename:
            mock_filename.return_value = "b\0x43b\0x43b\0x43b\0x43b\0x43"
            mem.load_ram()
            assert mem.ram == "b\0x43b\0x43b\0x43b\0x43b\0x43"

    def test_clear_ram(self, mem):
        mem.ram = bytearray(5)
        mem.load_fonts()
        assert mem.ram == "b\0x0b\0x0b\0x0b\0x0b\0x0b\0x0"