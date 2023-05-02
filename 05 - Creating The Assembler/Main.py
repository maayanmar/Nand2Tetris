"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from ast import parse
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    parser = Parser(input_file)  # parse the input file
    symbol_table = SymbolTable()
    converter = Code()  # code object - converts symbols to machine language
    address_counter = 16  # counter for assigning new variables
    label_counter = 0

    for i in range(len(parser.commands)):  # adding the L commands to the symbol table
        if parser.commands[i][0] == "(":
            symbol_table.add_entry(parser.commands[i][1:-1], i - label_counter)
            label_counter += 1

    for i in range(len(parser.commands)):  # adding varriables entries
        if parser.commands[i][0] == "@" and (not parser.commands[i][1].isdigit()) and not \
                symbol_table.contains(parser.commands[i][1:]):
            symbol_table.add_entry(parser.commands[i][1:], address_counter)
            address_counter += 1

    while parser.has_more_commands():  # write all commands
        write_command(converter, output_file, parser, symbol_table)


def write_command(converter, output_file, parser, symbol_table):
    """Writes the command to the output file."""

    if parser.command_type() == "A_COMMAND":
        value = symbol_table.get_address(parser.symbol()) if not parser.symbol().isdigit() else parser.symbol()
        output_file.write(format(int(value), "016b") + "\n")

    elif parser.command_type() == "C_COMMAND":
        is_extended = converter.is_extended_c_command(parser.comp())
        # check if the command is extended and get the right control bit
        comp_dest_jump = converter.convert_to_binary(*parser.parse_command())
        # convert the command to binary
        output_file.write("1" + is_extended + "1" + comp_dest_jump + "\n")

    parser.advance()


if "__main__" == __name__:
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
