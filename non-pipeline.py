# Dictionaries to map binary opcode, register codes, and function codes to their respective assembly language representations
opcodes = {
    '000000':'add', '000000':'sub', '100011':'lw', '101011':'sw',
    '000100':'beq', '000101':'bne', '000000':'slt', '000000':'addu',
    '001001':'addiu', '001111':'lui', '001101':'ori', '000011':'jal', '000000':'jr', '001000':'addi','000010':'j'
}
reg_codes = {
    '00000':'$0', '01001':'$t1', '01010':'$t2', '01011':'$t3', '01100':'$t4',
    '01101':'$t5','01110':'$t6', '01111':'$t7', '11000':'$t8', '10001':'$t9',
    '10100':'$s4', '10101':'$s5', '10110':'$s6', '10111':'$s7', '00010':'$v0',
    '00100':'$a0', '11111':'$ra', '00001':'$1', '10001': '$s1', '10010': '$s2'
}
func_codes = {
    '100000':'add', '100010':'sub', '101010':'slt', '100001':'addu', '001000':'jr'
}

# Initializing dictionaries for variable values, index, memory addresses, beq flags, and number mapping
values={
    '$t5': 0, '$t1': 5, '$s7': 0, '$1': 1, '$0': 0, '$s6': 0, '$t7': 0, '$s4': 0, '$s5': 0, '$t6': 0, '$t2': 268501216, '$t3': 268501344, '$t8': 0, '$s1': 0, '$s2': 0, '$t4': 9
}
index={}
address={
    4194396: 'beq1', 4194412: 'beq2', 4194496: 'beq3', 4194332: 'beq2fact', 4194316: 'beq1fact'
}
memory={
    268501216: 87, 268501220: 98, 268501224: 2, 268501228: 56, 268501232: 55,
}
beqs={
    'beq1': 0, 'beq2': 0, 'beq3': 0, 'beq1fact': 0, 'beq2fact': 0
}
num={'0000':0, '0001':1,'0010':2,'0011':3,'0100':4,'0101':5,'0110':6,'0111':7,'1000':8,'1001':9}

# Instruction Fetch(IF) stage
def IF(pc):
    # Fetches the instruction at the current program counter (pc) position
    line=index[pc] # Retrieves the instruction from the 'index' dictionary using the program counter as the key
    return line # Returns the fetched instruction

#Instruction Decode(ID) stage
def ID(line,pc):
    # Decodes the instruction
    s=line[0:6]  #Extracts the opcode from the instruction
    funct=line[26:32]  #Extracts the function code(for R-type instructions)
    rs=line[6:11] #Source register
    rt=line[11:16] #Target register
    rd=line[16:21] #Destination register
    imm=line[16:32] #Immediate value(for I-type instructions)
    ad=line[6:32] #Address field(for J-type instructions)
    #Determines the type of instruction (R, I, J) and returns appropriate values
    if s in ['000000']:
        return func_codes[funct],rs,rt,rd,imm,ad  #For R-type instructions
    else:
        return opcodes[s],rs,rt,rd,imm,ad #For I and J-type instructions
    
#Execute(EX) stage
def EX(inst,rs,rt,rd,imm,ad,pc,x):
    #Execute the instruction
    #Different actions based on the instruction type
    #'inst' contains the type of instruction (add, sub, etc.), and 'rs', 'rt', 'rd' are register values
    if(inst=='add' or inst=='addu'):
        t=values[reg_codes[rs]]+values[reg_codes[rt]]
    elif(inst=='sub'):
        t=values[reg_codes[rs]]-values[reg_codes[rt]]
    elif(inst=='slt'):
        t=0
        if(values[reg_codes[rs]]<values[reg_codes[rt]]):
            x=1
        else:
            x=0
    elif(inst=='bne'):
        if(values[reg_codes[rs]]!=values[reg_codes[rt]]):
            if(x==1):
                t=int(imm,2)
            else:
                t=0
    elif(inst=='lw' or inst=='sw'):
        t=values[reg_codes[rs]]+int(imm,2)
    elif(inst=='addi'):
        t=values[reg_codes[rs]]+int(imm,2)
    elif(inst=='beq'):
        if(values[reg_codes[rs]]==values[reg_codes[rt]]):
            t=int(imm,2)
        else:
            t=0
    elif(inst=='j'):
        ad='0000'+ad+'00'
        t=(beqs[address[int(ad,2)]]-pc-4)/4
    return t,x  #Returns the result of the operation and an updated flag 'x'

#Memory Access(MEM) stage
def MEM(t,pc,rt,inst,x):
    #Handles memory access operations
    if(inst=='lw' or inst=='sw'):
        #For load and store instructions
        mem=memory[t] #Access memory at the address calculated in the EX stage
        if(inst=='lw'):
            y=mem  #For lw, load the value from memory into the register
        else:
            memory[t]=values[reg_codes[rt]] # For sw, store the register value into memory
            y=0
        return y
    
#Write-back(WB) stage
def WB(t,pc,rd,rt,inst,y):
    #Handles the write-back stage
    if(inst in ['add', 'sub', 'addu']):
        #For arithmetic operations, write the result back to the destination register
        values[reg_codes[rd]]=t
    if(inst in ['addi']):
        #For immediate addition, write the result to the target register
        values[reg_codes[rt]]=t
    if(inst in ['lw']):
        #For load word, write the loaded value to the target register
        values[reg_codes[rt]]=y

#main()   
print("SORTING:")
with open("bubble_sort.txt", 'r') as infile: #bubble sort program
    pc=0 #Program counter initialization
    c=0  #Clock cycle counter initialization
    for line in infile:
        index[pc]=line #Storing each line of machine code with its corresponding program counter value
        k=line[0:6]
        if(k=='000100'): #Checking for branch-equal instructions
            c+=1
            beqs['beq'+str(c)]=pc #Storing branch-equal addresses
        pc=pc+4 #Incrementing the program counter
    b=pc #End address of the program
    pc=0 #Resetting program counter
    x=0 #Variable used in execute stage
    clock_cycle=0 #Initializing the clock cycle counter

    #Loop to execute each instruction in the bubble sort program
    while True:
        if(pc==b): #Exit condition
            break
        #Execute the MIPS instruction cycle stages
        line=IF(pc) 
        inst,rs,rt,rd,imm,ad=ID(line,pc)
        t,x=EX(inst,rs,rt,rd,imm,ad,pc,x)
        y=MEM(t,pc,rt,inst,x)
        WB(t,pc,rd,rt,inst,y)
        if(inst in ['beq','bne','j']): #Branch or jump instructions
            pc=pc+t*4
        pc+=4
        clock_cycle+=1 #Incrementing the clock cycle counter
    for keys in memory.keys():
        print(memory[keys]) #Print out the sorted elements from memory
    print("Number of clock cycles taken are",clock_cycle) #Print the total number of clock cycles taken

print()
print("FACTORIAL:")
index={} #Reset the index dictionary for the new program
values['$t1']=0 #Initialize the register $t1
with open("factorial.txt", 'r') as infile: #factorial program
    pc=0 #Initialize the program counter to 0
    c=0 #Initialize a counter for branch equal (beq) instructions specific to factorial
    for line in infile:
        index[pc]=line #Store each instruction in the index dictionary with the pc as the key
        k=line[0:6] #Extract the opcode from the instruction
        if(k=='000100'):
            c+=1
            beqs['beq'+str(c)+'fact']=pc
        pc=pc+4 #Increment the pc by 4

    b=pc  #Store the final program counter value after reading all instructions
    pc=0 #Reset the program counter to 0 for execution
    x=0 #Initialize a flag variable
    clock_cycle=0 #Initialize a counter for clock cycles
    #Loop to execute each instruction in the factorial program
    while True:
        if(pc==b): #Exit condition
            break
        #Execute the MIPS instruction cycle stages
        line=IF(pc)
        inst,rs,rt,rd,imm,ad=ID(line,pc)
        t,x=EX(inst,rs,rt,rd,imm,ad,pc,x)
        y=MEM(t,pc,rt,inst,x)
        WB(t,pc,rd,rt,inst,y)
        if(inst in ['beq','bne','j']):
            pc=pc+t*4
        pc+=4 #Increment the program counter for the next instruction
        clock_cycle+=1 #Increment the clock cycle counter
    print(values['$s2']) #Print the factorial result stored in register $s2
    print("Number of clock cycles taken are",clock_cycle) #Print the total number of clock cycles taken