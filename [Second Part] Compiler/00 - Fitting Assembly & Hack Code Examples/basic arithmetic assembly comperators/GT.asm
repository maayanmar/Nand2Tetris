@SP
M=M-1
A=M
D=M
@Y_POSITIVE 
D;JGT
@SP
A=M-1
D=M
@BIGGER_THAN
D;JGT    
@SUBTRACT
0;JMP
(Y_POSITIVE)
@SP
A=M-1
D=M
@LOWER_THAN
D;JLE
(SUBTRACT)
@SP
A=M
D=M
A=A-1
D=M-D
@BIGGER_THAN
D;JGT
(LOWER_THAN)
@SP
A=M-1
M=0
@END
0;JMP
(BIGGER_THAN)
@SP
A=M-1
M=-1
(END)