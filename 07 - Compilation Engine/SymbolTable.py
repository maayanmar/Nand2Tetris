"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

TYPE_INDEX = 0
KIND_INDEX = 1
COUNTER_INDEX = 2


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.class_table = {}
        self.subroutine_table = {}
        self.kind_index_dict = {"STATIC": 0, "FIELD": 0, "ARG": 0, "VAR": 0}

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.subroutine_table = {}
        self.kind_index_dict["ARG"] = 0
        self.kind_index_dict["VAR"] = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        if kind in ["STATIC", "FIELD"]:  # check if the kind is in a class level
            self.class_table[name] = [type, kind, self.kind_index_dict[kind]]
        else:  # the kind is not in a class level
            self.subroutine_table[name] = [type, kind, self.kind_index_dict[kind]]
        self.kind_index_dict[kind] += 1  # increment kind index

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        return self.kind_index_dict[kind]

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        convert_kind = {"ARG": "argument", "VAR": "local",
                        "STATIC": "static", "FIELD": "this"}
        if name in self.subroutine_table:
            return convert_kind[self.subroutine_table[name][KIND_INDEX]]
        return convert_kind[self.class_table[name][KIND_INDEX]]

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name][TYPE_INDEX]
        return self.class_table[name][TYPE_INDEX]

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name][COUNTER_INDEX]
        return self.class_table[name][COUNTER_INDEX]

    def get_kind_and_index(self, name: str) -> tuple[str, int]:
        """this method get identifier (param name) kind and index."""
        return self.kind_of(name), self.index_of(name)

    def is_var_name(self, name: str) -> bool:
        """this method checks if identifier (param name) is var or field"""
        is_var = name in self.subroutine_table and \
            self.subroutine_table[name][KIND_INDEX] == "VAR"
        is_field = name in self.class_table and \
            self.class_table[name][KIND_INDEX] == "FIELD"
        return is_var or is_field
