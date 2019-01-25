![logo](resources/pyChip8.png)
> Python Chip 8 emulator

## Table of Contents
- [Introduction](#introduction)
- [Dependancies](#dependancies)
- [Installation](#installation)
- [Args](#args)
- [Tests](#tests)

## Introduction
PyChip8 is a CHIP-8 computer interpreter written in Python, which allows you to run programs prepared for this machine directly on your computer. 

## Dependancies:
- Linux/Unix based OS
- Python 3.7 :snake:
- Pipenv (optional)

## Installation:
1. Using Pipenv:
* Open termianl install pipenv and go to project directory
* In bash terminal write `pipenv install` and then `pipenv shell`
* To run project use `python pyChip8` command
* Use `deactivate` command to kill pipenv shell :skull: 
2. Using pip:
* Open termianl and go to project directory
* Use `pip3 install -r requirements.txt` to install all dependencies
* To run project use `python3 pyChip8` command
3. Using pip with virtualenv:
* Type in project directory `virtualenv venv`
* Activate virtual environment by `source venv/bin/activate` command
* Use `pip3 install -r requirements.txt` to install all dependencies
* To run project use `python3 pyChip8` command
* Use `deactivate` command to kill virtualenv :skull: 

# Args
```
usage: pychip [-h] [-f ROMS] [-d]

Chip8 emulator

optional arguments:
  -h, --help            Show this help message and exit
  -f ROMS, --file ROMS  Use to provide roms file
  -d, --disassemler     Runs disassembler for given roms file
```

# Tests
1. Install pytest `pip install pytest`
2. Run `pytest` in root directory

App tested on linux, macOS
