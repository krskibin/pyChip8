import os
from setuptools import setup


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setup(
    name="chip8-python",
    version="0.0.4",
    author="krskibin",
    author_email="",
    description="Chip8 emulator written in python",
    license="",
    keywords="emulation emulator chip8",
    url="",
    packages=['an_example_pypi_project', 'tests'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
    ],
)
