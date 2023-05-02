import typing

""" Common Assembly Code for Arithmetic Commands"""

POP_Y = "@SP\nM=M-1\nA=M\nD=M\n"  # pop y from stack
DXY = "A=A-1\nD=M-D\n"  # D = x-y
SET_TRUE = "@SP\nA=M-1\nM=-1\n"  # set the stack top to be true
SET_FALSE = "@SP\nA=M-1\nM=0\n"  # set the stack top to be false

HANDLE_DIFFERENT_SIGNS = "@Y_POSITIVE\nD;JGT\n@SP\nA=M-1\nD=M\n@BIGGER_THAN\nD;JGT\n" + \
                         "@SUBTRACT\n0;JMP\n(Y_POSITIVE)\n@SP\nA=M-1\nD=M\n@LOWER_THAN\nD;JLE\n(" \
                         "SUBTRACT)\n@SP\nA=M\nD=M\n "
JUMP_IF_BIGGER = "@BIGGER_THAN\nD;JGT\n"
JUMP_IF_NOT_LOWER = "@BIGGER_THAN\nD;JGE\n"
LOWER_MARK = "(LOWER_THAN)\n"
BIGGER_MARK = "(BIGGER_THAN)\n"
JUMP_TO_END = "@END\n0;JMP\n"
END = "(END)\n"

SET_FALSE_AND_JUMP_IF_NOT_EQUAL = "M=0\n@END\nD;JNE\n"

""" END OF COMMON ASSEMBLY CODE FOR ARITHMETIC COMMANDS"""

# Note that EQ is shorter than GT and LT, because it doesn't need to handle overflow
# GT -> (x > y) .... x = *(SP-2), y = *(SP-1) 

GT = POP_Y + HANDLE_DIFFERENT_SIGNS + DXY + JUMP_IF_BIGGER + \
    LOWER_MARK + SET_FALSE + JUMP_TO_END + \
    BIGGER_MARK + SET_TRUE + END

LT = POP_Y + HANDLE_DIFFERENT_SIGNS + DXY + JUMP_IF_NOT_LOWER + \
    LOWER_MARK + SET_TRUE + JUMP_TO_END + \
    BIGGER_MARK + SET_FALSE + END

EQ = POP_Y + DXY + SET_FALSE_AND_JUMP_IF_NOT_EQUAL + SET_TRUE + END

POP_Y_AND_POINT_TO_X = POP_Y + "A=A-1\n"
POINT_TO_Y = "@SP\nA=M-1\n"

ART_DICT = {"gt": GT,
            "lt": LT,
            "eq": EQ,
            "add": POP_Y_AND_POINT_TO_X + "M=M+D\n",
            "sub": POP_Y_AND_POINT_TO_X + "M=M-D\n",
            "not": POINT_TO_Y + "M=!M\n",
            "neg": POINT_TO_Y + "M=-M\n",
            "and": POP_Y_AND_POINT_TO_X + "M=M&D\n",
            "or": POP_Y_AND_POINT_TO_X + "M=M|D\n",
            "shiftleft": POINT_TO_Y + "M=M<<\n",
            "shiftright": POINT_TO_Y + "M=M>>\n"
            }

PUSH_TEMPLATE = "\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
PUSH = "\nD=M" + PUSH_TEMPLATE
PUSH_CONST = "\nD=A" + PUSH_TEMPLATE

UPDATE_SP_AND_POINT_TO_Y = "\n@SP\nM=M-1\nA=M+1\n"
SAVE_VALUE_IN_STACK_AND_PUT_IT_IN_ADDRESS = "M=D\nA=A-1\nD=M\nA=A+1\nA=M\nM=D\n"

POP = UPDATE_SP_AND_POINT_TO_Y + SAVE_VALUE_IN_STACK_AND_PUT_IT_IN_ADDRESS
POP_CONST = "\nD=A" + UPDATE_SP_AND_POINT_TO_Y + "A=A+1\n" + SAVE_VALUE_IN_STACK_AND_PUT_IT_IN_ADDRESS

PUSH_POP_DICT_NOT_CONST = {"push": PUSH,
                           "pop": POP
                           }

PUSH_POP_DICT_CONST = {"push": PUSH_CONST,
                       "pop": POP_CONST
                       }

SEGMENT_DICT = {"SP": "SP",
                "local": "LCL",
                "argument": "ARG",
                "this": "THIS",
                "that": "THAT",
                "temp": "TEMP",
                "static": "STATIC"
                }

SET_LOCAL_TO_ZERO = '@0\nD=A\nM=M+1\nA=M-1\nM=D\n'

# Macros for compile return:

SET_NEW = "D=M\n@SP\nM=M+1\nA=M-1\nM=D\n"

RETURN_OLD = "\nM=M-1\nA=M\nD=M\n"



class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output_stream = output_stream
        self.current_file = ""
        self.current_function = ""
        self.current_return = 0
        self.counter = 0  # counter is used for counting arithmetic commands
                          # used to differentiate between their labels.

        # The navigator is used in order to translate parser command into actual code.
        self.navigator = [
            {
                "C_RETURN": self.write_return
            },
            {
                "C_ARITHMETIC": self.write_arithmetic,
                "C_LABEL": self.write_label,
                "C_GOTO": self.write_goto,
                "C_IF": self.write_if,
            },

            {
                "C_FUNCTION": self.write_function,
                "C_CALL": self.write_call,
            },

            {
               "C_PUSH": self.write_push_pop,
                "C_POP": self.write_push_pop, 
            }
        ]

    def get_method_and_index(self, command_type: str):
        """ This function return the right method to call"""
        for i in range(4):
            if command_type in self.navigator[i]:
                return self.navigator[i][command_type], i


    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.current_file = filename
        return

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        assembly_code_to_write = ART_DICT[command]
        for label in {"SUBTRACT", "Y_POSITIVE", "LOWER_THAN", "BIGGER_THAN", "END"}:
            # replace is used to different between commands labels
            assembly_code_to_write = assembly_code_to_write.replace(
                    label, label + "_" + command + "_" + str(self.counter))
            # also replaced in a debugging friendly way

        self.counter += 1  # increment counter
        self.output_stream.write(assembly_code_to_write)

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        if segment == "constant":  # translation to simple constant
            self.output_stream.write("@" + str(index) + PUSH_POP_DICT_CONST[command])
            return
        elif segment in ["pointer", "temp"]:  # translation to pointed segment
            index, segment = self.handle_pointer_and_temp(index, segment)
            command_adaptor = "\nA=A+D" if command == "push" else "\nD=A+D"
        else:
            command_adaptor = "\nA=M+D" if command == "push" else "\nD=M+D"
        self.output_stream.write("@" + str(index) + "\nD=A\n@" +
                                 SEGMENT_DICT[segment] + command_adaptor +
                                 PUSH_POP_DICT_NOT_CONST[command])
        # Note That command_adaptor is used because different commands needs
        # different commands in this place.

    @staticmethod
    def handle_pointer_and_temp(index, segment):
        """Handles the pointer and temp segments.
        The pointer segment is treated as a pointer to the THIS and THAT segments."""
        if segment == "temp":
            return index + 1, "that"  
        return 0, "that" if index == 1 else (index, "this")

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        self.output_stream.write("("+self.current_function+"$"+label+")\n")
        return

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        self.output_stream.write("@"+self.current_function+"$"+label+"\n"+"0;JMP\n")

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        self.output_stream.write("@SP\nM=M-1\nA=M\nD=M\n@"+self.current_function+"$"+label+"\nD;JNE\n")

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        self.current_function = function_name
        # (function_name)       // injects a function entry label into the code
        self.output_stream.write("("+function_name+")\n")
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        for i in range(n_vars):
            self.output_stream.write(SET_LOCAL_TO_ZERO)

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        label = function_name +"$ret." + str(self.current_return)

        to_write = ["@"+label + "\n", 
                    "D=A\n@SP\nM=M+1\nA=M-1\nM=D\n",  # push LCL   // saves LCL of the caller
                    "@R1\n" + SET_NEW,                # push ARG   // saves ARG of the caller
                    "@R2\n" + SET_NEW,                # push THIS  // saves THIS of the caller
                    "@R3\n" + SET_NEW,                # push THAT  // saves THAT of the caller
                    "@R4\n" + SET_NEW,                # ARG = SP-5-n_args  // repositions ARG
                    "@SP\nD=M\n@"+str(5+n_args)+"\nD=D-A\n@R2\nM=D\n",      # repositions LCL
                    "@SP\nD=M\n@R1\nM=D\n",                 # transfers control to the callee
                    "@"+function_name+"\n0;JMP\n", "("+label+")\n" # injects the return address label
                    ]
        for code in to_write:
            self.output_stream.write(code)
        self.current_return += 1

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # frame = LCL                  // frame is a temporary variable stored in [R10]
        self.output_stream.write("@R1\nD=M\n" + "@frame" + str(self.current_return) + "\nM=D\n")
        # return_address = *(frame-5)   // puts the return address in a temp var [R11]
        self.output_stream.write("@5\nD=D-A\nA=D\nD=M\n" + "@ret" + str(self.current_return) + "\nM=D\n") # D=M meaningless
        # *ARG = pop()                  // repositions the return value for the caller
        self.write_push_pop("pop","argument", 0)
        # SP = ARG + 1                  // repositions SP for the caller
        self.output_stream.write("@ARG\nD=M+1\n@SP\nM=D\n")

        load_return_frame = "@frame" + str(self.current_return)

        # THAT = *(frame-1)             // restores THAT for the caller
        self.output_stream.write(load_return_frame + RETURN_OLD + "@THAT\nM=D\n")
        # THIS = *(frame-2)             // restores THIS for the caller
        self.output_stream.write(load_return_frame + RETURN_OLD + "@THIS\nM=D\n")
        # ARG = *(frame-3)              // restores ARG for the caller
        self.output_stream.write(load_return_frame + RETURN_OLD + "@ARG\nM=D\n")
        # LCL = *(frame-4)              // restores LCL for the caller
        self.output_stream.write(load_return_frame + RETURN_OLD + "@LCL\nM=D\n")
        # goto return_address           // go to the return address
        self.output_stream.write("@ret" + str(self.current_return) + "\nA=M\n0;JMP\n")
        self.current_return += 1



