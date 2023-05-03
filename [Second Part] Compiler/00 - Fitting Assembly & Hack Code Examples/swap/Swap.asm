// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

@32767 // Max_value
D=A
@max
M=-D
@min
M=D

@R15 // i = R15
D=M
@i
M=D
@R14
D=M
@cur
M=D

(ITERATE) // i = R15 to ... i = 0
@i
M=M-1
@cur
A=M
D=M
@min
D=D-M
@UPDATE_MIN
D;JLT

(AFTER_MIN)
@cur
A=M
D=M
@max
D=D-M
@UPDATE_MAX
D;JGT


(AFTER_MAX)
@i
D=M
@SWAP
D;JEQ
@cur
M=M+1
@ITERATE
0;JMP

(UPDATE_MIN)
@cur
D=M
@min_pointer
M=D

A=M
D=M
@min
M=D
@AFTER_MIN
0;JMP


(UPDATE_MAX)
@cur
D=M
@max_pointer
M=D
A=M
D=M
@max
M=D
@AFTER_MAX
0;JMP

(SWAP)
@min
D=M
@max_pointer
A=M
M=D
@max
D=M
@min_pointer
A=M
M=D

(END)
@END
0;JMP



