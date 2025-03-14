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



