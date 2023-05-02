"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

FIRST_LETTERS = "@DAM(0"  # all the first letters of valid commands.

CMD_DICT = {"@": "A_COMMAND",
            "A": "C_COMMAND",
            "D": "C_COMMAND",
            "M": "C_COMMAND",
            "0": "C_COMMAND",
            "(": "L_COMMAND"
            }


class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        input_lines = input_file.read().replace(' ', '').splitlines()
        # remove spaces and split lines
        self.commands = [i.partition("/")[0] for i in input_lines if i and i[0] in FIRST_LETTERS] + ["end"]
        # remove comments and empty lines
        # "end" is the no more commands marker.
        self.line_index = 0
        self.current_command = self.commands[0]

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.commands[self.line_index] != "end"

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        if self.has_more_commands():
            self.line_index += 1
            self.current_command = self.commands[self.line_index]

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        return CMD_DICT[self.current_command[0]]

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        typ = self.command_type()
        if typ == "A_COMMAND":
            return self.current_command[1:]
        elif typ == "L_COMMAND":
            return self.current_command[1:-1]

    # Note that the following 3 methods are not used in the assembler,
    # but are made available for the sake of completeness API.
    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        current_command = self.current_command
        for i in range(len(current_command)):
            # find the first '=' | ';' return the string before '=' or 'null' if ';' is found
            if current_command[i] == '=':
                return current_command[:i]
            elif current_command[i] == ';':
                return 'null'

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        current_command = self.current_command
        for i in range(len(current_command)):
            if current_command[i] == '=':
                return current_command[i + 1:]
            elif current_command[i] == ';':
                return current_command[:i]

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        current_command = self.current_command
        for i in range(len(current_command)):
            if current_command[i] == ';':
                return current_command[i + 1:]
            elif current_command[i] == '=':
                return 'null'

    def parse_command(self) -> tuple[str, str, str]:
        """
        Returns:
            list[str]: [comp, dest, jump]
        """
        # Naive implementation:
        # return [self.comp(), self.dest(), self.jump()]
        # Optimized implementation:
        comp, dest, jump = 'null', 'null', 'null'
        for i in range(len(self.current_command)):
            if self.current_command[i] == '=':
                dest = self.current_command[:i]
                comp = self.current_command[i + 1:]
                break
            elif self.current_command[i] == ';':
                comp = self.current_command[:i]
                jump = self.current_command[i + 1:]
                break
        return comp, dest, jump
