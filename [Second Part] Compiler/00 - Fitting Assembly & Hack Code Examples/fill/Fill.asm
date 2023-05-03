

// (LOOP)
//     // saving screen address in variable "i"
//     @SCREEN
//     D = A
//     @i
//     M = D
//     // saving keyboard address in variable "j"
//     @KBD 
//     D = A
//     @j
//     M = D
//     // checking if some key is pressed
//     @KBD
//     D = M
//     @WHITE
//     D;JEQ  // jump if false, else:

// (BLACK) // all screen bytes = -1
//     @i
//     A = M
//     M = -1
//     @i
//     M = M+1
//     D = M
//     @j
//     D = M-D
//     @BLACK
//     D;JGT // jump back to black loop if needed
//     @LOOP
//     0;JMP // jump back to main loop

// (WHITE) // all screen bytes = 0
//     @i
//     A = M
//     M = 0
//     @i
//     M = M+1
//     D = M
//     @j
//     D = M-D
//     @WHITE
//     D;JGT // jump back to white loop if needed
//     @LOOP
//     0;JMP // jump back to main loop



(START) // INTIALIZE TO THE FIRST PIXEL
@SCREEN
D=A
@PIXEL
M=D

@KBD    // CHECK IF KEY IS PRESSED
D=M
@BLACK
D;JNE

(WHITE)
@COLOR
M=0
@LOOP
0;JMP

(BLACK)
@COLOR
M=-1

(LOOP) // LOOP THROUGH ALL PIXELS
@COLOR
D=M
@PIXEL
M=M+1
A=M-1
M=D
D=A+1
@KBD
D=D-A

@START
D;JGE

@LOOP
0;JMP






