choice=int(input("Enter 1 for sorting,2 for factorial:\n"))
#dictionary for opcodes
opcodes = {
    "100011":"load_word",
    "101011":"store_word",
    "000100":"beq",
    "000010": "jump_target",
    "000011": "jump_and_link",
    "000000":"r-type",
    "001000":"add_immediate",
    "001100":"and_immediate",
    "000101":"bne",
    "000111":"bgtz"
    # Add more instructions as needed
}
#dictionary for funct fields
funct_field={
    "100000":"add",
    "100100":"and",
    "100111":"nor",
    "100101":"or",
    "101010":"slt",
    "100010":"sub",
    "000000":"sll",
    "000010":"srl",
    "011000":"mult",
    "001101":"break",

}
#register file dictionary
register={
    0:"$0",
    8:"t0",
    9:"t1",
    10:"t2",
    11:"t3",
    12:"t4",
    13:"t5",
    14:"t6",
    15:"t7",
    24:"t8",
    25:"t9",
    16:"s0",
    17:"s1",
    18:"s2",
    19:"s3",
    20:"s4",
    21:"s5",
    22:"s6",
    23:"s7"
}

data_memory=[0]*120#creating a memory of size 120 filled with all 0's
#storing 5 numbers(these are our input numbers which we store in indices separated by 4 units)
#
num=0
if(choice==1):
    file_input = 'sorting_machine_code.txt'
    num=int(input("Enter the number of numbers to sort:\n"))
    print("Enter the numbers:")
    start=0
    for i in range(num):
        n=int(input())
        data_memory[start]=n
        start+=4
else:
    file_input = 'factorial_machine_code.txt'
    data_memory[0]= int(input("Enter the number whose factorial has to be found:\n"))
    num=1

register_value = {
        "$0": 0,
        "s0": 0,
        "s1": 0,
        "s2": 0,
        "s3": 0,
        "s4": 0,
        "s5": 0,
        "s6": 0,
        "s7": 0,
        "t0": 0,  # all of the below 3 can be varied and will still give proper output
        "t1": num,  # number of numbers on which operation has to be performed
        "t2": 0,  # starting address of inputs,i.e,the five numbers to sort
        "t3": 50,  # starting address of outputs
        "t4": 0,
        "t5": 0,
        "t6": 0,
        "t7": 0,
        "t8": 0,
        "t9": 0
}
readdata=0
rflag=0#flag to tell if instruction is r type
iflag=0#flag to tell if instruction is i type
jflag=0#flag to tell if instruction is j type
branch_flag=0#this tells if we have to branch or not
encounter_branch=0#this tells if we encountered any type of branch statement
opcode="" #stores opcode
rs=""   #stores rs(source register)
rs_value=0#stores value stored in rs
mem_to_reg=0#tells from where to write back to register file to(from alu result or memory)
rt=""   #stores rt
rt_value=0#stores value stored in rt
rd=""   #stores rd(destination register)
rd_value=0#stores value stored in rd
imm=""#stores imm field
jump=0#tells if we encountered a jump or not
alu_src_A=0#input to alu
alu_src_B=0#input to alu
alu_zero_flag=0#sees if srcA-srcB=0 , if it's 0 then zero flag will be 1
alu_result=0#stores result of the alu operation
reg_write=0#tells if we have to write back to the register or not
mem_write=0#tells if instruction is store word and if we have to write to memory or not
mem_read=0#indicates a load word
immdecimal=0 #stores the value of the immediate field as a decimal
shamt="" #represents the shift amount
shamt_decimal=0#shift amount in decimal
funct="" #represents the funct field
clock_cycles=0 #this counts the clock cycles
pc=0; #this is the program counter,holds the address of the next instruction to be executed
instruction_memory=[]#initializing an empty list that will act as instruction memory
# Opening the input file in read mode
with open(file_input, 'r') as file:
    lines = file.readlines()
for line in lines:
    instruction_memory.append(line.strip());#appending each line to our instruction memory
#function to convert binary string to equivalent decimal
def binary_to_decimal(binary_string):
    decimal=0
    power=len(binary_string)-1
    for bit in binary_string:
        if(bit=='1'):
            decimal+=pow(2,power)
        power-=1
    return decimal
#this function is used to find the decimal representation of immediate value
def find_twos_complement(binary_string):
    #if number is positive indicated by binary_string[0] then there's no need to compute two's complement
        if(binary_string[0]=='0'):
            return binary_to_decimal(binary_string)
        # Step 1: invert all bits of binary_string
        # inverted_string = ''.join(['0' if bit == '1' else '1' for bit in binary_string])
        inverted_string=''
        for bit in binary_string:
            if(bit=='1'):
                inverted_string+='0'
            else:
                inverted_string+='1'
        # Step 2: Add 1 to the inverted binary string
        carry = 1
        twos_comp_result = ''
        inverted_string=reversed(inverted_string)
        for bit in inverted_string:
            if bit == '0' and carry == 1:
                twos_comp_result = '1' + twos_comp_result
                carry = 0
            elif bit == '1' and carry == 1:
                twos_comp_result = '0' + twos_comp_result
            else:
                twos_comp_result = bit + twos_comp_result

        return -binary_to_decimal(twos_comp_result)


#instruction fetch(Phase 1)
#in this,we just get the instruction at the address pointed to by the pc
def instruction_fetch(pc_value):
    global instruction_memory
    global clock_cycles
    clock_cycles+=1#increment the number of clock cycles
    return instruction_memory[pc]#returns the instruction at the pc
#this models the instruction decode stage. Here,we decode our instruction and we find opcode,and using that ,we find other things like rs,rt,shamt,imm,funct depending on the type of the instruction
def instruction_decode(instruction):
    global clock_cycles
    global opcode
    global rs
    global rt
    global rd
    global rs_value
    global rt_value
    global rd_value
    global imm
    global immdecimal
    global register
    global register_value
    global rflag
    global iflag
    global jflag
    global jump
    global encounter_branch
    global funct
    global shamt
    global shamt_decimal
    clock_cycles+=1#increment the number of clock cycles
    opcode=instruction[:6]#6 most significant bits of the instruction is the opcode
    if(opcodes[opcode]=="r-type"):#instruction is r type
        rflag=1;#set rflag to 1 as it is r type
        rs=instruction[6:11]#the next 5 most MSB bits are rs
        temp=binary_to_decimal(rs)#this gives decimal rep of rs
        rs_value=register_value[register[temp]]#this gives value stored in the register rs points to
        rt=instruction[11:16]#the next 5 bits are rt
        temp = binary_to_decimal(rt)#this gives decimal rep of rt
        rt_value=register_value[register[temp]]#this gives value stored in the register rt points to
        rd=instruction[16:21]#the next 5 bits are rd
        temp = binary_to_decimal(rd)#this gives decimal rep of rd
        rd_value = register_value[register[temp]]#this gives value stored in the register rd points to
        shamt=instruction[21:26]#the next 5 bits are shift amount
        shamt_decimal=binary_to_decimal(shamt)#decimal rep of shift amount
        funct=instruction[26:32]#next 6 bits are funct field
        # print(opcode,rs_value,rt_value,rd_value,shamt_decimal,funct)
    elif(opcodes[opcode]=="jump_target" or opcodes[opcode]=="jump_and_link"):#instruction if jump type
        jflag=1;#indicates jump instruction
        imm=instruction[6:32]#last 26 bits are immediate field
        imm_extended="0"*4+imm+"0"*2#they have to be extended to 32 bits in this way
        immdecimal=find_twos_complement(imm_extended)#gives decimal rep of imm
    else:#instruction is i type
       iflag=1;#says it's i type
       rs=instruction[6:11]#next 5 bits are rs
       temp = binary_to_decimal(rs)
       rs_value = register_value[register[temp]]
       rt=instruction[11:16]#next 5 bits are rt
       temp =binary_to_decimal(rt)
       rt_value = register_value[register[temp]]
       imm=instruction[16:32]#last 16 bits are imm
       immdecimal=find_twos_complement(imm)
#this models the execute stage
def execute():
    global rflag
    global alu_result
    global alu_src_A
    global alu_src_B
    global funct
    global funct_field
    global opcode
    global opcodes
    global branch_flag
    global clock_cycles
    global mem_write
    global mem_read
    global reg_write
    global rt_value
    global iflag
    global immdecimal
    global shamt_decimal

    clock_cycles+=1#increment the number of clock cycles
    if(rflag==1):#if instruction is r type
        reg_write=1#we have to write back to register file
        alu_src_A=rs_value#srcA=rs
        alu_src_B=rt_value#srcB=rt
        if(funct_field[funct]=="add"):
            alu_result=alu_src_A+alu_src_B
        elif(funct_field[funct]=="and"):
            alu_result=alu_src_A&alu_src_B
        elif (funct_field[funct] == "nor"):
            alu_result = ~(alu_src_A | alu_src_B)
        elif (funct_field[funct] == "or"):
            alu_result = alu_src_A|alu_src_B
        elif (funct_field[funct] == "slt"):
            if(alu_src_A<alu_src_B):
                alu_result=1
            else:
                alu_result=0
        elif (funct_field[funct] == "sub"):
            alu_result = alu_src_A - alu_src_B
        elif (funct_field[funct] == "sll"):#represents shift left logical
            alu_result =rt_value*int(pow(2,shamt_decimal))
        elif(funct_field[funct]=="srl"):
            alu_result=rt_value//(int(pow(2,shamt_decimal)))
    elif(iflag==1):#indicates it's an i type instruction
        if(opcodes[opcode]=="beq"):
            alu_result=rs_value-rt_value;#srcA-rs_value and srcB-rt_value
            if(alu_result==0):#if difference is 0,then we need to take the branch
                branch_flag=1
        elif(opcodes[opcode]=="bne"):#for branch not equal
            alu_result=rs_value-rt_value
            if(alu_result!=0):
                branch_flag=1
        elif(opcodes[opcode]=="bgtz"):#branch on greater than
            if(rs_value>0):#this should branch on rs value being >0
                branch_flag=1
        elif(opcodes[opcode]=="add_immediate" or opcodes[opcode]=="load_word" or opcodes[opcode]=="store_word"):
            if(opcodes[opcode]=="load_word"):
                alu_result = rs_value + immdecimal
                mem_read=1
            elif(opcodes[opcode]=="store_word"):
                alu_result = rs_value + immdecimal
                mem_write=1
            else:
                alu_result = rs_value + immdecimal
                reg_write=1
        elif(opcodes[opcode]=="and_immediate"):
            alu_result=rs_value&immdecimal
#mimics the memory access phase
def memory_access():
    global clock_cycles
    global mem_write
    global data_memory
    global rt_value
    global alu_result
    global mem_read
    global mem_to_reg
    global reg_write
    clock_cycles+=1
    if(mem_write==1):#this indicates a store word instruction
            data_memory[alu_result]=rt_value
    elif(mem_read==1):#this indicates a load word instruction
            mem_to_reg=data_memory[alu_result]
    elif(reg_write==1):#this indicates an r type instruction or instructions like add immediate,and immediate etc
        mem_to_reg=alu_result
def write_back():#write back phase
    global clock_cycles
    global reg_write
    global register_value
    global register
    global mem_to_reg
    global mem_read
    global mem_write
    global rd
    global rt
    global rs
    global rs_value
    global rd_value
    global rt_value
    global data_memory
    clock_cycles+=1
    if(reg_write==1):#instruction has to be r type or i type like addimm,andimm etc
        # print("rd-value:",rd_value)
        # print("rd:",rd)
        if(rflag==1):#r type instruction
            register_value[register[binary_to_decimal(rd)]]=mem_to_reg
        elif(iflag==1):#addi type
            register_value[register[binary_to_decimal(rt)]]=mem_to_reg
    elif(mem_read==1):#load word
        register_value[register[binary_to_decimal(rt)]] = mem_to_reg
while pc<len(instruction_memory):#this is how many times our loop must run
    #fetching the instruction
    current_instruction=instruction_fetch(pc)#after instruction fetch,we get the current instruction pointed to by the pc
    #decoding the fetched instruction
    instruction_decode(current_instruction)#in the decode phase,we have to decode that instruction
    #execution phase
    execute()
    #memory access phase
    memory_access()
    #writeback
    write_back()
    if(branch_flag==1):#if we have to branch,then we must update our pc to pc+immdecimal+1(basically,it is :pc+(4+4*imm)//4 because our pc increments one index at a time
        pc=(pc+immdecimal+1)
    elif(jflag==1):#if we have to jump,we must update our pc in this manner
        pc=abs(immdecimal-4194304)//4#starting pc value in machine code=4194304. So to bring it to our units,we must subtract it from the imm value and divide by 4
        # if(count==6):
        #     exit()
    else:#just increase pc by 1 and move on
        pc+=1
    #reset all the values
    rflag = 0
    iflag = 0
    jflag = 0
    branch_flag = 0
    opcode = ""  # stores opcode
    rs = ""  # stores rs(source register)
    rs_value = 0
    mem_to_reg = 0
    rt = ""  # stores rt
    rt_value = 0
    rd = ""  # stores rd(destination register)
    rd_value = 0
    imm = ""
    jump = 0
    alu_src_A = 0
    alu_src_B = 0
    alu_zero_flag = 0
    alu_result = 0
    reg_write = 0
    mem_write = 0
    mem_read = 0
    immdecimal = 0  # stores the value of the immediate field as a decimal
    shamt = ""  # represents the shift amount
    shamt_decimal = 0
    funct = ""
if(choice==1):
    print("Output sorted in descending order is:")
    start=50#starting memory address of output
    for i in range(num):
        print(data_memory[start])
        start+=4
else:
    print("Factorial of the number is:")
    print(data_memory[50])#50 is starting output address
print("Total number of clock cycles is:")
print(clock_cycles)



