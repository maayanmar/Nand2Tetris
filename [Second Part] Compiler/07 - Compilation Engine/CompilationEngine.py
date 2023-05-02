"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import SymbolTable as st
import VMWriter


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """
    OPERATORS_DICT = {'+': 'add',
                      '-': 'sub',
                      '*': 'call Math.multiply 2',
                      '/': 'call Math.divide 2',
                      '&': 'and',
                      '|': 'or',
                      '<': 'lt',
                      '>': 'gt',
                      '=': 'eq'}

    UNARY_OPERATORS_DICT = {'-': 'neg',
                            '~': 'not',
                            '^': '<<',
                            '#': '>>'}

    def __init__(self, input_stream, output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.call_statements_dict = {"if": self.compile_if,
                                     "let": self.compile_let,
                                     "while": self.compile_while,
                                     "do": self.compile_do,
                                     "return": self.compile_return}
        self.tokenizer = input_stream
        self.writer = VMWriter.VMWriter(output_stream)
        self.symbol_table = None
        self.curr_class = None
        self.labels_counter = 0

    def get_labels(self, state, num=1) -> list[str]:
        """this function creates string labels with unique numbers"""
        self.labels_counter += 1
        return [f'{state}_{self.labels_counter - 1}'] if num == 1 else \
            [f'{state}_true_{self.labels_counter - 1}',
             f'{state}_false_{self.labels_counter - 1}']

    def advance_tokenizer(self, num=1) -> None:
        """ advance the tokenizer without writing the next tokens """
        for i in range(num):
            self.tokenizer.advance()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.symbol_table = st.SymbolTable()
        self.advance_tokenizer(2)  # skip "None" , "class"
        self.curr_class = self.tokenizer.current_token
        self.advance_tokenizer(2)  # skip identifier , "{"
        while self.tokenizer.current_token in ["static", "field"]:
            self.compile_var_dec()
        while self.tokenizer.current_token in ["function", "constructor", "method"]:
            self.compile_subroutine()

    def get_symbol_declaration(self) -> tuple[str, str, str]:
        """ This method gets the declaration details and returns it"""
        kind = self.tokenizer.current_token
        self.advance_tokenizer()
        typ = self.tokenizer.current_token
        self.advance_tokenizer()
        var_name = self.tokenizer.current_token
        self.advance_tokenizer()
        return kind, typ, var_name

    def get_next_tokens(self, num=1) -> list[str]:
        """ Returns a list of the next num tokens (and advance)"""
        output = []     # list of tokens
        for i in range(num):
            output.append(self.tokenizer.current_token)
            self.advance_tokenizer()
        return output   # return list of num next tokens

    def compile_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        [kind, typ, var_name] = self.get_next_tokens(3)
        self.symbol_table.define(var_name, typ, kind.upper())  # define the variable
        while self.tokenizer.current_token == ",":  # multiple var declarations
            self.advance_tokenizer()    # advance and get var name
            var_name = self.tokenizer.current_token
            self.symbol_table.define(var_name, typ, kind.upper())  # define the variable
            self.advance_tokenizer()    # proceed to , or ;
        self.advance_tokenizer()        # skip over ';'

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.symbol_table.start_subroutine()
        # note that return type is not used at all. (unneeded)
        [subroutine_type, return_type, subroutine_name] = self.get_next_tokens(3)
        if subroutine_type == 'method':
            self.symbol_table.define('this', self.curr_class, 'ARG')
        self.advance_tokenizer()  # skip "("
        self.compile_parameter_list()
        self.advance_tokenizer()  # skip ")"
        self.compile_subroutine_body(subroutine_type, subroutine_name)

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        if self.tokenizer.current_token != ")":
            [typ, name] = self.get_next_tokens(2)
            self.symbol_table.define(name, typ, 'ARG')
        while self.tokenizer.current_token != ")":
            self.advance_tokenizer()    # skip ","
            [typ, name] = self.get_next_tokens(2)
            self.symbol_table.define(name, typ, 'ARG')

    def compile_subroutine_body(self, subroutine_type, subroutine_name) -> None:
        """Compile a subroutine body including the enclosing "{}"""
        self.advance_tokenizer()    # skip "{"
        while self.tokenizer.current_token == "var":
            self.compile_var_dec()
        self.writer.write_function(f'{self.curr_class}.{subroutine_name}',
                                   self.symbol_table.var_count("VAR"))
        if subroutine_type == "constructor":
            self.writer.write_push("constant", self.symbol_table.var_count("FIELD"))
            self.writer.write_call("Memory.alloc", 1)
            self.writer.write_pop("pointer", 0)
        elif subroutine_type == "method":
            self.writer.write_push('argument', 0)
            self.writer.write_pop('pointer', 0)
        self.compile_statements()
        self.advance_tokenizer()    # skip "}"

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        while self.tokenizer.current_token in self.call_statements_dict:
            self.call_statements_dict[self.tokenizer.current_token]()
            # call the right compile statement method

    def compile_do(self) -> None:
        """Compiles a do statement."""

        self.advance_tokenizer()          # skip do
        self.compile_subroutine_call()
        self.writer.write_pop('temp', 0)  # dump garbage value
        self.advance_tokenizer()          # skip ";"

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.advance_tokenizer()          # skip "let"
        segment, index = self.symbol_table.get_kind_and_index(self.tokenizer.current_token)
        self.advance_tokenizer()          # skip "VarName"
        if self.tokenizer.current_token == "[":
            self.compile_let_array(index, segment)
        else:
            self.advance_tokenizer()    # skip "="
            self.compile_expression()
            self.writer.write_pop(segment, index)
        self.advance_tokenizer()        # skip ";"

    def compile_let_array(self, index, segment):
        """this method handles array indexing inorder to
        set values in array."""
        self.writer.write_push(segment, index)
        self.expression_brackets()  # skip "[" ~compile~ and skip "]"
        self.writer.write_arithmetic("add")
        self.advance_tokenizer()    # skip "="
        self.compile_expression()
        self.writer.write_pop('temp', 0)
        self.writer.write_pop('pointer', 1)
        self.writer.write_push('temp', 0)
        self.writer.write_pop('that', 0)

    def expression_brackets(self):
        """ This method, skip "[" | "(" compiles expression and
        skip "]" | ")" ."""
        self.advance_tokenizer()  # skip "["
        self.compile_expression()
        self.advance_tokenizer()  # skip "]"

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.advance_tokenizer(2)  # skips "while ("
        [label_true, label_false] = self.get_labels("while", 2)  # get labels & increase
        self.writer.write_label(label_true)
        self.compile_expression()  # compile expression
        self.writer.write_arithmetic("not")  # not expression
        self.advance_tokenizer(2)  # skips ")" , "{"
        self.writer.write_if(label_false)  # if not expression jump to false label
        self.compile_statements()  # compile statements
        self.advance_tokenizer()   # skips "}"
        self.writer.write_goto(label_true)    # goto expression
        self.writer.write_label(label_false)  # false label

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.advance_tokenizer()  # skips "return"
        if self.tokenizer.current_token != ";":
            self.compile_expression()
        else:                     # means we are at void function
            self.writer.write_push('constant', 0)
        self.writer.write_return()
        self.advance_tokenizer()  # skips ";""

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.advance_tokenizer()           # skips "if"
        self.expression_brackets()         # skip "(" compile expression and skip ")"
        self.writer.write_arithmetic("not")     # not expression
        [end_label, false_label] = self.get_labels("if", 2)
        self.writer.write_if(false_label)  # if not expression jump to false
        self.compile_statements_scope()
        self.writer.write_goto(end_label)  # skip else statements
        self.writer.write_label(false_label)
        if self.tokenizer.current_token == "else":
            self.advance_tokenizer()       # skip "else"
            self.compile_statements_scope()
        self.writer.write_label(end_label)

    def compile_statements_scope(self):
        """ skip "{", compile statements and skip "}"."""
        self.advance_tokenizer()
        self.compile_statements()
        self.advance_tokenizer()

    def compile_subroutine_call(self) -> None:
        """ Compiles a function call within a subroutine"""
        [subroutine_name] = self.get_next_tokens()
        is_method = 0               # flag for adding parameter (this) to methods.
        if self.tokenizer.current_token != ".":
            is_method = 1           # subroutine is a method
            self.writer.write_push("pointer", 0)
            subroutine_name = self.curr_class + "." + subroutine_name
        else:                       # the subroutine is within another module
            if self.symbol_table.is_var_name(subroutine_name):
                is_method = 1       # subroutine is a method
                self.writer.write_push(*self.symbol_table.get_kind_and_index(subroutine_name))
                subroutine_name = self.symbol_table.type_of(subroutine_name)
            [dot, name] = self.get_next_tokens(2)
            subroutine_name += dot + name
        self.advance_tokenizer()    # skip "("
        parameters = self.compile_expression_list() + is_method  # set parameters count (int)
        self.advance_tokenizer()    # skip ")"
        self.writer.write_call(subroutine_name, parameters)

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.compile_term()
        while self.tokenizer.current_token in self.OPERATORS_DICT:
            [operator] = self.get_next_tokens()
            self.compile_term()
            self.writer.write_arithmetic(self.OPERATORS_DICT[operator])

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        if self.tokenizer.current_token == "(":
            self.expression_brackets()
            return
        if self.tokenizer.current_token in self.UNARY_OPERATORS_DICT:
            self.handle_unary_op()
            return
        if self.tokenizer.tokens[self.tokenizer.token_counter] in "(.":
            self.compile_subroutine_call()
            return
        if self.tokenizer.current_type == "integerConstant":
            self.writer.write_push("constant", self.tokenizer.current_token)
        elif self.tokenizer.current_type == "stringConstant":
            self.handle_string()
        elif self.tokenizer.current_token in ["true", "false", "null"]:
            self.compile_jack_constants()
        elif self.tokenizer.current_token == "this":
            self.writer.write_push("pointer", 0)  # push this
        else:
            self.compile_identifier()
            return
        self.advance_tokenizer()

    def handle_unary_op(self):
        [unary_operator] = self.get_next_tokens()
        self.compile_term()
        self.writer.write_arithmetic(self.UNARY_OPERATORS_DICT[unary_operator])

    def compile_identifier(self):
        """ handles identifier push and array cases"""
        self.writer.write_push(*self.symbol_table.get_kind_and_index(
            self.tokenizer.current_token))
        self.advance_tokenizer()  # skip the identifier
        if self.tokenizer.current_token == "[":
            self.expression_brackets()
            self.writer.write_arithmetic("add")
            self.writer.write_pop('pointer', 1)
            self.writer.write_push('that', 0)

    def compile_jack_constants(self):
        """push jack constants to in their vm form"""
        self.writer.write_push('constant', 0)
        if self.tokenizer.current_token == "true":
            self.writer.write_arithmetic("not")

    def handle_string(self):
        """handle string push and assign"""
        string_len = len(self.tokenizer.current_token)
        self.writer.write_push('constant', string_len)
        self.writer.write_call('String.new', 1)
        for i in range(string_len):
            self.writer.write_push('constant', ord(self.tokenizer.current_token[i]))
            self.writer.write_call('String.appendChar', 2)

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        parameters = 0
        if self.tokenizer.current_token != ")":
            self.compile_expression()  # compile first expression
            parameters += 1
        while self.tokenizer.current_token != ")":
            self.advance_tokenizer()  # skip ","
            self.compile_expression()
            parameters += 1
        return parameters
