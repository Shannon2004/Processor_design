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

The implementation of the non-pipelined MIPS processor is provided in `non_pipelined_processor.py`. The program begins by defining several dictionaries that serve as mappings for essential components of the processor, including opcodes, registers, and function codes. Additionally, it initializes memory structures for data storage, instruction storage, and register storage.

The program accepts an input text file containing an instruction set derived from the assembly code available in the MIPS Assembler repository. Depending on the user's choice, the input can correspond to either a sorting task or a factorial computation. The main function orchestrates the execution of the instruction cycle by sequentially invoking the following five stages: IF, ID, EXE, MEM, WB. Each of these stages is implemented as a separate function. After completing all five stages for an instruction, the program counter is updated accordingly. The update depends on whether the instruction is a standard operation, a branch instruction, or a jump instruction. Once all instructions have been executed, the program outputs the final results of the instruction set execution.

### 1. Instruction Fetch (`instruction_fetch()`)

**Purpose**: Retrieves the next instruction from instruction memory using the program counter (PC).

**Implementation Details**:
- Takes the current PC value as input parameter.
- Increments the global clock cycle counter to track execution time.
- Returns the instruction stored at the memory location indicated by PC.
- Accesses the instruction from the `instruction_memory` list which was loaded from the input file.
- Simulates the fetch stage of a real processor where instructions are read from memory.

### 2. Instruction Decode (`instruction_decode()`)

**Purpose**: Examines the fetched instruction to determine its type and operands.

**Implementation Details**:
- Extracts the 6-bit opcode from the instruction (most significant bits).
- Increments the global clock cycle counter.
- Sets appropriate flags (`rflag`, `iflag`, `jflag`) based on instruction type.
- Handles three instruction formats:
  
  **R-Type Format (Register-type):**
  - Structure: `opcode (6 bits) | rs (5 bits) | rt (5 bits) | rd (5 bits) | shamt (5 bits) | funct (6 bits)`
  - Extracts and converts `rs`, `rt`, `rd` register indices.
  - Retrieves corresponding register values from the register file.
  - Extracts shift amount (`shamt`) and function code (`funct`).
  
  **I-Type Format (Immediate-type):**
  - Structure: `opcode (6 bits) | rs (5 bits) | rt (5 bits) | immediate (16 bits)`
  - Extracts and converts `rs` and `rt` register indices.
  - Retrieves corresponding register values.
  - Extracts and converts the 16-bit immediate value (handles two's complement for signed values).
  
  **J-Type Format (Jump-type):**
  - Structure: `opcode (6 bits) | target address (26 bits)`
  - Extracts 26-bit immediate value which represents the jump target address.
  - Converts immediate to its proper representation for use in PC calculation.

- Uses helper functions like `binary_to_decimal()` and `find_twos_complement()` for binary-to-decimal conversion.

### 3. Execute (`execute()`)

**Purpose**: Performs the actual operation specified by the instruction.

**Implementation Details**:
- Increments the global clock cycle counter.
- Determines operation based on instruction type and opcode/function field.
- For **R-type instructions**:
  - Sets register write flag to indicate write-back is needed.
  - Sets ALU source operands from register values.
  - Performs operation based on function field (add, subtract, AND, OR, SLT, etc.).
  - Handles logical operations (AND, OR, NOR).
  - Handles shift operations (SLL, SRL) using the shift amount field.
  - Stores result in the ALU result register.
- For **I-type instructions**:
  - For **branch instructions** (beq, bne, bgtz):
    - Compares register values based on branch type.
    - Sets branch flag if branch condition is met.
  - For **load/store instructions**:
    - Calculates effective address by adding base register value and immediate offset.
    - Sets appropriate memory read/write flags.
  - For **immediate arithmetic operations**:
    - Performs operation between register value and immediate value.
    - Sets register write flag for write-back.
- For **J-type instructions**:
  - Execution happens implicitly through PC update in the main loop.

### 4. Memory Access (`memory_access()`)

**Purpose**: Performs memory operations if required by the instruction.

**Implementation Details**:
- Increments the global clock cycle counter.
- Handles three main cases:
  - **Memory Write (Store Instructions):**
    - If `mem_write` flag is set (from store word instruction).
    - Writes `rt_value` (register value) to `data_memory` at address calculated in ALU.
  - **Memory Read (Load Instructions):**
    - If `mem_read` flag is set (from load word instruction).
    - Reads value from `data_memory` at address calculated in ALU.
    - Stores value in `mem_to_reg` for use in write-back stage.
  - **No Memory Operation:**
    - For ALU operations (R-type and some I-type), simply passes ALU result to `mem_to_reg` for write-back.
- Uses `data_memory` array to simulate processor's data memory.

### 5. Write Back (`write_back()`)

**Purpose**: Updates registers with computation results if needed.

**Implementation Details**:
- Increments the global clock cycle counter.
- Handles two main cases:
  - **Register Write Operations:**
    - If `reg_write` flag is set (ALU operations, immediate operations).
    - Writes `mem_to_reg` value to the destination register (`rd` for R-type, `rt` for I-type).
  - **Memory Load Operations:**
    - If `mem_read` flag is set (load word), writes the value from `mem_to_reg` to the target register (`rt`).
- Updates the `register_value` dictionary with computed results.
- Completes the instruction execution cycle.

### Program Control Flow
After executing all five stages for an instruction, the PC is updated based on instruction type:
- For **branch instructions** (with `branch_flag` set): `PC += immediate + 1`
- For **jump instructions** (with `jflag` set): `PC = (immediate - base_address) / 4`
- For **sequential execution**: `PC += 1`

After PC update, all control flags and temporary registers are reset for the next instruction cycle.

## Pipelined MIPS Processor

The pipelined processor is largely similar to the non-pipelined version, except for some modifications to enable pipelining. These modifications include:

### Pipelined Registers
These registers store information as an instruction moves from one pipeline stage to another. The contents of these registers are:

- **IF/ID Pipeline Register**: Stores the Program Counter (PC) and the fetched instruction.
- **ID/EX Pipeline Register**: Stores control signals, such as the destination register, ALU operation, instruction type, memory access, and write-back requirements. Additionally, it holds the PC, `rs`, `rt`, `rd`, immediate value, and shift amount.
- **EX/MEM Pipeline Register**: Contains control signals, branch flag, ALU result, and relevant data from the ID/EX pipeline register.
- **MEM/WB Pipeline Register**: Holds control signals, data to be loaded from memory to registers, and the destination register.

### Hazard Detection
- Structural hazards are handled by introducing stalls. A stall is implemented as an empty instruction by clearing all control signals while retaining the same program counter value. This ensures no unintended execution while consuming a clock cycle.

### Forwarding Unit
To minimize stalls, a forwarding unit is introduced, which allows values from previous stages to be forwarded to subsequent ones. There are three cases:

1. **Case 1: R-type instruction followed by an R-type instruction**  
   - If there is a dependency between the two (i.e., the destination register of the first is a source for the second), the ALU result from the EX stage is forwarded to the next EX stage.

2. **Case 2: I-type instruction followed by an R-type instruction with dependency**  
   - The `rt` value of the I-type instruction is forwarded from the MEM stage to the EX stage for use in the R-type instruction.

3. **Case 3: Dependency across multiple instructions**  
   - An I-type instruction followed by two R-type instructions, all with dependencies. Forwarding occurs twice: from EX to EX and from WB to EX.

### Flushing
- When a branch instruction is encountered, the IF and ID stages are flushed to remove incorrect instructions from the pipeline. The correct instruction is fetched in the next cycle. Flushing is implemented by skipping the IF and ID stages for that cycle.

---
This pipeline implementation improves efficiency by handling hazards and minimizing stalls while maintaining correct execution flow.
