# Processor Design

## Pre-requisites

### Five Phases of Execution in a Processor
A processor executes instructions in five key stages:

1. **Instruction Fetch (IF)**: The processor fetches the instruction from memory based on the program counter (PC).
2. **Instruction Decode (ID)**: The fetched instruction is decoded to determine the operation and operands required.
3. **Execution (EXE)**: The operation is performed, such as arithmetic computations, logic operations, or address calculations.
4. **Memory Access (MEM)**: If the instruction involves memory (e.g., load/store), the required data is read from or written to memory.
5. **Write Back (WB)**: The computed result is written back to a register, completing the instruction execution.

### Pipelined vs. Non-Pipelined Processors

- **Non-Pipelined Processor**: Each instruction completes all five stages before the next instruction begins, leading to longer execution time.
- **Pipelined Processor**: Multiple instructions are executed simultaneously by overlapping different execution stages, improving performance and instruction throughput.


## Non-Pipelined MIPS Processor

The implementation of the non-pipelined MIPS processor is provided in non_pipelined_processor.py. The program begins by defining several dictionaries that serve as mappings for essential components of the processor, including opcodes, registers, and function codes. Additionally, it initializes memory structures for data storage, instruction storage, and register storage.

The program accepts an input text file containing an instruction set derived from the assembly code available in the MIPS Assembler repository. Depending on the user's choice, the input can correspond to either a sorting task or a factorial computation. The main function orchestrates the execution of the instruction cycle by sequentially invoking the following five stages: IF, ID, EXE, MEM, WB. Each of these stages is implemented as a separate function. After completing all five stages for an instruction, the program counter is updated accordingly. The update depends on whether the instruction is a standard operation, a branch instruction, or a jump instruction. Once all instructions have been executed, the program outputs the final results of the instruction set execution.
