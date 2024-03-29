# 16 bit memory addressing
memory = [bin(0)] * 65536 #65536 ~= 64k

opToLen = {0x69:2, 0x65:2, 0x75:2, 0x6D:3, 0x7D:3, 0x79:3, 0x61:2, 0x71:2, #ADC
           0x29:2, 0x25:2, 0x35:2, 0x2D:3, 0x3D:3, 0x39:2, 0x21:2, 0x31:2, #AND
           0x0A:1, 0x06:2, 0x16:2, 0x0E:3, 0x1E:3, #ASL
           0x10:2, 0x30:2, 0x50:2, 0x70:2, 0x90:2, 0xB0:2, 0xD0:2, 0xF0:2, #BRANCH
           0x24:2, 0x2C:3, #BIT
           0x00:1, #BRK
           0x18:1, 0x38:1, 0x58:1, 0x78:1, 0xB8:1, 0xD8:1, 0xF8:1, #FLAG
           0xE6:2, 0xF6:2, 0xEE:3, 0xFE:3, #INC
           0x4C:3, 0x6C:3, #JMP
           0x20:3, #JSR
           0xA9:2, 0xA5:2, 0xB5:2, 0xAD:3, 0xBD:3, 0xB9:3, 0xA1:2, 0xB1:2, #LDA
           0xA2:2, 0xA6:2, 0xB6:2, 0xAE:3, 0xBE:3, #LDX
           0xA0:2, 0xA4:2, 0xB4:2, 0xAC:3, 0xBC:3, #LDY
           0x4A:1, 0x46:2, 0x56:2, 0x4E:3, 0x5E:3, #LSR
           0xEA:1, #NOP
           0x09:2, 0x05:2, 0x15:2, 0x0D:3, 0x1D:3, 0x19:3, 0x01:2, 0x11:2, #ORA
           0xAA:1, 0x8A:1, 0xCA:1, 0xE8:1, 0xA8:1, 0x98:1, 0x88:1, 0xC8:1, #Register Instructions
           0x2A:1, 0x26:2, 0x36:2, 0x2E:3, 0x3E:3, #ROL
           0x6A:1, 0x66:2, 0x76:2, 0x6E:3, 0x7E:3, #ROR
           0x40:1, #RTI
           0x60:1, #RTS
           0xE9:2, 0xE5:2, 0xF5:2, 0xED:3, 0xFD:3, 0xF9:3, 0xE1:2, 0xF1:2, #SBC
           0x85:2, 0x95:2, 0x8D:3, 0x9D:3, 0x99:3, 0x81:2, 0x91:2, #STA
           0x9A:0, 0xBA:0, 0x48:0, 0x68:0, 0x08:0, 0x28:0, #STACK INSTRUCTION
           0x86:2, 0x96:2, 0x8E:3, #STX
           0x84:2, 0x94:2, 0x8C:3 #STY
           }  
opToTime = {0x69:2, 0x65:3, 0x75:4, 0x6D:4, 0x7D:4+1, 0x79:4+1, 0x61:6, 0x71:5+1, #ADC
            0x29:2, 0x25:3, 0x35:4, 0x2D:4, 0x3D:4+1, 0x39:4+1, 0x21:6, 0x31:5+1, #AND
            0x0A:2, 0x06:5, 0x16:6, 0x0E:6, 0x1E:7, #ASL
            0x10:2+1+2, 0x30:2+1+2, 0x50:2+1+2, 0x70:2+1+2, 0x90:2+1+2, 0xB0:2+1+2, 0xD0:2+1+2, 0xF0:2+1+2, #BRANCH
            0x24:3, 0x2C:4, #BIT
            0x00:7, #BRK
            0x18:2, 0x38:2, 0x58:2, 0x78:2, 0xB8:2, 0xD8:2, 0xF8:2, #FLAG
            0xE6:5, 0xF6:6, 0xEE:6, 0xFE:7, #INC
            0x4C:3, 0x6C:5, #JMP
            0x20:6, #JSR
            0xA9:2, 0xA5:3, 0xB5:4, 0xAD:4, 0xBD:4+1, 0xB9:4+1, 0xA1:6, 0xB1:5+1, #LDA
            0xA2:3, 0xA6:3, 0xB6:4, 0xAE:4, 0xBE:4+1, #LDX
            0xA0:2, 0xA4:3, 0xB4:4, 0xAC:4, 0xBC:4+1, #LDY
            0x4A:2, 0x46:5, 0x56:6, 0x4E:6, 0x5E:7, #LSR
            0xEA:2, #NOP
            0x09:2, 0x05:3, 0x15:4, 0x0D:4, 0x1D:4+1, 0x19:4+1, 0x01:6, 0x11:5, #ORA
            0xAA:2, 0x8A:2, 0xCA:2, 0xE8:2, 0xA8:2, 0x98:2, 0x88:2, 0xC8:2, #Register Instructions
            0x2A:2, 0x26:5, 0x36:6, 0x2E:6, 0x3E:7, #ROL
            0x6A:2, 0x66:5, 0x76:6, 0x6E:6, 0x7E:7, #ROR
            0x40:6, #RTI
            0x60:6, #RTS
            0xE9:2, 0xE5:3, 0xF5:4, 0xED:4, 0xFD:4+1, 0xF9:4+1, 0xE1:6, 0xF1:5+1, #SBC
            0x85:3, 0x95:4, 0x8D:4, 0x9D:5, 0x99:5, 0x81:6, 0x91:6, #STA
            0x9A:2, 0xBA:2, 0x48:3, 0x68:4, 0x08:3, 0x28:4, #STACK INSTRUCTION
            0x86:3, 0x96:4, 0x8E:4, #STX
            0x84:3, 0x94:4, 0x8C:4 #STY
            }  

class cpu:
    def __init__(self):
        self.pc = bin(0) # 16 bit
        self.register_a = bin(0) # 8 bit
        self.sp = bin(0) # 8 bit
        self.register_x = bin(0) # 8 bit
        self.register_y = bin(0) # 8 bit
        self.status = bin(0)  # 8 bit

 #   def fetch():
 #   def decode():
 #   def execute():
    
    def run():
        #fetch opcode
        opcode = memory[self.pc]
        self.pc+=1
        #decode & execute
        #ADC
        if opcode in [0x69, 0x65, 0x75, 0x6D, 0x7D, 0x79, 0x61, 0x71]:
            print("ADC")
        #AND
        if opcode in [0x29, 0x25, 0x35, 0x2D, 0x3D, 0x39, 0x21, 0x31]:
            print("AND")
        #ASL
        if opcode in [0x0A, 0x06, 0x16, 0x0E, 0x1E]:
            print("ASL")
        #BIT
        if opcode in [0x24, 0x2C]:
            print("BIT")
        #BRANCH
        if opcode in [0x10, 0x30, 0x50, 0x70, 0x90, 0xB0, 0xD0, 0xF0]:
            print("BRANCH")
        #BRK
        if opcode in [0x00]:
            print("BRK")
        #CMP
        if opcode in [0xC9, 0xC5, 0xD5, 0xCD, 0xDD, 0xD9, 0xC1, 0xD1]:
            print("CMP")
        #CPX
        if opcode in [0xE0, 0xE4, 0xEC]:
            print("CPX")
        #CPY
        if opcode in [0xC0, 0xC4, 0xCC]:
            print("CPY")
        #DEC
        if opcode in [0xC6, 0xD6, 0xCE, 0xDE]:
            print("DEC")
        #EOR
        if opcode in [0x49, 0x45, 0x55, 0x4D, 0x5D, 0x59, 0x41, 0x51]:
            print("EOR")
        #FLAG
        if opcode in [0x18, 0x38, 0x58, 0x78, 0xB8, 0xD8, 0xF8]:
            print("FLAG")
        #INC
        if opcode in [0xE6, 0xF6, 0xEE, 0xFE]:
            print("INC")
        #JMP
        if opcode in [0x4C, 0x6C]:
            print("JMP")
        #JSR
        if opcode in [0x20]:
            print("JSR")
        #LDA
        if opcode in [0xA9, 0xA5, 0xB5, 0xAD, 0xBD, 0xB9, 0xA1, 0xB1]:
            if opcode==0xA9: #Immediate
                byte1 = memory[self.pc]
                self.register_a = byte1
            if opcode==0xA9: #Zero Page
                byte1 = memory[memory[self.pc]]
                self.register_a = byte1
            if opcode==0xA9: #Zero Page X
                byte1 = memory[memory[self.pc]+self.register_x]
                self.register_a = byte1
            if opcode==0xA9: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                add =  byte2 << 8 | byte1
                self.register_a = memory[add]
            if opcode==0xA9: #Abosolute,X
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                add =  byte2 << 8 | byte1
                self.register_a = memory[add+self.register_x]]
            if opcode==0xA9: #Abosolute,Y
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                add =  byte2 << 8 | byte1
                self.register_a = memory[add+self.register_y]]
            if opcode==0xA9: #Indirect,X
                byte1 = memory[self.pc]
                add = byte1 + self.register_x
                self.register_a = memory[memory[add]]
            if opcode==0xA9: #Indirect,Y
                byte1 = memory[self.pc]
                addr = memory[byte1] + self.register_y
                self.register_a = memory[addr]
            if self.register_a == 0x0:
                    self.status = self.status | 0b00000010
                else:
                    self.status = self.status & 0b11111101
                if self.register_a & 0b10000000:
                    self.status = self.status | 0b10000000
                else:
                    self.status = self.status & 0b01111111
            self.pc += opToLen[self.pc]
            print("LDA")
        #LDX
        if opcode in [0xA2, 0xA6, 0xB6, 0xAE, 0xBE]:
            print("LDX")
        #LDY
        if opcode in [0xA0, 0xA4, 0xB4, 0xAC, 0xBC]:
            print("LDY")
        #LSR
        if opcode in [0x4A, 0x46, 0x56, 0x4E, 0x5E]:
            print("LSR")
        #NOP
        if opcode in [0xEA]:
            print("NOP")
        #ORA
        if opcode in [0x09, 0x05, 0x15, 0x0D, 0x1D, 0x19, 0x01, 0x11]:
            print("ORA")
        #Register Instructions
        if opcode in [0xAA, 0x8A, 0xCA, 0xE8, 0xA8, 0x98, 0x88, 0xC8]:
            print("Register Instructions")
        #ROL
        if opcode in [0x2A, 0x26, 0x36, 0x2E, 0x3E]:
            print("ROL")
        #ROR
        if opcode in [0x6A, 0x66, 0x76, 0x6E, 0x7E]:
            print("ROR")
        #RTI
        if opcode in [0x40]:
            print("RTI")
        #RTS
        if opcode in [0x60]:
            print("RTS")
        #SBC
        if opcode in [0xE9, 0xE5, 0xF5, 0xED, 0xFD, 0xF9, 0xE1, 0xF1]:
            print("SBC")
        #STA
        if opcode in [0x85, 0x95, 0x8D, 0x9D, 0x99, 0x81, 0x91]:
            print("STA")
        #STACK INSTRUCTION
        if opcode in [0x9A, 0xBA, 0x48, 0x68, 0x08, 0x28]:
            print("STACK INSTRUCTION")
        #STX
        if opcode in [0x86, 0x96, 0x8E]:
            print("STX")
        #STY
        if opcode in [0x84, 0x94, 0x8C]:
            print("STY")
       
        
