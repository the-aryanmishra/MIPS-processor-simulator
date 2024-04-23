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
phase=['IF','ID','EX','MEM','WB']
instructions=[]
address={
    4194396: 'beq1', 4194412: 'beq2', 4194496: 'beq3', 4194332: 'beq2fact', 4194316: 'beq1fact'
}
memory={
    268501216: 87, 268501220: 98, 268501224: 2, 268501228: 56, 268501232: 55
}
beqs={
    'beq1': 0, 'beq2': 0, 'beq3': 0, 'beq1fact': 0, 'beq2fact': 0
}

# Pipeline registers for each stage of the pipeline
IFID_pipeline={'line': '','pc': 0}
IDEX_pipeline={'inst': '','rs': '','rt': '','rd': '','imm': '','ad': '','pc': 0}
EXMEM_pipeline={'inst': '','rt': '','rd': '','t': 0}
MEMWB_pipeline={'inst': '','rt': '','rd': '','t': 0}
# Number mapping dictionary
num={'0000':0, '0001':1,'0010':2,'0011':3,'0100':4,'0101':5,'0110':6,'0111':7,'1000':8,'1001':9}


# Instruction Fetch (IF) stage
def IF(pc):
    line = index[pc]  # Fetches the instruction at the current program counter (pc) position
    return line  # Returns the fetched instruction

# Instruction Decode (ID) stage
def ID(line, pc):
    s = line[0:6]  # Extracts the opcode from the instruction
    funct = line[26:32]  # Extracts the function code (for R-type instructions)
    rs = line[6:11]  # Source register
    rt = line[11:16]  # Target register
    rd = line[16:21]  # Destination register (for R-type instructions)
    imm = line[16:32]  # Immediate value (for I-type instructions)
    ad = line[6:32]  # Address field (for J-type instructions)
    if s in ['000000']:
        return func_codes[funct], rs, rt, rd, imm, ad  # For R-type instructions
    else:
        return opcodes[s], rs, rt, rd, imm, ad  # For I-type and J-type instructions

#Execution (EX) stage
def EX(inst,rs,rt,rd,imm,ad,pc,x,ors,ort):
    # Handle forwarding and stalls for hazard prevention
    if(inst=='add' or inst=='addu'):
        # Forwarding logic for add, addu, and sub instructions
        if(ors==0 and ort==0):
            t=values[reg_codes[rs]]+values[reg_codes[rt]]
        elif(ors!=0): # Forwarding from ORS (old rs value)
            t=ors+values[reg_codes[rt]]
        else:
            t=values[reg_codes[rs]]+ort  # Forwarding from ORT (old rt value)
    elif(inst=='sub'):
        if(ors==0 and ort==0):
            t=values[reg_codes[rs]]-values[reg_codes[rt]]
        elif(ors!=0):
            t=ors-values[reg_codes[rt]]
        else:
            t=values[reg_codes[rs]]-ort
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
        # For the j instruction, calculate the jump address
        ad='0000'+ad+'00'
        t=(beqs[address[int(ad,2)]]-pc-4)/4
    return t,x # Return the result of the operation and an updated flag 'x'

#Memory(MEM) stage    
def MEM(t,pc,rt,inst,x):
    if(inst=='lw' or inst=='sw'):
        mem=memory[t]  # Access memory at the address calculated in the EX stage
        if(inst=='lw'):
            y=mem
        else:
            memory[t]=values[reg_codes[rt]]
            y=0
        return y

#Write-back(WB) stage
def WB(t,pc,rd,rt,inst,y):
    #Write the result back to the appropriate register for arithmetic and load instructions
    if(inst in ['add', 'sub', 'addu']):
        values[reg_codes[rd]]=t
    if(inst in ['addi']):
        values[reg_codes[rt]]=t
    if(inst in ['lw']):
        values[reg_codes[rt]]=y

#Bubble sort part
print("SORTING:")
with open("bubble_sort.txt", 'r') as infile:
    pc=0
    c=0
    for line in infile:
        index[pc]=line
        k=line[0:6]
        if(k=='000100'):
            c+=1
            beqs['beq'+str(c)]=pc
        pc=pc+4
    b=pc
    pc=0
    x=0
    for u in range(0,5):
        instructions.append(['IF','ID','EX','MEM','WB'])
    clock_cycle=0
    j=0
    flag=0
    # Handling pipeline stages and hazards
    while True:
        # Initialize variables for pipeline processing and hazard detection
        c=0
        b_over=0
        flag2=0 # Flag for data hazard detection
        ors=0  # Forwarding value for source operand
        ort=0  # Forwarding value for target operand
        if(pc==b): # Check if all instructions are processed
            break
        # Process each pipeline stage for the current instruction
        while True:
            if(pc==b):
                break
            k=instructions[c].pop(0)

            if(k=='IF'):
                line=IF(pc)
                IFID_pipeline['line']=line
                IFID_pipeline['pc']=pc
                break
            elif(k=='ID'):
                inst,rs,rt,rd,imm,ad=ID(IFID_pipeline['line'],IFID_pipeline['pc'])
                if(flag!=1):
                    IDEX_pipeline['inst']=inst
                    IDEX_pipeline['rs']=rs
                    IDEX_pipeline['rt']=rt
                    IDEX_pipeline['rd']=rd
                    IDEX_pipeline['imm']=imm
                    IDEX_pipeline['ad']=ad
                    IDEX_pipeline['pc']=IFID_pipeline['pc']
            # Hazard handling in the Execute (EX) stage
            elif(k=='EX'):
                t,x=EX(IDEX_pipeline['inst'],IDEX_pipeline['rs'],IDEX_pipeline['rt'],IDEX_pipeline['rd'],IDEX_pipeline['imm'],IDEX_pipeline['ad'],IDEX_pipeline['pc'],x,ors,ort)
                EXMEM_pipeline['inst']=IDEX_pipeline['inst']
                EXMEM_pipeline['rt']=IDEX_pipeline['rt']
                EXMEM_pipeline['rd']=IDEX_pipeline['rd']
                EXMEM_pipeline['rs']=IDEX_pipeline['rs']
                EXMEM_pipeline['imm']=IDEX_pipeline['imm']
                EXMEM_pipeline['ad']=IDEX_pipeline['ad']
                EXMEM_pipeline['pc']=IDEX_pipeline['pc']
                EXMEM_pipeline['t']=t
                if(IDEX_pipeline['inst'] in ['beq','bne','j']):
                    if(t!=0):
                        pc+=t*4
                        for l in range(c+1,5):
                            instructions[l]=['IF','ID','EX','MEM','WB']
            elif(k=='MEM'):
                y=MEM(EXMEM_pipeline['t'],pc,EXMEM_pipeline['rt'],EXMEM_pipeline['inst'],x)
                MEMWB_pipeline['inst']=EXMEM_pipeline['inst']
                MEMWB_pipeline['rd']=EXMEM_pipeline['rd']
                MEMWB_pipeline['rt']=EXMEM_pipeline['rt']
                MEMWB_pipeline['rs']=EXMEM_pipeline['rs']
                MEMWB_pipeline['imm']=EXMEM_pipeline['imm']
                MEMWB_pipeline['ad']=EXMEM_pipeline['ad']
                MEMWB_pipeline['pc']=EXMEM_pipeline['pc']
                MEMWB_pipeline['t']=EXMEM_pipeline['t']
                MEMWB_pipeline['y']=y
                if(EXMEM_pipeline['inst'] in ['add', 'sub', 'addu'] and (EXMEM_pipeline['rd'] in [IDEX_pipeline['rs'], IDEX_pipeline['rt']])):
                    flag2=1
                    if(EXMEM_pipeline['rd']==IDEX_pipeline['rs']):
                        ors=EXMEM_pipeline['t']
                    else:
                        ort=EXMEM_pipeline['t']
                if(EXMEM_pipeline['inst'] in ['addi'] and (EXMEM_pipeline['rt'] in [IDEX_pipeline['rs'], IDEX_pipeline['rt']])):
                    flag2=1
                    if(EXMEM_pipeline['rt']==IDEX_pipeline['rs']):
                        ors=EXMEM_pipeline['t']
                    else:
                        ort=EXMEM_pipeline['t']
                if(EXMEM_pipeline['inst']=='lw' and (EXMEM_pipeline['rt'] in [IDEX_pipeline['rs'],IDEX_pipeline['rt']])):
                    flag=1
                    if(EXMEM_pipeline['rt']==IDEX_pipeline['rs']):
                        prs=1
                    else:
                        prt=1
                    break
                if(EXMEM_pipeline['inst'] in ['beq', 'bne', 'j']):
                    if(EXMEM_pipeline['t']!=0):
                        pc+=EXMEM_pipeline['t']*4
            elif(k=='WB'):
                WB(MEMWB_pipeline['t'],pc,MEMWB_pipeline['rd'],MEMWB_pipeline['rt'],MEMWB_pipeline['inst'],MEMWB_pipeline['y'])
                if(prs==1):
                    ors=MEMWB_pipeline['t']
                if(prt==1):
                    ort=MEMWB_pipeline['t']
                if(MEMWB_pipeline['inst'] in ['add', 'sub'] and (MEMWB_pipeline['rd'] in [IDEX_pipeline['rs'], IDEX_pipeline['rt']])):
                    flag2=1
                    if(EXMEM_pipeline['rd']==IDEX_pipeline['rs']):
                        ors=EXMEM_pipeline['t']
                    else:
                        ort=EXMEM_pipeline['t']
                if(MEMWB_pipeline['inst'] in ['addi'] and (MEMWB_pipeline['rt'] in [IDEX_pipeline['rs'], IDEX_pipeline['rt']])):
                    flag2=1
                    if(EXMEM_pipeline['rt']==IDEX_pipeline['rs']):
                        ors=EXMEM_pipeline['t']
                    else:
                        ort=EXMEM_pipeline['t']
                if(MEMWB_pipeline['inst'] in ['beq', 'bne']):
                    if(MEMWB_pipeline['t']!=0):
                        pc+=MEMWB_pipeline['t']*4
                        v=MEMWB_pipeline['t']*4
                        b_over=1
                if(MEMWB_pipeline['inst']=='j'):
                    pc+=MEMWB_pipeline['t']*4
                    v=MEMWB_pipeline['t']*4
                    b_over=1
            #if(flag==1):
                
            prs=0
            prt=0
            flag=0
            pc+=4
            c+=1
        clock_cycle+=1
        if [] in instructions:
            instructions.pop(0)
            instructions.append(['IF','ID','EX','MEM','WB']) 
            if(b_over==1):
                j+=v
            j+=4
        pc=j
    for keys in memory.keys():
        print(memory[keys])
    print("The number of clock cycles are",clock_cycle)

print()

#Factorial of a number(In this case, of 9)

print("FACTORIAL:")
index={}
values['$t1']=0
with open("factorial.txt", 'r') as infile:
    pc=0
    c=0
    for line in infile:
        index[pc]=line
        k=line[0:6]
        if(k=='000100'):
            c+=1
            beqs['beq'+str(c)+'fact']=pc
        pc=pc+4
    b=pc
    pc=0
    x=0
    for u in range(0,5):
        instructions.append(['IF','ID','EX','MEM','WB'])
    clock_cycle=0
    j=0
    flag=0
    while True:
        c=0
        b_over=0
        flag2=0
        ors=0
        ort=0
        if(pc==b):
            break
        while True:
            if(pc==b):
                break
            k=instructions[c].pop(0)
            if(k=='IF'):
                line=IF(pc)
                IFID_pipeline['line']=line
                IFID_pipeline['pc']=pc
                break
            elif(k=='ID'):
                inst,rs,rt,rd,imm,ad=ID(IFID_pipeline['line'],IFID_pipeline['pc'])
                if(flag!=1):
                    IDEX_pipeline['inst']=inst
                    IDEX_pipeline['rs']=rs
                    IDEX_pipeline['rt']=rt
                    IDEX_pipeline['rd']=rd
                    IDEX_pipeline['imm']=imm
                    IDEX_pipeline['ad']=ad
                    IDEX_pipeline['pc']=IFID_pipeline['pc']
            elif(k=='EX'):
                t,x=EX(IDEX_pipeline['inst'],IDEX_pipeline['rs'],IDEX_pipeline['rt'],IDEX_pipeline['rd'],IDEX_pipeline['imm'],IDEX_pipeline['ad'],IDEX_pipeline['pc'],x,ors,ort)
                EXMEM_pipeline['inst']=IDEX_pipeline['inst']
                EXMEM_pipeline['rt']=IDEX_pipeline['rt']
                EXMEM_pipeline['rd']=IDEX_pipeline['rd']
                EXMEM_pipeline['rs']=IDEX_pipeline['rs']
                EXMEM_pipeline['imm']=IDEX_pipeline['imm']
                EXMEM_pipeline['ad']=IDEX_pipeline['ad']
                EXMEM_pipeline['pc']=IDEX_pipeline['pc']
                EXMEM_pipeline['t']=t
                if(IDEX_pipeline['inst'] in ['beq','bne','j']):
                    if(t!=0):
                        pc+=t*4
                        for l in range(c+1,5):
                            instructions[l]=['IF','ID','EX','MEM','WB']
            elif(k=='MEM'):
                y=MEM(EXMEM_pipeline['t'],pc,EXMEM_pipeline['rt'],EXMEM_pipeline['inst'],x)
                MEMWB_pipeline['inst']=EXMEM_pipeline['inst']
                MEMWB_pipeline['rd']=EXMEM_pipeline['rd']
                MEMWB_pipeline['rt']=EXMEM_pipeline['rt']
                MEMWB_pipeline['rs']=EXMEM_pipeline['rs']
                MEMWB_pipeline['imm']=EXMEM_pipeline['imm']
                MEMWB_pipeline['ad']=EXMEM_pipeline['ad']
                MEMWB_pipeline['pc']=EXMEM_pipeline['pc']
                MEMWB_pipeline['t']=EXMEM_pipeline['t']
                MEMWB_pipeline['y']=y
                if(EXMEM_pipeline['inst'] in ['add', 'sub', 'addu'] and (EXMEM_pipeline['rd'] in [IDEX_pipeline['rs'], IDEX_pipeline['rt']])):
                    flag2=1
                    if(EXMEM_pipeline['rd']==IDEX_pipeline['rs']):
                        ors=EXMEM_pipeline['t']
                    else:
                        ort=EXMEM_pipeline['t']
                if(EXMEM_pipeline['inst'] in ['addi'] and (EXMEM_pipeline['rt'] in [IDEX_pipeline['rs'], IDEX_pipeline['rt']])):
                    flag2=1
                    if(EXMEM_pipeline['rt']==IDEX_pipeline['rs']):
                        ors=EXMEM_pipeline['t']
                    else:
                        ort=EXMEM_pipeline['t']
                if(EXMEM_pipeline['inst']=='lw' and (EXMEM_pipeline['rt'] in [IDEX_pipeline['rs'],IDEX_pipeline['rt']])):
                    flag=1
                    if(EXMEM_pipeline['rt']==IDEX_pipeline['rs']):
                        prs=1
                    else:
                        prt=1
                    break
                if(EXMEM_pipeline['inst'] in ['beq', 'bne', 'j']):
                    if(EXMEM_pipeline['t']!=0):
                        pc+=EXMEM_pipeline['t']*4
            elif(k=='WB'):
                WB(MEMWB_pipeline['t'],pc,MEMWB_pipeline['rd'],MEMWB_pipeline['rt'],MEMWB_pipeline['inst'],MEMWB_pipeline['y'])
                if(prs==1):
                    ors=MEMWB_pipeline['t']
                if(prt==1):
                    ort=MEMWB_pipeline['t']
                if(MEMWB_pipeline['inst'] in ['add', 'sub'] and (MEMWB_pipeline['rd'] in [IDEX_pipeline['rs'], IDEX_pipeline['rt']])):
                    flag2=1
                    if(EXMEM_pipeline['rd']==IDEX_pipeline['rs']):
                        ors=EXMEM_pipeline['t']
                    else:
                        ort=EXMEM_pipeline['t']
                if(MEMWB_pipeline['inst'] in ['addi'] and (MEMWB_pipeline['rt'] in [IDEX_pipeline['rs'], IDEX_pipeline['rt']])):
                    flag2=1
                    if(EXMEM_pipeline['rt']==IDEX_pipeline['rs']):
                        ors=EXMEM_pipeline['t']
                    else:
                        ort=EXMEM_pipeline['t']
                if(MEMWB_pipeline['inst'] in ['beq', 'bne']):
                    if(MEMWB_pipeline['t']!=0):
                        pc+=MEMWB_pipeline['t']*4
                        v=MEMWB_pipeline['t']*4
                        b_over=1
                if(MEMWB_pipeline['inst']=='j'):
                    pc += MEMWB_pipeline['t']*4
                    v=MEMWB_pipeline['t']*4
                    b_over=1
            prs=0
            prt=0
            flag=0
            pc+=4
            c+=1
        clock_cycle+=1
        if [] in instructions:
            instructions.pop(0)
            instructions.append(['IF','ID','EX','MEM','WB']) 
            if(b_over==1):
                j+=v
            j+=4
        pc=j
    print(values['$s2'])
    print("The number of clock cycles are",clock_cycle)