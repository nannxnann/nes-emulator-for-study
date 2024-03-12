# 16 bit memory addressing
memory = [bin(0)] * 65536 #65536 ~= 64k

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
       
        
