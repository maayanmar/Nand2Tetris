# Compiler for Java-like Language
This is a compiler for a Java-like language that compiles source code into executable HACK code.

The compiler performs the following steps:

Parsing: The source code is parsed and converted into an intermediate representation in the form of VM code. This is done by the compiler's parser module.

Translation: The VM code is then translated into assembly code. This is done by the VMTranslator module. The translation process involves mapping each VM command to one or more assembly commands.

Assembly: The assembly code is then assembled into HACK code. This is done by the Assembler module, which translates the assembly code into binary machine code that can be executed on the HACK computer.

The resulting HACK code can then be loaded onto a HACK computer and executed. The HACK computer is a simple computer architecture with a CPU, memory, and input/output devices.
