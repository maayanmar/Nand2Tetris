@SP
M=M-1
A=M
D=M
@Y_POSITIVE 
D;JGT
@SP
A=M-1
D=M
@NOT_EQUAL
D;JGT    
@SUBTRACT
0;JMP
(Y_POSITIVE)
@SP
A=M-1
D=M
@NOT_EQUAL
D;JLE
(SUBTRACT)
@SP
A=M
D=M
A=A-1
D=M-D
@NOT_EQUAL
D;JNE
@SP
A=M-1
M=-1
@END
0;JMP
(NOT_EQUAL)
@SP
A=M-1
M=0
(END)