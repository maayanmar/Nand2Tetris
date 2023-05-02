"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs 
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    SYMBOLS_DICT = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
                    '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#'}
                    
    KEYWORDS_DICT = {'class', 'constructor', 'function', 'method', 'field',
                     'static', 'var', 'int', 'char', 'boolean', 'void', 'true',
                     'false', 'null', 'this', 'let', 'do', 'if', 'else',
                     'while', 'return'}

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.input_stream = input_stream
        self.tokens = self.extract_tokens()
        self.token_counter = 0      # current token index
        self.current_token = None   # current token
        self.current_type = None    # current token type

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self.tokens[self.token_counter] is not None

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        self.current_token = self.get_token()
        self.current_type = self.token_type()
        
    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        token = self.current_token
        if token in self.KEYWORDS_DICT:
            return "keyword"
        elif token in self.SYMBOLS_DICT:
            return "symbol"
        elif token.isnumeric() and 0 <= int(token) <= 32767:
            return "integerConstant"
        elif token[0] == '\"' and token[-1] == '\"':
            self.current_token = token[1:-1]
            return "stringConstant"
        return "identifier"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.current_token.upper()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        return self.current_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        return self.current_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        return int(self.current_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        return self.current_token[1:-1]

    def extract_tokens(self) -> list:
        """Creates a list of tokens from the input stream.

        Returns:
            list[str]: list of tokens.
        """
        input_lines = self.input_stream.read().splitlines()
        tokens = []
        in_comment, in_string = False, False
        token, next_char = "", ""
        for line in input_lines:
            for i in range(len(line) + 1):  # for each char in line
                char, next_char = self.update_chars(i, line, next_char)
                if not in_string:
                    if char in " \t":  # meaning we are at the end of a word
                        token = self.add_and_reset_token(token, tokens)
                        continue
                    if char == "/" and next_char == "/":  # oneline comment
                        token = self.add_and_reset_token(token, tokens)
                        break
                    if in_comment:  # multiline comment check if to close it
                        in_comment, next_char = self.handle_comment(char, in_comment, next_char)
                        continue
                    elif next_char == "*" and char == "/":  # open multiline comment
                        in_comment = True
                        token = self.add_and_reset_token(token, tokens)
                    elif char == "\"":  # start of a string
                        in_string, token = self.initialize_for_string(char, token, tokens)
                    else:  # regular char check if this is a symbol
                        token = self.handle_char(char, token, tokens)
                else:  # (in_string is true) check if we are at the end of a string
                    in_string, token = self.handle_string(char, in_string, token, tokens)
            if not in_string and not in_comment:  # if we are at the end of a line
                token = self.add_and_reset_token(token, tokens)
            next_char = ""
        tokens.append(None)  # None symbolizes the end of the file
        return tokens

    @staticmethod
    def handle_comment(char, in_comment, next_char):
        if next_char == "/" and char == "*":
            in_comment = False
            next_char = ""
        return in_comment, next_char

    @staticmethod
    def initialize_for_string(char, token, tokens):
        in_string = True
        if token:
            tokens.append(token)
        token = char
        return in_string, token

    def handle_char(self, char, token, tokens):
        if char in self.SYMBOLS_DICT:
            token = self.add_and_reset_token(token, tokens)
            tokens.append(char)
        else:
            token += char
        return token

    def handle_string(self, char, in_string, token, tokens):
        """Handles the case where we are in a string."""
        if char == "\"":
            in_string = False
            token += char
            token = self.add_and_reset_token(token, tokens)
        else:
            token += char
        return in_string, token

    @staticmethod
    def update_chars(i, line, next_char):
        """ Updates the current char and the next char.

        Args:
            i (int): current index.
            line (str): current line.
            next_char (str): next char.

        Returns:
            char (str): current char.
        """
        char = next_char
        if i != len(line):
            next_char = line[i]
        else:
            next_char = ""
        return char, next_char

    @staticmethod
    def add_and_reset_token(token: str, tokens: list) -> str:
        """Adds the token to the list of tokens and resets the token.

        Args:
            token (str): current token.
            tokens (list[str]): list of tokens.

        Returns:
            str: empty string. 
        """
        if token:
            tokens.append(token)
        return ""

    def get_token(self) -> str:
        """Returns the current token.

        Returns:
            str: current token.
        """
        self.token_counter += 1
        return self.tokens[self.token_counter - 1]
