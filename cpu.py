import pygame as pg
import numpy as np
import time
import random
# CPU Ricoh 2A03 (from 6502 without decimal mode)
# 16 bit memory addressing
#todo: Not sure if the the overflow bit is setting correctly in ADC and SBC
#      Not sure if the BRK is implemented right


memory = [0b0] * 65536 #65536 ~= 64k

opToLen = {0x69:2, 0x65:2, 0x75:2, 0x6D:3, 0x7D:3, 0x79:3, 0x61:2, 0x71:2, #ADC
           0x29:2, 0x25:2, 0x35:2, 0x2D:3, 0x3D:3, 0x39:2, 0x21:2, 0x31:2, #AND
           0x0A:1, 0x06:2, 0x16:2, 0x0E:3, 0x1E:3, #ASL
           0x10:2, 0x30:2, 0x50:2, 0x70:2, 0x90:2, 0xB0:2, 0xD0:2, 0xF0:2, #BRANCH
           0x24:2, 0x2C:3, #BIT
           0x00:1, #BRK
           0xC9:2, 0xC5:2, 0xD5:2, 0xCD:3, 0xDD:3, 0xD9:3, 0xC1:2, 0xD1:2, #CMP
           0xE0:2, 0xE4:2, 0xEC:3, #CPX
           0xC0:2, 0xC4:2, 0xCC:3, #CPY
           0xC6:2, 0xD6:2, 0xCE:3, 0xDE:3, #DEC
           0x49:2, 0x45:2, 0x55:2, 0x4D:3, 0x5D:3, 0x59:3, 0x41:2, 0x51:2, #EOR
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
            0xC9:2, 0xC5:3, 0xD5:4, 0xCD:4, 0xDD:4+1, 0xD9:4+1, 0xC1:6, 0xD1:5+1, #CMP
            0xE0:2, 0xE4:3, 0xEC:4, #CPX
            0xC0:2, 0xC4:3, 0xCC:4, #CPY
            0xC6:5, 0xD6:6, 0xCE:6, 0xDE:7, #DEC
            0x49:2, 0x45:3, 0x55:4, 0x4D:4, 0x5D:4+1, 0x59:4+1, 0x41:6, 0x51:5+1, #EOR
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

gamecode = [0x20, 0x06, 0x06, 0x20, 0x38, 0x06, 0x20, 0x0d, 0x06, 0x20, 0x2a, 0x06, 0x60, 0xa9, 0x02, 0x85,
    0x02, 0xa9, 0x04, 0x85, 0x03, 0xa9, 0x11, 0x85, 0x10, 0xa9, 0x10, 0x85, 0x12, 0xa9, 0x0f, 0x85,
    0x14, 0xa9, 0x04, 0x85, 0x11, 0x85, 0x13, 0x85, 0x15, 0x60, 0xa5, 0xfe, 0x85, 0x00, 0xa5, 0xfe,
    0x29, 0x03, 0x18, 0x69, 0x02, 0x85, 0x01, 0x60, 0x20, 0x4d, 0x06, 0x20, 0x8d, 0x06, 0x20, 0xc3,
    0x06, 0x20, 0x19, 0x07, 0x20, 0x20, 0x07, 0x20, 0x2d, 0x07, 0x4c, 0x38, 0x06, 0xa5, 0xff, 0xc9,
    0x77, 0xf0, 0x0d, 0xc9, 0x64, 0xf0, 0x14, 0xc9, 0x73, 0xf0, 0x1b, 0xc9, 0x61, 0xf0, 0x22, 0x60,
    0xa9, 0x04, 0x24, 0x02, 0xd0, 0x26, 0xa9, 0x01, 0x85, 0x02, 0x60, 0xa9, 0x08, 0x24, 0x02, 0xd0,
    0x1b, 0xa9, 0x02, 0x85, 0x02, 0x60, 0xa9, 0x01, 0x24, 0x02, 0xd0, 0x10, 0xa9, 0x04, 0x85, 0x02,
    0x60, 0xa9, 0x02, 0x24, 0x02, 0xd0, 0x05, 0xa9, 0x08, 0x85, 0x02, 0x60, 0x60, 0x20, 0x94, 0x06,
    0x20, 0xa8, 0x06, 0x60, 0xa5, 0x00, 0xc5, 0x10, 0xd0, 0x0d, 0xa5, 0x01, 0xc5, 0x11, 0xd0, 0x07,
    0xe6, 0x03, 0xe6, 0x03, 0x20, 0x2a, 0x06, 0x60, 0xa2, 0x02, 0xb5, 0x10, 0xc5, 0x10, 0xd0, 0x06,
    0xb5, 0x11, 0xc5, 0x11, 0xf0, 0x09, 0xe8, 0xe8, 0xe4, 0x03, 0xf0, 0x06, 0x4c, 0xaa, 0x06, 0x4c,
    0x35, 0x07, 0x60, 0xa6, 0x03, 0xca, 0x8a, 0xb5, 0x10, 0x95, 0x12, 0xca, 0x10, 0xf9, 0xa5, 0x02,
    0x4a, 0xb0, 0x09, 0x4a, 0xb0, 0x19, 0x4a, 0xb0, 0x1f, 0x4a, 0xb0, 0x2f, 0xa5, 0x10, 0x38, 0xe9,
    0x20, 0x85, 0x10, 0x90, 0x01, 0x60, 0xc6, 0x11, 0xa9, 0x01, 0xc5, 0x11, 0xf0, 0x28, 0x60, 0xe6,
    0x10, 0xa9, 0x1f, 0x24, 0x10, 0xf0, 0x1f, 0x60, 0xa5, 0x10, 0x18, 0x69, 0x20, 0x85, 0x10, 0xb0,
    0x01, 0x60, 0xe6, 0x11, 0xa9, 0x06, 0xc5, 0x11, 0xf0, 0x0c, 0x60, 0xc6, 0x10, 0xa5, 0x10, 0x29,
    0x1f, 0xc9, 0x1f, 0xf0, 0x01, 0x60, 0x4c, 0x35, 0x07, 0xa0, 0x00, 0xa5, 0xfe, 0x91, 0x00, 0x60,
    0xa6, 0x03, 0xa9, 0x00, 0x81, 0x10, 0xa2, 0x00, 0xa9, 0x01, 0x81, 0x10, 0x60, 0xa2, 0x00, 0xea,
    0xea, 0xca, 0xd0, 0xfb, 0x60]

class CPU:
    def __init__(self):
        self.pc = 0b0                 # 16 bit
        self.register_a = 0b0         # 8 bit
        self.sp = 0b11111111          # 8 bit
        self.register_x = 0b0         # 8 bit
        self.register_y = 0b0         # 8 bit
        self.status = 0b00110000      # 8 bit  
        
        #status
        #NV1B DIZC
        #|||| ||||
        #|||| |||+- Carry
        #|||| ||+-- Zero
        #|||| |+--- Interrupt Disable
        #|||| +---- Decimal
        #|||+------ (No CPU effect; see: the B flag)
        #||+------- (No CPU effect; always pushed as 1)
        #|+-------- Overflow
        #+--------- Negative

 #   def fetch():
 #   def decode():
 #   def execute():
    
    def run(self):
        #fetch opcode
        opcode = memory[self.pc]
        #DEBUG
        print("==============================================")
        print("PC=", hex(cpu.pc), "opcode=", hex(opcode))

        self.pc+=1
        #decode & execute
        #ADC
        if opcode in [0x69, 0x65, 0x75, 0x6D, 0x7D, 0x79, 0x61, 0x71]:
            origin = self.register_a
            toadd = 0
            if opcode==0x69: #Immediate
                toadd = memory[self.pc]
                self.register_a += memory[self.pc]
            elif opcode==0x65: #Zero Page
                toadd = memory[memory[self.pc]]
                self.register_a += memory[memory[self.pc]]
            elif opcode==0x75: #Zero Page X
                toadd = memory[memory[self.pc]+self.register_x]
                self.register_a += memory[memory[self.pc]+self.register_x]
            elif opcode==0x6D: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                toadd = memory[addr]
                self.register_a += memory[addr]
            elif opcode==0x7D: #Abosolute,X
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                toadd = memory[addr+self.register_x]
                self.register_a += memory[addr+self.register_x]
            elif opcode==0x79: #Abosolute,Y
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                toadd = memory[addr+self.register_y]
                self.register_a += memory[addr+self.register_y]
            elif opcode==0x61: #(Indirect,X)
                toadd = memory[memory[memory[self.pc] + self.register_x]]
                self.register_a += memory[memory[memory[self.pc] + self.register_x]]
            elif opcode==0x71: #(Indirect,)Y
                toadd = memory[memory[memory[self.pc]] + self.register_y]
                self.register_a += memory[memory[memory[self.pc]] + self.register_y]
            # Handle overflow, and set the flag
            if self.register_a > 255:
                    self.register_a %= 256
                    self.status |= 0b00000001 # Carry flag
            else:
                self.status &= 0b11111110
            if self.register_a == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if self.register_a & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            if (origin^self.register_a)&0b10000000:
                self.status = self.status | 0b01000000
            else:
                self.status = self.status & 0b10111111
            self.pc += (opToLen[opcode]-1)
            print("ADC")
        #AND
        if opcode in [0x29, 0x25, 0x35, 0x2D, 0x3D, 0x39, 0x21, 0x31]:
            if opcode==0x29: #Immediate
                self.register_a &= memory[self.pc]
            elif opcode==0x25: #Zero Page
                self.register_a &= memory[memory[self.pc]]
            elif opcode==0x35: #Zero Page X
                self.register_a &= memory[memory[self.pc]+self.register_x]
            elif opcode==0x2D: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                self.register_a &= memory[addr]
            elif opcode==0x3D: #Abosolute,X
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                self.register_a &= memory[addr+self.register_x]
            elif opcode==0x39: #Abosolute,Y
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                self.register_a &= memory[addr+self.register_y]
            elif opcode==0x21: #(Indirect,X)
                self.register_a &= memory[memory[memory[self.pc] + self.register_x]]
            elif opcode==0x31: #(Indirect,)Y
                self.register_a &= memory[memory[memory[self.pc]] + self.register_y]
            if self.register_a == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if self.register_a & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            print("AND")
        #ASL
        if opcode in [0x0A, 0x06, 0x16, 0x0E, 0x1E]:
            bit7 = 0
            res = 0
            if opcode==0x0A: #Accumulator
                bit7 = self.register_a|0b10000000
                self.register_a <<= 1
                res = self.register_a
                self.register_a &= 0b11111111
            elif opcode==0x06: #Zero Page
                bit7 = memory[memory[self.pc]]|0b10000000
                memory[memory[self.pc]] <<= 1
                res = memory[memory[self.pc]]
                memory[memory[self.pc]] &= 0b11111111
            elif opcode==0x16: #Zero Page X
                bit7 = memory[memory[self.pc]+self.register_x] | 0b10000000
                memory[memory[self.pc]+self.register_x] <<= 1
                res = memory[memory[self.pc]+self.register_x]
                memory[memory[self.pc]+self.register_x] &= 0b11111111
            elif opcode==0x0E: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                bit7 = memory[addr]|0b10000000
                memory[addr] <<= 1
                res = memory[addr]
                memory[addr] &= 0b11111111
            elif opcode==0x1E: #Abosolute,X
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                bit7 = memory[addr+self.register_x]|0b10000000
                memory[addr+self.register_x] <<= 1
                res = memory[addr+self.register_x]
                memory[addr+self.register_x] &= 0b11111111
            # Handle overflow, and set the flag
            if bit7 & 0b10000000:
                self.status |= 0b00000001 # Carry flag
            else:
                self.status &= 0b11111110
            if res & 0b11111111 == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if res & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            print("ASL")
        #BIT
        if opcode in [0x24, 0x2C]:
            res = 0
            tested = 0
            if opcode==0x24: #Zero Page
                tested = memory[memory[self.pc]]
                res = self.register_a & tested
            elif opcode==0x2C: #Absolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                tested = memory[addr]
                res = self.register_a & tested
            if res == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if tested & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            if tested & 0b01000000:
                self.status = self.status | 0b01000000
            else:
                self.status = self.status & 0b10111111
            self.pc += (opToLen[opcode]-1)
            print("BIT")
        #BRANCH
        if opcode in [0x10, 0x30, 0x50, 0x70, 0x90, 0xB0, 0xD0, 0xF0]:
            print("op ", hex(opcode), "staus ", hex(self.status), "offset ", hex(memory[self.pc]), hex(memory[self.pc+1]))
            jump = False
            offset = memory[self.pc]
            if opcode==0x10:   #BPL
                jump = (self.status & 0b10000000)==0
            elif opcode==0x30: #BMI
                jump = (self.status & 0b10000000)
            elif opcode==0x50: #BVC
                jump = (self.status & 0b01000000)==0
            elif opcode==0x70: #BVS
                jump = (self.status & 0b01000000)
            elif opcode==0x90: #BCC
                jump = (self.status & 0b00000001)==0
            elif opcode==0xB0: #BCS
                jump = (self.status & 0b00000001)
            elif opcode==0xD0: #BNE
                jump = (self.status & 0b00000010)==0
            elif opcode==0xF0: #BEQ
                jump = (self.status & 0b00000010)
            self.pc += (opToLen[opcode]-1)
            if offset&0b10000000:
                offset=((offset^0b11111111)+1)%256
                offset=-offset
                print("hoho", offset)
            if jump:
                self.pc = self.pc+offset
            print("BRANCH")
        #BRK
        if opcode in [0x00]:
            #currently nop
            print("BRK")
        #CMP
        if opcode in [0xC9, 0xC5, 0xD5, 0xCD, 0xDD, 0xD9, 0xC1, 0xD1]:
            print("cmp", hex(opcode), "a", hex(self.register_a))
            res = 0
            if opcode==0xC9: #Immediate
                res = self.register_a - memory[self.pc]
            elif opcode==0xC5: #Zero Page
                res = self.register_a - memory[memory[self.pc]]
            elif opcode==0xD5: #Zero Page X
                res = self.register_a - memory[memory[self.pc]+self.register_x]
            elif opcode==0xCD: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                res = self.register_a - memory[addr]
            elif opcode==0xDD: #Abosolute,X
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                res = self.register_a - memory[addr+self.register_x]
            elif opcode==0xD9: #Abosolute,Y
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                res = self.register_a - memory[addr+self.register_y]
            elif opcode==0xC1: #(Indirect,X)
                res = self.register_a - memory[memory[memory[self.pc] + self.register_x]]
            elif opcode==0xD1: #(Indirect,)Y
                res = self.register_a - memory[memory[memory[self.pc]] + self.register_y]
            # Handle overflow, and set the flag
            if res < 0:
                self.status |= 0b00000001 # Carry flag
            else:
                self.status &= 0b11111110
            if res == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if res & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            print("CMP")
        #CPX
        if opcode in [0xE0, 0xE4, 0xEC]:
            res = 0
            if opcode==0xC9: #Immediate
                res = self.register_x - memory[self.pc]
            elif opcode==0xC5: #Zero Page
                res = self.register_x - memory[memory[self.pc]]
            elif opcode==0xCD: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                res = self.register_x - memory[addr]
            if res >= 0:
                self.status |= 0b00000001 # Carry flag
            else:
                self.status &= 0b11111110
            if res == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if res & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            print("CPX")
        #CPY
        if opcode in [0xC0, 0xC4, 0xCC]:
            res = 0
            if opcode==0xC9: #Immediate
                res = self.register_y - memory[self.pc]
            elif opcode==0xC5: #Zero Page
                res = self.register_y - memory[memory[self.pc]]
            elif opcode==0xCD: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                res = self.register_y - memory[addr]
            if res >= 0:
                self.status |= 0b00000001 # Carry flag
            else:
                self.status &= 0b11111110
            if res == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if res & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            print("CPY")
        #DEC
        if opcode in [0xC6, 0xD6, 0xCE, 0xDE]:
            res = 0
            if opcode==0xC6: #Zero Page
                memory[memory[self.pc]] -= 1
                res = memory[memory[self.pc]]
                memory[memory[self.pc]] &= 0b11111111
            elif opcode==0xD6: #Zero Page X
                memory[memory[self.pc]+self.register_x] -= 1
                res = memory[memory[self.pc]+self.register_x]
                memory[memory[self.pc]+self.register_x] &= 0b11111111
            elif opcode==0xCE: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                memory[addr] -= 1
                res = memory[addr]
                memory[addr] &= 0b11111111
            elif opcode==0xDE: #Abosolute,X
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                memory[addr+self.register_x] -= 1
                res = memory[addr+self.register_x]
                memory[addr+self.register_x] &= 0b11111111
            if res == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if res & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            print("DEC")
        #EOR
        if opcode in [0x49, 0x45, 0x55, 0x4D, 0x5D, 0x59, 0x41, 0x51]:
            if opcode==0x49: #Immediate
                self.register_a ^= memory[self.pc]
            elif opcode==0x45: #Zero Page
                self.register_a ^= memory[memory[self.pc]]
            elif opcode==0x55: #Zero Page X
                self.register_a ^= memory[memory[self.pc]+self.register_x]
            elif opcode==0x4D: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                self.register_a ^= memory[addr]
            elif opcode==0x5D: #Abosolute,X
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                self.register_a ^= memory[addr+self.register_x]
            elif opcode==0x59: #Abosolute,Y
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                self.register_a ^= memory[addr+self.register_y]
            elif opcode==0x41: #(Indirect,X)
                self.register_a ^= memory[memory[memory[self.pc] + self.register_x]]
            elif opcode==0x51: #(Indirect,)Y
                self.register_a ^= memory[memory[memory[self.pc]] + self.register_y]
            self.register_a &= (0b11111111) # make sure a register has only 1 byte
            if self.register_a == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if self.register_a & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            print("EOR")
        #FLAG
        if opcode in [0x18, 0x38, 0x58, 0x78, 0xB8, 0xD8, 0xF8]:
            print("FLAG")
            if opcode==0x18: #CLC
                self.status = self.status & 0b11111110
            elif opcode==0x38: #SEC
                self.status = self.status | 0b00000001
            elif opcode==0x58: #CLI
                self.status = self.status & 0b11111011
            elif opcode==0x78: #SEI
                self.status = self.status | 0b00000100
            elif opcode==0xB8: #CLV
                self.status = self.status & 0b10111111
            elif opcode==0xD8: #CLD
                self.status = self.status & 0b11101111
            elif opcode==0xF8: #SED
                self.status = self.status | 0b00010000

        #INC
        if opcode in [0xE6, 0xF6, 0xEE, 0xFE]:
            res = 0
            if opcode==0xE6: #Zero Page
                memory[memory[self.pc]] += 1
                res = memory[memory[self.pc]]
                memory[memory[self.pc]] &= 0b11111111
            elif opcode==0xF6: #Zero Page X
                memory[memory[self.pc]+self.register_x] += 1
                res = memory[memory[self.pc]+self.register_x]
                memory[memory[self.pc]+self.register_x] &= 0b11111111
            elif opcode==0xEE: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                memory[addr] += 1
                res = memory[addr]
                memory[addr] &= 0b11111111
            elif opcode==0xFE: #Abosolute,X
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                memory[addr+self.register_x] += 1
                res = memory[addr+self.register_x]
                memory[addr+self.register_x] &= 0b11111111
            if res == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if res & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            print("INC")
        #JMP
        if opcode in [0x4C, 0x6C]:
            if opcode==0x4C: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                self.pc = memory[addr]
            elif opcode==0x6C: #Indirect
                #AN INDIRECT JUMP MUST NEVER USE A
                #VECTOR BEGINNING ON THE LAST BYTE
                #OF A PAGE
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                self.pc = memory[(addr&0xFF00)<<8 | (addr+1)%0x100] << 8 | memory[addr]
            print("JMP")
        #JSR
        if opcode in [0x20]:
            byte1 = memory[self.pc]
            byte2 = memory[self.pc+1]
            addr =  byte2 << 8 | byte1
            self.pc+=1
            memory[self.sp+0x100] = (self.pc & 0xff00) >> 8
            memory[self.sp-1+0x100] = (self.pc & 0xff)
            self.sp -= 2
            self.pc = addr
            print("JSR")
        #LDA
        if opcode in [0xA9, 0xA5, 0xB5, 0xAD, 0xBD, 0xB9, 0xA1, 0xB1]:
            print(hex(opcode), hex(memory[self.pc]), memory[self.pc])
            if opcode==0xA9: #Immediate
                byte1 = memory[self.pc]
                self.register_a = byte1
            elif opcode==0xA5: #Zero Page
                byte1 = memory[memory[self.pc]]
                self.register_a = byte1
            elif opcode==0xB5: #Zero Page X
                byte1 = memory[memory[self.pc]+self.register_x]
                self.register_a = byte1
            elif opcode==0xAD: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                add =  byte2 << 8 | byte1
                self.register_a = memory[add]
            elif opcode==0xBD: #Abosolute,X
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                add =  byte2 << 8 | byte1
                self.register_a = memory[add+self.register_x]
            elif opcode==0xB9: #Abosolute,Y
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                add =  byte2 << 8 | byte1
                self.register_a = memory[add+self.register_y]
            elif opcode==0xA1: #(Indirect,X)
                byte1 = memory[self.pc]
                add = byte1 + self.register_x
                self.register_a = memory[memory[add]]
            elif opcode==0xB1: #(Indirect,)Y
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
            self.pc += (opToLen[opcode]-1)
            print("LDA")
        #LDX
        if opcode in [0xA2, 0xA6, 0xB6, 0xAE, 0xBE]:
            if opcode==0xA2: #Immediate
                self.register_x = memory[self.pc]
            elif opcode==0xA6: #Zero Page
                self.register_x = memory[memory[self.pc]]
            elif opcode==0xB6: #Zero Page Y
                self.register_x = memory[memory[self.pc]+self.register_y]
            elif opcode==0xAE: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                self.register_x = memory[addr]
            elif opcode==0xBE: #Abosolute,Y
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                self.register_x = memory[addr+self.register_y]
            if self.register_x == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if self.register_x & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            print("LDX")
        #LDY
        if opcode in [0xA0, 0xA4, 0xB4, 0xAC, 0xBC]:
            if opcode==0xA2: #Immediate
                self.register_y = memory[self.pc]
            elif opcode==0xA6: #Zero Page
                self.register_y = memory[memory[self.pc]]
            elif opcode==0xB6: #Zero Page X
                self.register_y = memory[memory[self.pc]+self.register_x]
            elif opcode==0xAE: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                self.register_y = memory[addr]
            elif opcode==0xBE: #Abosolute,X
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                self.register_y = memory[addr+self.register_x]
            if self.register_y == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if self.register_y & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            print("LDY")
        #LSR
        if opcode in [0x4A, 0x46, 0x56, 0x4E, 0x5E]:
            bit0 = 0
            res = 0
            if opcode==0x4A: #Accumulator
                bit0 = self.register_a&0b00000001
                self.register_a >>= 1
                res = self.register_a
            elif opcode==0x46: #Zero Page
                bit0 = memory[memory[self.pc]]&0b00000001
                memory[memory[self.pc]] >>= 1
                res = memory[memory[self.pc]]
            elif opcode==0x56: #Zero Page X
                bit0 = memory[memory[self.pc]+self.register_x]&0b00000001
                memory[memory[self.pc]+self.register_x] >>= 1
                res = memory[memory[self.pc]+self.register_x]
            elif opcode==0x4E: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                bit0 = memory[addr] & 0b00000001
                memory[addr] >>= 1
                res = memory[addr]
            elif opcode==0x5E: #Abosolute,X
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                memory[addr+self.register_x] | 0b00000001
                memory[addr+self.register_x] >>= 1
                res = memory[addr+self.register_x]
            # Handle overflow, and set the flag
            if bit0:
                self.status |= 0b00000001 # Carry flag
            else:
                self.status &= 0b11111110
            if self.register_a == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if self.register_a & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            print("LSR")
        #NOP
        if opcode in [0xEA]:
            print("NOP")
        #ORA
        if opcode in [0x09, 0x05, 0x15, 0x0D, 0x1D, 0x19, 0x01, 0x11]:
            if opcode==0x09: #Immediate
                self.register_a |= memory[self.pc]
            elif opcode==0x05: #Zero Page
                self.register_a |= memory[memory[self.pc]]
            elif opcode==0x15: #Zero Page X
                self.register_a |= memory[memory[self.pc]+self.register_x]
            elif opcode==0x0D: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                self.register_a |= memory[addr]
            elif opcode==0x1D: #Abosolute,X
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                self.register_a |= memory[addr+self.register_x]
            elif opcode==0x19: #Abosolute,Y
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                self.register_a |= memory[addr+self.register_y]
            elif opcode==0x01: #(Indirect,X)
                self.register_a |= memory[memory[memory[self.pc] + self.register_x]]
            elif opcode==0x11: #(Indirect,)Y
                self.register_a |= memory[memory[memory[self.pc]] + self.register_y]
            if self.register_a == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if self.register_a & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            print("ORA")
        #Register Instructions
        if opcode in [0xAA, 0x8A, 0xCA, 0xE8, 0xA8, 0x98, 0x88, 0xC8]:
            bit7 = 0
            res = 0
            if opcode==0xAA: #TAX
                self.register_x = self.register_a
                bit7 = self.register_x & 0b10000000
                res = self.register_x
            elif opcode==0x8A: #TXA
                self.register_a = self.register_x
                bit7 = self.register_a & 0b10000000
                res = self.register_a
            elif opcode==0xCA: #DEX
                self.register_x-=1
                self.register_x %= 256
                bit7 = self.register_x & 0b10000000
                res = self.register_x
            elif opcode==0xE8: #INX
                self.register_x+=1
                self.register_x %= 256
                bit7 = self.register_x & 0b10000000
                res = self.register_x
            elif opcode==0xA8: #TAY
                self.register_y = self.register_a
                bit7 = self.register_y & 0b10000000
                res = self.register_y
            elif opcode==0x98: #TYA
                self.register_a = self.register_y
                bit7 = self.register_a & 0b10000000
                res = self.register_a
            elif opcode==0x88: #DEY
                self.register_y-=1
                self.register_y %= 256
                bit7 = self.register_y & 0b10000000
                res = self.register_y
            elif opcode==0xC8: #INY
                self.register_y+=1
                self.register_y %= 256
                bit7 = self.register_y & 0b10000000
                res = self.register_y

            if bit7:
                self.status |= 0b10000000
            else:
                self.status &= 0b01111111
            if res == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            print("Register Instructions")
        #ROL
        if opcode in [0x2A, 0x26, 0x36, 0x2E, 0x3E]:
            bit7 = 0
            res = 0
            if opcode==0x2A: #Accumulator
                bit7 = self.register_a & 0b10000000
                self.register_a <<= 1
                self.register_a |= (self.status & 0b00000001)
                res = self.register_a
            elif opcode==0x26: #Zero Page
                bit7 = memory[memory[self.pc]] & 0b10000000
                memory[memory[self.pc]] <<= 1
                memory[memory[self.pc]] |= (self.status & 0b00000001)
                res = memory[memory[self.pc]]
            elif opcode==0x36: #Zero Page X
                bit7 = memory[memory[self.pc]+self.register_x]  & 0b10000000
                memory[memory[self.pc]+self.register_x] <<= 1
                memory[memory[self.pc]+self.register_x] |= (self.status & 0b00000001)
                res = memory[memory[self.pc]+self.register_x]
            elif opcode==0x2E: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                bit7 = memory[addr] & 0b10000000
                memory[addr] <<= 1
                memory[addr] |= (self.status & 0b00000001)
                res = memory[addr]
            elif opcode==0x3E: #Abosolute,x
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                bit7 = memory[addr+self.register_x] & 0b10000000
                memory[addr+self.register_x] <<= 1
                memory[addr+self.register_x] |= (self.status & 0b00000001)
                res = memory[addr+self.register_x]
            if bit7:
                self.status | 0b00000001
            else:
                self.status & 0b11111110
            if res == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            print("ROL")
        #ROR
        if opcode in [0x6A, 0x66, 0x76, 0x6E, 0x7E]:
            bit0 = 0
            res = 0
            if opcode==0x6A: #Accumulator
                bit0 = self.register_a & 0b00000001
                self.register_a <<= 1
                self.register_a |= ((self.status & 0b00000001)<<7)
                res = self.register_a
            elif opcode==0x66: #Zero Page
                bit0 = memory[memory[self.pc]] & 0b00000001
                memory[memory[self.pc]] <<= 1
                memory[memory[self.pc]] |= ((self.status & 0b00000001)<<7)
                res = memory[memory[self.pc]]
            elif opcode==0x76: #Zero Page X
                bit0 = memory[memory[self.pc]+self.register_x]  & 0b00000001
                memory[memory[self.pc]+self.register_x] <<= 1
                memory[memory[self.pc]+self.register_x] |= ((self.status & 0b00000001)<<7)
                res = memory[memory[self.pc]+self.register_x]
            elif opcode==0x6E: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                bit0 = memory[addr] & 0b00000001
                memory[addr] <<= 1
                memory[addr] |= ((self.status & 0b00000001)<<7)
                res = memory[addr]
            elif opcode==0x7E: #Abosolute,x
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                bit0 = memory[addr+self.register_x] & 0b00000001
                memory[addr+self.register_x] <<= 1
                memory[addr+self.register_x] |= ((self.status & 0b00000001)<<7)
                res = memory[addr+self.register_x]
            if bit0:
                self.status | 0b00000001
            else:
                self.status & 0b11111110
            if res == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            print("ROR")
        #RTI
        if opcode in [0x40]:
            self.sp += 1
            self.status = memory[self.sp+0x100]
            self.pc = memory[self.sp+2+0x100]<<8 | memory[self.sp+1+0x100]
            self.sp += 2
            print("RTI")
        #RTS
        if opcode in [0x60]:
            self.pc = (memory[self.sp+2+0x100]<<8 | memory[self.sp+1+0x100]) + 1
            self.sp += 2
            print("RTS")
        #SBC
        if opcode in [0xE9, 0xE5, 0xF5, 0xED, 0xFD, 0xF9, 0xE1, 0xF1]:
            carry = self.status|0b00000001
            tosub = 0
            if opcode==0x69: #Immediate
                tosub = memory[self.pc]
                self.register_a = self.register_a - memory[self.pc] - (1-carry)
            elif opcode==0x65: #Zero Page
                tosub = memory[memory[self.pc]]
                self.register_a = self.register_a - memory[memory[self.pc]] - (1-carry)
            elif opcode==0x75: #Zero Page X
                tosub = memory[memory[self.pc]+self.register_x]
                self.register_a = self.register_a - memory[memory[self.pc]+self.register_x] - (1-carry)
            elif opcode==0x6D: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                tosub = memory[addr]
                self.register_a = self.register_a - memory[addr] - (1-carry)
            elif opcode==0x7D: #Abosolute,X
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                tosub = memory[addr+self.register_x]
                self.register_a = self.register_a - memory[addr+self.register_x] - (1-carry)
            elif opcode==0x79: #Abosolute,Y
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                tosub = memory[addr+self.register_y]
                self.register_a = self.register_a - memory[addr+self.register_y] - (1-carry)
            elif opcode==0x61: #(Indirect,X)
                tosub = memory[memory[memory[self.pc] + self.register_x]]
                self.register_a = self.register_a - memory[memory[memory[self.pc] + self.register_x]] - (1-carry)
            elif opcode==0x71: #(Indirect,)Y
                tosub = memory[memory[memory[self.pc]] + self.register_y]
                self.register_a = self.register_a - memory[memory[memory[self.pc]] + self.register_y] - (1-carry)
            # Handle overflow, and set the flag
            if self.register_a < 0:
                self.register_a |= 0b11111111
                self.status |= 0b00000001 # Carry flag
            else:
                self.status &= 0b11111110
            if self.register_a == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if self.register_a & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            if ((origin^tosub)&0b10000000) and ((origin^self.register_a)&0b10000000):
                self.status = self.status | 0b01000000
            else:
                self.status = self.status & 0b10111111
            self.pc += (opToLen[opcode]-1)
            print("SBC")
        #STA
        if opcode in [0x85, 0x95, 0x8D, 0x9D, 0x99, 0x81, 0x91]:
            #print(hex(opcode))
            if opcode==0x85: #Zero Page
                #print(memory[self.pc], self.register_a)
                memory[memory[self.pc]] = self.register_a
            elif opcode==0x95: #Zero Page X
                memory[memory[self.pc]+self.register_x] = self.register_a
            elif opcode==0x8D: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                memory[addr] = self.register_a
            elif opcode==0x9D: #Abosolute,X
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                memory[addr+self.register_x] = self.register_a
            elif opcode==0x99: #Abosolute,Y
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                memory[addr+self.register_y] = self.register_a
            elif opcode==0x81: #(Indirect,X)
                memory[memory[memory[self.pc] + self.register_x]] = self.register_a
            elif opcode==0x91: #(Indirect,)Y
                memory[memory[memory[self.pc]] + self.register_y] = self.register_a
            self.pc += (opToLen[opcode]-1)
            print("STA")
        #STACK INSTRUCTION
        # the stack is always on page one ($100-$1FF) and works top down
        if opcode in [0x9A, 0xBA, 0x48, 0x68, 0x08, 0x28]:
            print("STACK INSTRUCTION")
            if opcode==0x9A: #TXS
                self.sp = self.register_x
            elif opcode==0xBA: #TSX
                self.register_x = self.sp
            elif opcode==0x48: #PHA
                memory[self.sp+0x100] = self.register_a
                self.sp-=1
            elif opcode==0x68: #PLA
                self.sp+=1
                self.register_a = memory[self.sp+0x100]
            elif opcode==0x08: #PHP
                memory[self.sp+0x100] = self.status
                self.sp-=1
            elif opcode==0x29: #PLP
                self.sp+=1
                self.status = memory[self.sp+0x100]
        #STX
        if opcode in [0x86, 0x96, 0x8E]:
            if opcode==0x86: #Zero Page
                memory[memory[self.pc]] = register_x
            elif opcode==0x96: #Zero Page Y
                memory[memory[self.pc]+self.register_y] = register_x
            elif opcode==0x8E: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                memory[addr] = register_x
            self.pc += (opToLen[opcode]-1)
            print("STX")
        #STY
        if opcode in [0x84, 0x94, 0x8C]:
            if opcode==0x84: #Zero Page
                memory[memory[self.pc]] = register_y
            elif opcode==0x94: #Zero Page X
                memory[memory[self.pc]+self.register_x] = register_y
            elif opcode==0x8C: #Abosolute
                byte1 = memory[self.pc]
                byte2 = memory[self.pc+1]
                addr =  byte2 << 8 | byte1
                memory[addr] = register_y
            self.pc += (opToLen[opcode]-1)
            print("STY")
        print("new PC=", hex(self.pc), "opcode=", hex(opcode))
        print('reg.A=', hex(self.register_a))
        print('reg.X=', hex(self.register_x))
        print('reg.Y=', hex(self.register_y))
        print('SP=', hex(self.sp))
        print('reg.status=', bin(self.status))
        
        print("stack content:", memory[self.sp+0x100:0x200])
#def render:

#def io:

def load_game():
    for i in range(len(gamecode)):
        memory[0x600+i] = gamecode[i]

if __name__=="__main__":
    pg.init()
    screen = pg.display.set_mode((640, 480))
    colors = np.array([[120, 250, 90], [250, 90, 120], [255, 255, 255]])
    toRend = np.array(memory[0x0200:0x0600], dtype = np.int32)
    gridarray = np.reshape(toRend, (32, 32))
    surface = pg.surfarray.make_surface(colors[gridarray])
    surface = pg.transform.scale(surface, (400, 400))
    clock = pg.time.Clock()

    cpu = CPU()
    cpu.pc = 0x600
    #memory[0xff] = 0x77
    memory[0xfe] = random.randint(1, 255)
    load_game()
    running = True
    while running:
        memory[0xfe] = random.randint(1, 255)
        #render image
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        toRend = np.array(memory[0x0200:0x0600], dtype = np.int32)
        gridarray = np.reshape(toRend, (32, 32))
        #for x in range(0x200, 0x300):
        #print((memory[0x0000:0x0030]))
        #print((memory[0x01F0:0x0200]))
        #print(sum(memory[0x0200:0x0600]))
        surface = pg.surfarray.make_surface(colors[gridarray])
        surface = pg.transform.scale(surface, (400, 400))
        screen.fill((30, 30, 30))
        screen.blit(surface, (0, 0))
        pg.display.flip()
        cpu.run()
        clock.tick(60)
        inp = input("wait")
        if inp=='m':
            print("mem content:", memory[:0x20])
        #time.sleep(1)
    print("init cpu")