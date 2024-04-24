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
num=0
data_memory=[0]*120#creating a memory of size 120 filled with all 0's
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
register_value={
    "$0":0,
    "s0":0,
    "s1":0,
    "s2":0,
    "s3":0,
    "s4":0,
    "s5":0,
    "s6":0,
    "s7":0,
    "t0":0,#all of the below 3 can be varied and will still give proper output
    "t1":num,#number of numbers to sort
    "t2":0,#starting address of inputs,i.e,the five numbers to sort
    "t3":50,#starting address of outputs
    "t4":0,
    "t5":0,
    "t6":0,
    "t7":0,
    "t8":0,
    "t9":0
}
# data_memory[12]=2
# data_memory[16]=1
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
stall = 0
IF_ID_pipeline_reg = [] # Pipelined registers
ID_EX_pipeline_reg = []
EX_MEM_pipeline_reg = []
MEM_WB_pipeline_reg = []
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


IF_happend = -1     # Control signals for pipelining
ID_happend = -1
EX_happend = -1
MEM_happend = -1
count = 0
imm_written_back = 0        # if ins depends on previous two ins
imm_reg_dst = ""

while(True):
    a,b,c,d = 0,0,0,0
    clock_cycles += 1
    IF_status = clock_cycles
    if(MEM_happend + 1 == clock_cycles):    # if mem happens then write back
        if(MEM_WB_pipeline_reg[0][1]):# Check RegWrite and write back to proper destination.
            register_value[register[binary_to_decimal(MEM_WB_pipeline_reg[2])]]=MEM_WB_pipeline_reg[1]
            imm_written_back = MEM_WB_pipeline_reg[1] # mem-to-reg
            imm_reg_dst = MEM_WB_pipeline_reg[2]   # Reg-dst
    if(EX_happend+1 == clock_cycles):   # if EXhappens then do mem
        if(EX_MEM_pipeline_reg[0][2]):#this indicates a store word instruction
            data_memory[EX_MEM_pipeline_reg[3]]=EX_MEM_pipeline_reg[6]
        elif(EX_MEM_pipeline_reg[0][1]):#this indicates a load word instruction
            mem_to_reg=data_memory[EX_MEM_pipeline_reg[3]]
        elif(EX_MEM_pipeline_reg[0][4]):#this indicates an r type instruction or instructions like add immediate,and immediate etc
            mem_to_reg=EX_MEM_pipeline_reg[3]
        Control_Signals_MEM = [EX_MEM_pipeline_reg[0][3],EX_MEM_pipeline_reg[0][4]]# Mem-to-reg,RegWr
        MEM_WB_pipeline_reg = [Control_Signals_MEM,mem_to_reg,EX_MEM_pipeline_reg[5]] #EX_MEM_pipeline[5] = RegDst
        a = 1   # Writeback happend.
    if(ID_happend + 1 ==  clock_cycles):    # if id happens then EX
       
        alu_result = 0 # Intializing
        branch_flag = 0
        if(ID_EX_pipeline_reg[0][1] == "sll"):
            alu_src_A = ID_EX_pipeline_reg[8]   # if sll alu_src_a = shamt
        else:
            alu_src_A = register_value[register[binary_to_decimal(ID_EX_pipeline_reg[7])]]  # else rs_value
        if(ID_EX_pipeline_reg[0][0] == ID_EX_pipeline_reg[6]):  
            alu_src_B = register_value[register[binary_to_decimal(ID_EX_pipeline_reg[5])]]
        else:
            if((ID_EX_pipeline_reg[0][1] == "beq") and (ID_EX_pipeline_reg[0][1] == "bgtz")):
                alu_src_B = register_value[register[binary_to_decimal(ID_EX_pipeline_reg[5])]]  # if beq src b is rt
            else:
                alu_src_B = ID_EX_pipeline_reg[4]   # else immedical value
                # Forwarding unit
        if(len(EX_MEM_pipeline_reg)):
            if(EX_MEM_pipeline_reg[5] == ID_EX_pipeline_reg[7]):    #rd == rs
                alu_src_A = EX_MEM_pipeline_reg[3]  # forward alu_result to src A
            elif(EX_MEM_pipeline_reg[5] == ID_EX_pipeline_reg[5]):  #rd == rt
                
                ID_EX_pipeline_reg[3] = EX_MEM_pipeline_reg[3]  # forward alu_result to register rt
        if(len(MEM_WB_pipeline_reg)):
            
            if(MEM_WB_pipeline_reg[2] == ID_EX_pipeline_reg[7]):    # if Load, rt of load == rs
                alu_src_A = MEM_WB_pipeline_reg[1]  # forward mem to reg to alu src A
            elif(MEM_WB_pipeline_reg[2] == ID_EX_pipeline_reg[5]):  # rt of load == rs
                
                ID_EX_pipeline_reg[3] = MEM_WB_pipeline_reg[1]  # forward mem-to-reg to rt_value
                
        if(imm_reg_dst == ID_EX_pipeline_reg[7]):   # ins depends on previous to previous ins, dest == rs
            alu_src_A = imm_written_back    # forward written back value
        elif(imm_reg_dst == ID_EX_pipeline_reg[5]): # dest == rt
             ID_EX_pipeline_reg[3] = imm_written_back
        if(ID_EX_pipeline_reg[0][2] == 1):  # If control signal ALU_Src = 1, then i type
           
            if(ID_EX_pipeline_reg[0][1] == "beq" or ID_EX_pipeline_reg[0][1] == "bgtz"):
                 alu_src_B = ID_EX_pipeline_reg[3]  # if beq alu_srcb = rt
            else:
                 alu_src_B = ID_EX_pipeline_reg[4]  #else immediate value
            
        else:
             alu_src_B = ID_EX_pipeline_reg[3]  # for r-type rt_value
            # Performing operations
        
        if(ID_EX_pipeline_reg[0][1] =="add"):
            alu_result = alu_src_A +alu_src_B
        elif(ID_EX_pipeline_reg[0][1]=="and"):
                alu_result=alu_src_A&alu_src_B
        elif (ID_EX_pipeline_reg[0][1] == "nor"):
                alu_result = ~(alu_src_A | alu_src_B)
        elif (ID_EX_pipeline_reg[0][1] == "or"):
                alu_result = alu_src_A|alu_src_B
        elif (ID_EX_pipeline_reg[0][1] == "slt"):
                if(alu_src_A<alu_src_B):
                    alu_result=1
                else:
                    alu_result=0
        elif (ID_EX_pipeline_reg[0][1] == "sub"):
                alu_result = alu_src_A - alu_src_B
        elif (ID_EX_pipeline_reg[0][1] == "sll"):#represents shift left logical
                alu_result =alu_src_B*int(pow(2,alu_src_A))
        
        if(ID_EX_pipeline_reg[0][1]=="beq"):
             alu_result=alu_src_A-alu_src_B;#srcA-rs_value and srcB-rt_value
             if(alu_result==0):#if difference is 0,then we need to take the branch
                branch_flag= 1
             elif(ID_EX_pipeline_reg[0][1]=="bne"):#for branch not equal
                alu_result=alu_src_A-alu_src_B
                if(alu_result!=0):
                    branch_flag= 1
        elif(ID_EX_pipeline_reg[0][1]=="bgtz"):#branch on greater than
                if(alu_src_A>0):#this should branch on rs value being >0
                    branch_flag= 1
        elif(ID_EX_pipeline_reg[0][1]=="add_immediate" or ID_EX_pipeline_reg[0][1]=="load_word" or ID_EX_pipeline_reg[0][1]=="store_word"):
                if(ID_EX_pipeline_reg[0][1]=="load_word"):
                    alu_result = alu_src_A + alu_src_B
                    # mem_read=ID_EX_pipeline_reg[0][4]
                elif(ID_EX_pipeline_reg[0][1]=="store_word"):
                    alu_result =alu_src_A+alu_src_B
                    # mem_write=ID_EX_pipeline_reg[0][5]
                else:
                    alu_result = alu_src_A+alu_src_B
                    # reg_write=ID_EX_pipeline_reg[0][7]
        elif(ID_EX_pipeline_reg[0][1]=="and_immediate"):
                alu_result=alu_src_A&alu_src_B
        Branch_ex = ID_EX_pipeline_reg[0][3]    # Updating pipeline registers
        MemRead_ex = ID_EX_pipeline_reg[0][4]
        MemWrite_ex = ID_EX_pipeline_reg[0][5]
        MemtoReg_ex = ID_EX_pipeline_reg[0][6]
        RegWrite_ex = ID_EX_pipeline_reg[0][7]
        Control_Signals_EX = [Branch_ex,MemRead_ex,MemWrite_ex,MemtoReg_ex,RegWrite_ex]
        EX_MEM_pipeline_reg = [Control_Signals_EX,ID_EX_pipeline_reg[1],branch_flag,alu_result,ID_EX_pipeline_reg[5],ID_EX_pipeline_reg[0][0],register_value[register[binary_to_decimal(ID_EX_pipeline_reg[5])]]]
        # control signals,pc,branch_flag,result,rt,regDst,rt_value
        if(branch_flag == 1):
            pc = ID_EX_pipeline_reg[1]+ID_EX_pipeline_reg[4]    # pc + imm
            IF_happend = IF_happend+700     # flush ID and IF
            IF_status = IF_status + 700
        b = 1   # EX happend
    if(IF_happend + 1 == clock_cycles): # if fetch happens then decode
        instruction  = IF_ID_pipeline_reg[1]
        Control_Signals = []
        Branch = 0  # Intializing control signals
        MemRead = 0
        MemWrite = 0
        RegWrite = 0
        MemtoReg = 0
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
            # Deciding control signals
            RegDst = rd
            ALU_Op = funct_field[funct]
            ALU_Src = 0
            RegWrite = 1
        elif(opcodes[opcode]=="jump_target" or opcodes[opcode]=="jump_and_link"):#instruction if jump type
            jflag=1;#indicates jump instruction
            imm=instruction[6:32]#last 26 bits are immediate field
            imm_extended="0"*4+imm+"0"*2#they have to be extended to 32 bits in this way
            immdecimal=find_twos_complement(imm_extended)#gives decimal rep of imm
            RegDst = 0
            ALU_Op = "0"
            ALU_Src = 3
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
            RegDst = rt
            ALU_Op = opcodes[instruction[0:6]]
            ALU_Src = 1
            # Deciding control signals
            if((ALU_Op == "beq") or (ALU_Op == "bne") or (ALU_Op == "bgtz")):
                Branch = 1
            elif ((ALU_Op == "add_immediate") or (ALU_Op == "and_immediate")):
                RegWrite = 1
            else:
                if(ALU_Op == "load_word"):
                    MemRead = 1
                    MemtoReg = 1
                    RegWrite = 1
                else:
                    MemWrite = 1
        Control_Signals = [RegDst,ALU_Op,ALU_Src,Branch,MemRead,MemWrite,MemtoReg,RegWrite]
        ID_EX_pipeline_reg = [Control_Signals,pc,rs_value,rt_value,immdecimal,rt,rd,rs,shamt_decimal]
        # Hazard detection
        if(len(ID_EX_pipeline_reg) and len(EX_MEM_pipeline_reg)):
            # Hazard detection for load, if mem read is 1 and destination of load is one of the sources of the instruction
            if((EX_MEM_pipeline_reg[0][1]) and ((ID_EX_pipeline_reg[5] == EX_MEM_pipeline_reg[4]) or (ID_EX_pipeline_reg[7] == EX_MEM_pipeline_reg[4]))):
                Control_Signals = [RegDst,ALU_Op,ALU_Src,0,0,0,0,0] # stall
                pc = pc-1   # retaining same pc
                ID_EX_pipeline_reg = [Control_Signals,pc,rs_value,rt_value,immdecimal,rt,rd,rs,shamt_decimal]
        if(opcodes[opcode]=="jump_target" or opcodes[opcode]=="jump_and_link"):
            pc = abs(immdecimal-4194304)//4
           
        c = 1   # ID happend
    if(IF_status == clock_cycles):  #  Useful for flushing, when beq is taken
        if(pc < len(instruction_memory)):
            ins = instruction_memory[pc]
            pc += 1
            IF_ID_pipeline_reg = [pc,ins]
            count = 0   # if valid instruction fetch should happen
        elif(pc == len(instruction_memory)):
            ins = "00000000000000000000000000000000"    #no-op
            IF_ID_pipeline_reg = [pc,ins]
            count += 1
        d =1    # IF happend
    if(d == 1):
         IF_happend = clock_cycles 
    if(c == 1):
        ID_happend = clock_cycles
    if(b == 1):
        EX_happend = clock_cycles
    if(a == 1):
        MEM_happend = clock_cycles
    if(count == 4): # no-op is taken 4 times, ie write back of last instruction is finished
         break
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
    