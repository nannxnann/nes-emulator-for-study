import pygame as pg
import numpy as np
import time
import random
import sys
import json
from ppu import PPU

# this is the implementation that connect memory to ppu
# which may not pass harte test
lst_cycles = 0
no_extra_absx = [0x1E, 0xFE, 0xDE, 0x5E, 0x3E, 0x7E, 0x9D]
no_extra_absy = [0x99]
no_extra_indy = [0x91]

op_to_asembly = {0x69:"ADC", 0x65:"ADC", 0x75:"ADC", 0x6D:"ADC", 0x7D:"ADC", 0x79:"ADC", 0x61:"ADC", 0x71:"ADC", #ADC
           0x29:"AND", 0x25:"AND", 0x35:"AND", 0x2D:"AND", 0x3D:"AND", 0x39:"AND", 0x21:"AND", 0x31:"AND", #AND
           0x0A:"ASL", 0x06:"ASL", 0x16:"ASL", 0x0E:"ASL", 0x1E:"ASL", #ASL
           0x10:"BRANCH", 0x30:"BRANCH", 0x50:"BRANCH", 0x70:"BRANCH", 0x90:"BRANCH", 0xB0:"BRANCH", 0xD0:"BRANCH", 0xF0:"BRANCH", #BRANCH
           0x24:"BIT", 0x2C:"BIT", #BIT
           0x00:"BRK", #BRK
           0xC9:"CMP", 0xC5:"CMP", 0xD5:"CMP", 0xCD:"CMP", 0xDD:"CMP", 0xD9:"CMP", 0xC1:"CMP", 0xD1:"CMP", #CMP
           0xE0:"CPX", 0xE4:"CPX", 0xEC:"CPX", #CPX
           0xC0:"CPY", 0xC4:"CPY", 0xCC:"CPY",#CPY
           0xC6:"DEC", 0xD6:"DEC", 0xCE:"DEC", 0xDE:"DEC", #DEC
           0x49:"EOR", 0x45:"EOR", 0x55:"EOR", 0x4D:"EOR", 0x5D:"EOR", 0x59:"EOR", 0x41:"EOR", 0x51:"EOR", #EOR
           0x18:"FLAG", 0x38:"FLAG", 0x58:"FLAG", 0x78:"FLAG", 0xB8:"FLAG", 0xD8:"FLAG", 0xF8:"FLAG", #FLAG
           0xE6:"INC", 0xF6:"INC", 0xEE:"INC", 0xFE:"INC", #INC
           0x4C:"JMP", 0x6C:"JMP", #JMP
           0x20:"JSR", #JSR
           0xA9:"LDA", 0xA5:"LDA", 0xB5:"LDA", 0xAD:"LDA", 0xBD:"LDA", 0xB9:"LDA", 0xA1:"LDA", 0xB1:"LDA", #LDA
           0xA2:"LDX", 0xA6:"LDX", 0xB6:"LDX", 0xAE:"LDX", 0xBE:"LDX", #LDX
           0xA0:"LDY", 0xA4:"LDY", 0xB4:"LDY", 0xAC:"LDY", 0xBC:"LDY", #LDY
           0x4A:"LSR", 0x46:"LSR", 0x56:"LSR", 0x4E:"LSR", 0x5E:"LSR", #LSR
           0xEA:"NOP", #NOP
           0x09:"ORA", 0x05:"ORA", 0x15:"ORA", 0x0D:"ORA", 0x1D:"ORA", 0x19:"ORA", 0x01:"ORA", 0x11:"ORA", #ORA
           0xAA:"RG", 0x8A:"RG", 0xCA:"RG", 0xE8:"RG", 0xA8:"RG", 0x98:"RG", 0x88:"RG", 0xC8:"RG", #Register Instructions
           0x2A:"ROL", 0x26:"ROL", 0x36:"ROL", 0x2E:"ROL", 0x3E:"ROL", #ROL
           0x6A:"ROR", 0x66:"ROR", 0x76:"ROR", 0x6E:"ROR", 0x7E:"ROR", #ROR
           0x40:"RTI", #RTI
           0x60:"RTS", #RTS
           0xE9:"SBC", 0xE5:"SBC", 0xF5:"SBC", 0xED:"SBC", 0xFD:"SBC", 0xF9:"SBC", 0xE1:"SBC", 0xF1:"SBC", #SBC
           0x85:"STA", 0x95:"STA", 0x8D:"STA", 0x9D:"STA", 0x99:"STA", 0x81:"STA", 0x91:"STA", #STA
           0x9A:"STACK", 0xBA:"STACK", 0x48:"STACK", 0x68:"STACK", 0x08:"STACK", 0x28:"STACK", #STACK INSTRUCTION
           0x86:"STX", 0x96:"STX", 0x8E:"STX", #STX
           0x84:"STY", 0x94:"STY", 0x8C:"STY", #STY
           #unofficial
           }

implemented = ["69", "65", "75", "6D", "7D", "79", "61", "71", #ADC
           "29", "25", "35", "2D", "3D", "39", "21", "31", #AND
           "0A", "06", "16", "0E", "1E", #ASL
           "10", "30", "50", "70", "90", "B0", "D0", "F0", #BRANCH
           "24", "2C", #BIT
           "00", #BRK
           "C9", "C5", "D5", "CD", "DD", "D9", "C1", "D1", #CMP
           "E0", "E4", "EC", #CPX
           "C0", "C4", "CC", #CPY
           "C6", "D6", "CE", "DE", #DEC
           "49", "45", "55", "4D", "5D", "59", "41", "51", #EOR
           "18", "38", "58", "78", "B8", "D8", "F8", #FLAG
           "E6", "F6", "EE", "FE", #INC
           "4C", "6C", #JMP
           "20", #JSR
           "A9", "A5", "B5", "AD", "BD", "B9", "A1", "B1", #LDA
           "A2", "A6", "B6", "AE", "BE", #LDX
           "A0", "A4", "B4", "AC", "BC", #LDY
           "4A", "46", "56", "4E", "5E", #LSR
           "EA", #NOP
           "09", "05", "15", "0D", "1D", "19", "01", "11", #ORA
           "AA", "8A", "CA", "E8", "A8", "98", "88", "C8", #Register Instructions
           "2A", "26", "36", "2E", "3E", #ROL
           "6A", "66", "76", "6E", "7E", #ROR
           "40", #RTI
           "60", #RTS
           "E9", "E5", "F5", "ED", "FD", "F9", "E1", "F1", #SBC
           "85", "95", "8D", "9D", "99", "81", "91", #STA
           "9A", "BA", "48", "68", "08", "28", #STACK INSTRUCTION
           "86", "96", "8E", #STX
           "84", "94", "8C", #STY
           #unofficial
           "0B","2B", #AAC
           ]

opToLen = {0x69:2, 0x65:2, 0x75:2, 0x6D:3, 0x7D:3, 0x79:3, 0x61:2, 0x71:2, #ADC
           0x29:2, 0x25:2, 0x35:2, 0x2D:3, 0x3D:3, 0x39:3, 0x21:2, 0x31:2, #AND
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
           0x84:2, 0x94:2, 0x8C:3, #STY
           #unofficial
           0x0B:2, 0x2B:2, #AAC
           0x87:2, 0x97:2, 0x83:2, 0x8F:3, #AAX
           0x6B:2, #ARR
           }  
opToTime = {0x69:2, 0x65:3, 0x75:4, 0x6D:4, 0x7D:4, 0x79:4, 0x61:6, 0x71:5, #ADC
            0x29:2, 0x25:3, 0x35:4, 0x2D:4, 0x3D:4, 0x39:4, 0x21:6, 0x31:5, #AND
            0x0A:2, 0x06:5, 0x16:6, 0x0E:6, 0x1E:7, #ASL
            0x10:2, 0x30:2, 0x50:2, 0x70:2, 0x90:2, 0xB0:2, 0xD0:2, 0xF0:2, #BRANCH
            0x24:3, 0x2C:4, #BIT
            0x00:7, #BRK
            0xC9:2, 0xC5:3, 0xD5:4, 0xCD:4, 0xDD:4, 0xD9:4, 0xC1:6, 0xD1:5, #CMP
            0xE0:2, 0xE4:3, 0xEC:4, #CPX
            0xC0:2, 0xC4:3, 0xCC:4, #CPY
            0xC6:5, 0xD6:6, 0xCE:6, 0xDE:7, #DEC
            0x49:2, 0x45:3, 0x55:4, 0x4D:4, 0x5D:4, 0x59:4, 0x41:6, 0x51:5, #EOR
            0x18:2, 0x38:2, 0x58:2, 0x78:2, 0xB8:2, 0xD8:2, 0xF8:2, #FLAG
            0xE6:5, 0xF6:6, 0xEE:6, 0xFE:7, #INC
            0x4C:3, 0x6C:5, #JMP
            0x20:6, #JSR
            0xA9:2, 0xA5:3, 0xB5:4, 0xAD:4, 0xBD:4, 0xB9:4, 0xA1:6, 0xB1:5, #LDA
            0xA2:2, 0xA6:3, 0xB6:4, 0xAE:4, 0xBE:4, #LDX
            0xA0:2, 0xA4:3, 0xB4:4, 0xAC:4, 0xBC:4, #LDY
            0x4A:2, 0x46:5, 0x56:6, 0x4E:6, 0x5E:7, #LSR
            0xEA:2, #NOP
            0x09:2, 0x05:3, 0x15:4, 0x0D:4, 0x1D:4, 0x19:4, 0x01:6, 0x11:5, #ORA
            0xAA:2, 0x8A:2, 0xCA:2, 0xE8:2, 0xA8:2, 0x98:2, 0x88:2, 0xC8:2, #Register Instructions
            0x2A:2, 0x26:5, 0x36:6, 0x2E:6, 0x3E:7, #ROL
            0x6A:2, 0x66:5, 0x76:6, 0x6E:6, 0x7E:7, #ROR
            0x40:6, #RTI
            0x60:6, #RTS
            0xE9:2, 0xE5:3, 0xF5:4, 0xED:4, 0xFD:4, 0xF9:4, 0xE1:6, 0xF1:5, #SBC
            0x85:3, 0x95:4, 0x8D:4, 0x9D:5, 0x99:5, 0x81:6, 0x91:6, #STA
            0x9A:2, 0xBA:2, 0x48:3, 0x68:4, 0x08:3, 0x28:4, #STACK INSTRUCTION
            0x86:3, 0x96:4, 0x8E:4, #STX
            0x84:3, 0x94:4, 0x8C:4, #STY
            #unofficial
            0x0B:2, 0x2B:2, #AAC
            0x87:3, 0x97:4, 0x83:6, 0x8F:4, #AAX
            0x6B:2, #ARR
            }  

#addrmode 0: Immediate, 1: Zero Page, 2: Zero PageX, 3: Absolute, 4: AbsoluteX, 5: AbsoluteY,
#6: (Inderect,X), 7:(Inderect,)Y, 8:accumulate, 9:Inderect, 10: Zero PageY
op_to_mode = {
            0x69:0, 0x65:1, 0x75:2, 0x6D:3, 0x7D:4, 0x79:5, 0x61:6, 0x71:7, #ADC ok
            0x29:0, 0x25:1, 0x35:2, 0x2D:3, 0x3D:4, 0x39:5, 0x21:6, 0x31:7,#AND ok
            0x0A:8, 0x06:1, 0x16:2, 0x0E:3, 0x1E:4, #ASL ok
            0x10:2, 0x30:2, 0x50:2, 0x70:2, 0x90:2, 0xB0:2, 0xD0:2, 0xF0:2, #BRANCH ?
            0x24:1, 0x2C:3, #BIT ok
            0x00:7, #BRK ?
            0xC9:0, 0xC5:1, 0xD5:2, 0xCD:3, 0xDD:4, 0xD9:5, 0xC1:6, 0xD1:7, #CMP ok
            0xE0:0, 0xE4:1, 0xEC:3, #CPX ok
            0xC0:0, 0xC4:1, 0xCC:3, #CPY ok
            0xC6:1, 0xD6:2, 0xCE:3, 0xDE:4, #DEC ok
            0x49:0, 0x45:1, 0x55:2, 0x4D:3, 0x5D:4, 0x59:5, 0x41:6, 0x51:7, #EOR ok
            0x18:2, 0x38:2, 0x58:2, 0x78:2, 0xB8:2, 0xD8:2, 0xF8:2, #FLAG ?
            0xE6:1, 0xF6:2, 0xEE:3, 0xFE:4, #INC ok
            0x4C:3, 0x6C:9, #JMP ok
            0x20:6, #JSR ?
            0xA9:0, 0xA5:1, 0xB5:2, 0xAD:3, 0xBD:4, 0xB9:5, 0xA1:6, 0xB1:7, #LDA ok
            0xA2:0, 0xA6:1, 0xB6:10, 0xAE:3, 0xBE:5, #LDX ok
            0xA0:0, 0xA4:1, 0xB4:2, 0xAC:3, 0xBC:4, #LDY ok
            0x4A:0, 0x46:1, 0x56:2, 0x4E:3, 0x5E:4, #LSR ok
            0xEA:2, #NOP ok
            0x09:0, 0x05:1, 0x15:2, 0x0D:3, 0x1D:4, 0x19:5, 0x01:6, 0x11:7, #ORA ok
            0xAA:2, 0x8A:2, 0xCA:2, 0xE8:2, 0xA8:2, 0x98:2, 0x88:2, 0xC8:2, #Register Instructions ?
            0x2A:8, 0x26:1, 0x36:2, 0x2E:3, 0x3E:4, #ROL ok
            0x6A:8, 0x66:1, 0x76:2, 0x6E:3, 0x7E:4, #ROR ok
            0x40:6, #RTI ?
            0x60:6, #RTS ?
            0xE9:0, 0xE5:1, 0xF5:2, 0xED:3, 0xFD:4, 0xF9:5, 0xE1:6, 0xF1:7, #SBC ok
            0x85:1, 0x95:2, 0x8D:3, 0x9D:4, 0x99:5, 0x81:6, 0x91:7, #STA ok
            0x9A:2, 0xBA:2, 0x48:3, 0x68:4, 0x08:3, 0x28:4, #STACK INSTRUCTION ?
            0x86:1, 0x96:10, 0x8E:3, #STX ok
            0x84:1, 0x94:2, 0x8C:3, #STY ok
            #unofficial
            0x0B:0, 0x2B:0, #AAC
            0x87:1, 0x97:10, 0x83:6, 0x8F:3, #AAX
            0x6B:0, #ARR
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

# CPU Ricoh 2A03 (from 6502 without decimal mode)
# 16 bit memory addressing
#todo: Not sure if the the overflow bit is setting correctly in ADC and SBC
#      Not sure if the BRK is implemented right


memory = [0b0] * (65536) #65536 ~= 64k
ppu_rg_map = set([i for i in range(0x2000, 0x3FFF)])

class BUS:
    def __init__(self, cpu):
        self.debug = 0
        self.cpu = cpu
        self.ppu_write_func = [self.write_PPUCTRL, self.write_PPUMASK, self.write_PPUSTATUS, self.write_OAMADDR, self.write_OAMDATA,
                               self.write_PPUSCROLL, self.write_PPUADDR, self.write_PPUDATA]
        self.ppu_read_func = [self.read_PPUCTRL, self.read_PPUMASK, self.read_PPUSTATUS, self.read_OAMADDR, self.read_OAMDATA,
                               self.read_PPUSCROLL, self.read_PPUADDR, self.read_PPUDATA]
        #print("cpu bus init done")
    def write_PPUCTRL(self, data):
        self.cpu.ppu.write_ctrl(data)
    def write_PPUMASK(self, data):
        self.cpu.ppu.write_mask(data)
    def write_PPUSTATUS(self, data):
        if self.debug:
            print("not allow to write ppu reg_status")
    def write_OAMADDR(self, data):
        self.cpu.ppu.write_oamaddr(data)
        if self.debug:
            print("oops we write reg_oamaddr, better implemented it write")
    def write_OAMDATA(self, data):
        self.cpu.ppu.write_oamdata(data)
        if self.debug:
            print("Do not write directly to this register in most cases, better implemented it write")
    def write_PPUSCROLL(self, data):
        if self.debug:
            print("scroll game not support yet")
    def write_PPUADDR(self, data):
        self.cpu.ppu.write_vramaddr(data)
    def write_PPUDATA(self, data):
        self.cpu.ppu.write_vramdata(data)
    def write_OAMDMA(self, data):
        if self.debug:
            print("dma need to be implemented", hex(data))
    
    def read_PPUCTRL(self):
        if self.debug:
            print("not allow to read ppu reg_ctrl")
        return self.cpu.ppu.reg_ctrl
    def read_PPUMASK(self):
        if self.debug:
            print("not allow to read ppu reg_mask")
        return self.cpu.ppu.reg_mask
    def read_PPUSTATUS(self):
        return self.cpu.ppu.read_status()
    def read_OAMADDR(self):
        if self.debug:
            print("not allow to read ppu reg_oamaddr")
        return self.cpu.ppu.reg_oamaddr
    def read_OAMDATA(self):
        return self.cpu.ppu.read_oamdata()
    def read_PPUSCROLL(self):
        if self.debug:
            print("not allow to read ppu reg_scroll")
        return self.cpu.ppu.reg_scroll
    def read_PPUADDR(self):
        if self.debug:
            print("not allow to read ppu reg_vramaddr")
        return self.cpu.ppu.reg_vramaddr
    def read_PPUDATA(self):
        return self.cpu.ppu.read_vramdata()
    def read_OAMDMA(self):
        if self.debug:
            print("not allow to read ppu reg_dma")
        return self.cpu.ppu.reg_dma


    def write(self, addr, data):
        if addr in ppu_rg_map:
            rg_addr = (addr-0x2000)%8
            self.ppu_write_func[rg_addr](data)
        elif addr == 0x4014:
            self.write_OAMDMA(data)
        else:
            memory[addr%65536] = data

    def read(self, addr):
        if addr in ppu_rg_map:
            rg_addr = (addr-0x2000)%8
            return self.ppu_read_func[rg_addr]()
        if addr == 0x4014:
            return self.read_OAMDMA(self)
        return memory[addr%65536]
        

class CPU:
    def __init__(self):
        self.pc = 0b0                 # 16 bit
        self.register_a = 0b0         # 8 bit
        self.sp = 0b11111111          # 8 bit
        self.register_x = 0b0         # 8 bit
        self.register_y = 0b0         # 8 bit
        self.status = 0b00110000      # 8 bit  
        self.bus = BUS(self)
        self.jiffies = 0
        self.cycle_this_ins = 0 # cycle took for current instruction
        self.ppu = PPU()
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


    def nes_init(self):
        self.pc = memory[0xFFFD]<<8|memory[0xFFFC]
        print("pc start at, ", hex(memory[0xFFFD]<<8|memory[0xFFFC]))
        self.sp = 0xFD
        self.status = 0x04
        return 7 #cycles
 #   def fetch():
 #   def decode():
 #   def execute():
    # 2 cpu cycle
    def handle_nmi(self):
        # save pc to stack
        self.pc %= 65536
        tmp = self.pc 
        memory[self.sp+0x100] = (self.pc & 0xff00) >> 8
        self.sp = (self.sp-1)%256

        self.pc-=1
        self.pc %= 65536
        byte1 = memory[self.pc]
        byte2 = memory[self.pc+1]
        addr =  byte2 << 8 | byte1
        self.pc = addr

        memory[self.sp+0x100] = (tmp & 0xff)
        self.sp = (self.sp-1)%256

        #save status to stack
        memory[self.sp+0x100] = self.status
        self.sp = (self.sp-1)%256
        # disable interrupt
        self.status |= 0b000001000
        # jump to nmi handler
        self.pc = memory[0xfffb]<<8|memory[0xfffa]
        #print("nmi jump to ", hex(self.pc))
    # give addressing mode return address

    # addrmode 0: Immediate, 1: Zero Page, 2: Zero PageX, 3: Absolute, 4: AbsoluteX, 5: AbsoluteY, 6: (Inderect,X), 7:(Inderect,)Y 
    # get target address by giving addressing mode and pc+1
    def get_target_addr(self, mode, opc=None):
        #Immediate
        if mode==0:
            return self.pc
        #Zero Page
        elif mode==1:
            return self.bus.read(self.pc)
        #Zero PageX
        elif mode==2:
            return (self.bus.read(self.pc)+self.register_x)%256
        #Absolute
        elif mode==3:
            byte1 = self.bus.read(self.pc%65536)
            byte2 = self.bus.read((self.pc+1)%65536)
            return (byte2<<8) | byte1
        #AbsoluteX
        elif mode==4:
            byte1 = self.bus.read(self.pc%65536)
            byte2 = self.bus.read((self.pc+1)%65536)
            addr = (byte2<<8) | byte1
            if ( opc not in no_extra_absx and (((addr+self.register_x)%65536)&0xff00) != ((addr%65536)&0xff00)):
                self.cycle_this_ins += 1
            return (addr+self.register_x)%65536
            
        #AbsoluteY
        elif mode==5:
            byte1 = self.bus.read(self.pc%65536)
            byte2 = self.bus.read((self.pc+1)%65536)
            addr = (byte2<<8) | byte1
            if ( opc not in no_extra_absy and (((addr+self.register_y)%65536)&0xff00) != ((addr)&0xff00)):
                self.cycle_this_ins += 1
            return (addr+self.register_y)%65536
        #(Inderect,X)
        elif mode==6:
            base = (self.bus.read(self.pc)+self.register_x)%256
            byte1 = self.bus.read(base)
            byte2 = self.bus.read((base+1)%256)
            return (byte2<<8) | byte1
        #(Inderect,)Y 
        elif mode==7:
            base = self.bus.read(self.pc)
            byte1 = self.bus.read(base)
            byte2 = self.bus.read((base+1)%256)
            addr = (byte2<<8) | byte1
            if ( opc not in no_extra_indy and (((addr+self.register_y)%65536)&0xff00) != ((addr)&0xff00)):
                self.cycle_this_ins += 1
            return (addr + self.register_y)%65536
        #ACCUMULATOR
        elif mode==8:
            return 0
        #INDERECT
        elif mode==9:
            byte1 = self.bus.read(self.pc)
            byte2 = self.bus.read(self.pc+1)
            addr1 = (byte2 << 8) | byte1
            addr2 = (byte2 << 8) | ((byte1+1)%256)
            b1 = self.bus.read(addr1)
            b2 = self.bus.read(addr2)
            return (b2 << 8) | b1
        #Zero PageY
        elif mode==10:
            return (self.bus.read(self.pc)+self.register_y)%256
    # return cycle it takes
    def run(self):
        #fetch opcode
        #print(self.pc)
        opcode = memory[self.pc]
        #DEBUG
        #print("==============================================")
        #if opcode not in op_to_asembly:
        #    print("PC=", hex(cpu.pc), "opcode=", hex(opcode), "invalid opcode ")
        #else:   
        #    print("PC=", hex(cpu.pc), "opcode=", hex(opcode), "op=", op_to_asembly[opcode]
        #          ,"V=", (self.ppu.total_cycles//341)%262, " H=", self.ppu.total_cycles%341, "total ppu cyc=", self.ppu.total_cycles)
        
        # do we need extra cycle due to the cross page
        if opcode not in opToTime:
            print(hex(self.pc))
            print("invalid opcode !!!")
            return
        self.cycle_this_ins = opToTime[opcode]
        self.pc += 1
        self.pc %= (65536)
        #decode & execute
        #ADC
        if opcode in [0x69, 0x65, 0x75, 0x6D, 0x7D, 0x79, 0x61, 0x71]:
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            oprand = self.bus.read(target_addr)
            origin = self.register_a
            iscarry = self.status & 0b00000001
            toadd = oprand
            self.register_a = (self.register_a + oprand + iscarry)
            # Handle overflow, and set the flag
            iscarry2 = 0
            if self.register_a >= 256:
                self.register_a %= 256
                self.status |= 0b00000001 # Carry flag
                iscarry2 = 1
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
            if (origin^toadd)&0b10000000:
                self.status = self.status & 0b10111111
            else:
                self.status = self.status & 0b10111111
                if origin&0b10000000:
                    if self.register_a&0b10000000==0:
                        self.status = self.status | 0b01000000
                elif (self.register_a&0b10000000):
                    self.status = self.status | 0b01000000
                
            self.pc += (opToLen[opcode]-1)
            self.pc %= 65536
            #print("ADC")
        #AND
        if opcode in [0x29, 0x25, 0x35, 0x2D, 0x3D, 0x39, 0x21, 0x31]:
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            oprand = self.bus.read(target_addr)
            self.register_a &= oprand
            if self.register_a == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if self.register_a & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            self.pc%=65536
            #print("AND")
        #ASL
        if opcode in [0x0A, 0x06, 0x16, 0x0E, 0x1E]:
            bit7 = 0
            res = 0
            if opcode==0x0A: #Accumulator
                bit7 = self.register_a&0b10000000
                self.register_a <<= 1
                res = self.register_a
                self.register_a &= 0b11111111
            else: #other
                target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
                oprand = self.bus.read(target_addr)
                bit7 = oprand&0b10000000
                oprand <<= 1
                oprand &= 0b11111111
                self.bus.write(target_addr, oprand)
                res = oprand

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
            self.pc %= 65536
            #print("ASL")
        #BIT
        if opcode in [0x24, 0x2C]:
            res = 0
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            oprand = self.bus.read(target_addr)
            tested = oprand
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
            self.pc %= 65536
            #print("BIT")
        #BRANCH default 2 cycle, +1 if branch, +1 if cross page
        if opcode in [0x10, 0x30, 0x50, 0x70, 0x90, 0xB0, 0xD0, 0xF0]:
            #print("op ", hex(opcode), "staus ", hex(self.status), "offset ", hex(memory[self.pc]), hex(memory[self.pc+1]))
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
            self.pc %= 65536
            if offset&0b10000000:
                offset=((offset^0b11111111)+1)%256
                offset=-offset
                #print("hoho", offset)
            if jump:
                self.cycle_this_ins += 1
                if ((((self.pc+offset)%65536)&0xff00) != ((self.pc)&0xff00)):
                    self.cycle_this_ins += 1
                self.pc = (self.pc+offset)%65536
            #print("BRANCH")
        #BRK
        if opcode in [0x00]:
            #MSB of PC+2 to stack
            #LSB of PC+2 to stack
            #status or BRK flag to stack
            # disable interrupt
            #PC = memory[0xffff]<<8+memory[0xfffe]
            
            memory[self.sp+0x100] = (self.pc+1)>>8
            self.sp-=1
            self.sp%=256
            memory[self.sp+0x100] = (self.pc+1)%256
            self.sp-=1
            self.sp%=256
            memory[self.sp+0x100] = self.status|0b00010000
            self.sp-=1
            self.sp%=256
            self.status |= 0b00000100
            self.pc = memory[0xffff]*256 + memory[0xfffe]
            #print("BRK")
        #CMP
        if opcode in [0xC9, 0xC5, 0xD5, 0xCD, 0xDD, 0xD9, 0xC1, 0xD1]:
            #print("cmp", hex(opcode), "a", hex(self.register_a))
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            oprand = self.bus.read(target_addr)
            res = 0
            tosub = ((oprand^0b11111111))%256
            res = self.register_a + tosub + 1
            # Handle overflow, and set the flag
            if res >= 256:
                res %= 256
                self.status |= 0b00000001 # Carry flag
                iscarry2 = 1
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
            self.pc %= 65536
            #print("CMP")
        #CPX
        if opcode in [0xE0, 0xE4, 0xEC]:
            res = 0
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            oprand = self.bus.read(target_addr)
            res = self.register_x - oprand
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
            self.pc %= 65536
            #print("CPX")
        #CPY
        if opcode in [0xC0, 0xC4, 0xCC]:
            res = 0
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            oprand = self.bus.read(target_addr)
            res = self.register_y - oprand
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
            self.pc %= 65536
            #print("CPY")
        #DEC
        if opcode in [0xC6, 0xD6, 0xCE, 0xDE]:
            res = 0
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            oprand = self.bus.read(target_addr)
            oprand -= 1
            res = oprand
            oprand &= 0b11111111
            self.bus.write(target_addr, oprand)
            if res == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if res & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            self.pc %= 65536
            #print("DEC")
        #EOR
        if opcode in [0x49, 0x45, 0x55, 0x4D, 0x5D, 0x59, 0x41, 0x51]:
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            oprand = self.bus.read(target_addr)
            self.register_a ^= oprand
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
            self.pc %= 65536
            #print("EOR")
        #FLAG
        if opcode in [0x18, 0x38, 0x58, 0x78, 0xB8, 0xD8, 0xF8]:
            #print("FLAG")
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
                self.status = self.status & 0b11110111
            elif opcode==0xF8: #SED
                self.status = self.status | 0b00001000

        #INC
        if opcode in [0xE6, 0xF6, 0xEE, 0xFE]:
            res = 0
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            oprand = self.bus.read(target_addr)
            oprand += 1
            res = oprand%256
            oprand &= 0b11111111
            self.bus.write(target_addr, oprand)

            if res == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if res & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            self.pc %= 65536
            #print("INC")
        #JMP
        if opcode in [0x4C, 0x6C]:
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            self.pc = target_addr
            #print("JMP")
        #JSR
        if opcode in [0x20]:
            self.pc+=1
            self.pc %= 65536
            tmp = self.pc 
            memory[self.sp+0x100] = (self.pc & 0xff00) >> 8
            self.sp = (self.sp-1)%256

            self.pc-=1
            self.pc %= 65536
            byte1 = memory[self.pc]
            byte2 = memory[self.pc+1]
            addr =  byte2 << 8 | byte1
            self.pc = addr

            memory[self.sp+0x100] = (tmp & 0xff)
            self.sp = (self.sp-1)%256


            #print("JSR")
        #LDA
        if opcode in [0xA9, 0xA5, 0xB5, 0xAD, 0xBD, 0xB9, 0xA1, 0xB1]:
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            oprand = self.bus.read(target_addr)
            #print(hex(opcode), hex(memory[self.pc]), memory[self.pc])
            self.register_a = oprand
            if self.register_a == 0x0:
                    self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if self.register_a & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            self.pc %= 65536
            #print("LDA")
        #LDX
        if opcode in [0xA2, 0xA6, 0xB6, 0xAE, 0xBE]:
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            oprand = self.bus.read(target_addr)
            self.register_x = oprand
            if self.register_x == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if self.register_x & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            self.pc %= 65536
            #print("LDX")
        #LDY
        if opcode in [0xA0, 0xA4, 0xB4, 0xAC, 0xBC]:
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            oprand = self.bus.read(target_addr)
            self.register_y = oprand
            
            if self.register_y == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if self.register_y & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            self.pc %= 65536
            #print("LDY")
        #LSR
        if opcode in [0x4A, 0x46, 0x56, 0x4E, 0x5E]:
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            oprand = self.bus.read(target_addr)
            bit0 = 0
            res = 0
            if opcode==0x4A: #Accumulator
                bit0 = self.register_a&0b00000001
                self.register_a >>= 1
                res = self.register_a
            else: #Zero Page
                bit0 = oprand&0b00000001
                oprand >>= 1
                self.bus.write(target_addr, oprand)
                res = oprand
            # Handle overflow, and set the flag
            if bit0:
                self.status |= 0b00000001 # Carry flag
            else:
                self.status &= 0b11111110
            if res == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            self.pc %= 65536
            #print("LSR")
        #NOP
        if opcode in [0xEA]:
            pass
            #print("NOP")
        #ORA
        if opcode in [0x09, 0x05, 0x15, 0x0D, 0x1D, 0x19, 0x01, 0x11]:
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            oprand = self.bus.read(target_addr)
            self.register_a |= oprand
            if self.register_a == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if self.register_a & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            self.pc %= 65536
            #print("ORA")
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
            #print("Register Instructions")
        #ROL
        if opcode in [0x2A, 0x26, 0x36, 0x2E, 0x3E]:
            bit7 = 0
            res = 0
            if opcode==0x2A: #Accumulator
                bit7 = self.register_a & 0b10000000
                self.register_a <<= 1
                self.register_a |= (self.status & 0b00000001)
                self.register_a &= 0b11111111
                res = self.register_a
            else: #others
                target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
                oprand = self.bus.read(target_addr)
                bit7 = oprand & 0b10000000
                oprand <<= 1
                oprand |= (self.status & 0b00000001)
                oprand &= 0b11111111
                res = oprand
                self.bus.write(target_addr, oprand)
            if bit7:
                self.status |= 0b00000001
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
            #print("ROL")
            self.pc += (opToLen[opcode]-1)
            self.pc %= 65536
        #ROR
        if opcode in [0x6A, 0x66, 0x76, 0x6E, 0x7E]:
            bit0 = 0
            res = 0
            if opcode==0x6A: #Accumulator
                bit0 = self.register_a & 0b00000001
                self.register_a >>= 1
                self.register_a |= ((self.status & 0b00000001)<<7)
                self.register_a &= 0b11111111
                res = self.register_a
            else: #Others
                target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
                oprand = self.bus.read(target_addr)
                bit0 = oprand & 0b00000001
                oprand >>= 1
                oprand |= ((self.status & 0b00000001)<<7)
                oprand &= 0b11111111
                res = oprand
                self.bus.write(target_addr, oprand)
            if bit0:
                self.status |= 0b00000001
            else:
                self.status &= 0b11111110
            if res == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            #print("ROR")
            if res & 0b10000000:
                self.status = self.status | 0b10000000
            else:
                self.status = self.status & 0b01111111
            self.pc += (opToLen[opcode]-1)
            self.pc %= 65536
        #RTI 記得 status register 的操作，1(bit 5) 保持 1，B 保持原本
        if opcode in [0x40]:
            self.sp += 1
            self.sp%=256
            self.status = 0b00000000
            tmp = self.status&0b00010000
            if tmp:
                self.status = 0b00010000
            self.status |= memory[self.sp+0x100]
            self.status |= 0b00100000
            if not tmp:
                self.status &= 0b11101111
            self.pc = memory[(self.sp+2)%256+0x100]<<8 | memory[(self.sp+1)%256+0x100]
            self.sp += 2
            self.sp%=256
            #print("RTI")
        #RTS
        if opcode in [0x60]:
            self.pc = ((memory[(self.sp+2)%256+0x100]<<8 | memory[(self.sp+1)%256+0x100]) + 1)%65536
            self.sp += 2
            self.sp%=256
            #print("RTS")
        #SBC
        if opcode in [0xE9, 0xE5, 0xF5, 0xED, 0xFD, 0xF9, 0xE1, 0xF1]:
            origin = self.register_a
            iscarry = self.status&0b00000001
            #carry = ((carry)^0b11111111+1)%256
            tosub = 0
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            oprand = self.bus.read(target_addr)
            tosub = ((oprand^0b11111111))%256
            #why this not working
            #ar = ((carry)^0b11111111+1)%256
            self.register_a = (self.register_a + tosub + iscarry)
            # Handle overflow, and set the flag
            iscarry2 = 0
            if self.register_a >= 256:
                self.register_a %= 256
                self.status |= 0b00000001 # Carry flag
                iscarry2 = 1
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
            if (origin^tosub)&0b10000000:
                self.status = self.status & 0b10111111
            else:
                self.status = self.status & 0b10111111
                if origin&0b10000000:
                    if self.register_a&0b10000000==0:
                        self.status = self.status | 0b01000000
                elif (self.register_a&0b10000000):
                    self.status = self.status | 0b01000000
                
            self.pc += (opToLen[opcode]-1)
            self.pc %= 65536
            
        #STA
        if opcode in [0x85, 0x95, 0x8D, 0x9D, 0x99, 0x81, 0x91]:
            #print(hex(opcode))
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            #print(memory[self.pc], self.register_a)
            self.bus.write(target_addr, self.register_a)
            #print("mem", memory[addr + self.register_y],  hex(addr + self.register_y))
            self.pc += (opToLen[opcode]-1)
            self.pc %= 65536
            #print("STA")
        #STACK INSTRUCTION
        # the stack is always on page one ($100-$1FF) and works top down
        if opcode in [0x9A, 0xBA, 0x48, 0x68, 0x08, 0x28]:
            #print("STACK INSTRUCTION")
            res = None
            if opcode==0x9A: #TXS
                self.sp = self.register_x
            elif opcode==0xBA: #TSX
                self.register_x = self.sp
                res = self.register_x
            elif opcode==0x48: #PHA
                memory[self.sp+0x100] = self.register_a
                self.sp-=1
                self.sp%=256
            elif opcode==0x68: #PLA
                self.sp+=1
                self.sp%=256
                self.register_a = memory[self.sp+0x100]
                res = self.register_a
            elif opcode==0x08: #PHP
                memory[self.sp+0x100] = self.status|0b00010000
                self.sp-=1
                self.sp%=256
            elif opcode==0x28: #PLP delayed irq not implemented
                self.sp+=1
                self.sp%=256
                tmp = self.status&0b00110000
                self.status = memory[self.sp+0x100]
                self.status &= 0b11001111
                self.status |= tmp

            # status register
            if res!=None:
                if res == 0:
                    self.status |= 0b00000010
                else:
                    self.status &= 0b11111101
                if res & 0b10000000:
                    self.status = self.status | 0b10000000
                else:
                    self.status = self.status & 0b01111111
            
        #STX
        if opcode in [0x86, 0x96, 0x8E]:
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            self.bus.write(target_addr, self.register_x)
            self.pc += (opToLen[opcode]-1)
            self.pc %= 65536
            #print("STX")
        #STY
        if opcode in [0x84, 0x94, 0x8C]:
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            self.bus.write(target_addr, self.register_y)
            self.pc += (opToLen[opcode]-1)
            self.pc %= 65536
            #print("STY")

        # start of illegal instruction
        #AAC
        if opcode in [0x0B, 0x2B]:
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            oprand = self.bus.read(target_addr)
            self.register_a &= oprand
            if self.register_a == 0x0:
                self.status = self.status | 0b00000010
            else:
                self.status = self.status & 0b11111101
            if self.register_a & 0b10000000:
                self.status = self.status | 0b10000000
                self.status = self.status | 0b00000001
            else:
                self.status = self.status & 0b01111111
                self.status = self.status & 0b11111110
            self.pc += (opToLen[opcode]-1)
            self.pc %= 65536
        
        # todo:
        # AAX - (hart test set 跟 nes wiki 有出入 on status bit N, Z)
        if opcode in [0x87, 0x97, 0x83, 0x8F]:
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            res = self.register_a & self.register_x
            self.bus.write(target_addr, res)
            self.pc += (opToLen[opcode]-1)
            self.pc %= 65536
        # todo not done yet
        # ARR not done yet
        if opcode in [0x6B]:
            target_addr = self.get_target_addr(op_to_mode[opcode], opcode)
            oprand = self.bus.read(target_addr)
            self.register_a &= oprand
            self.register_a >>= 1
            self.register_a |= ((self.status & 0b00000001)<<7)
            if self.status & 0b00000001:
                self.status &= 0xFE
            bit5 = 1 if (self.register_a & 0b00100000) else 0
            bit6 = 1 if (self.register_a & 0b01000000) else 0
            if bit5:
                if bit6:
                    #set C, clear V
                    self.status |= 0x01
                    self.status &= 0b10111111
                else:
                    #set V, clear C
                    self.status |= 0x40
                    self.status &= 0b10111111
            else:
                if bit6:
                    #set C, set V
                    self.status |= 0x01
                    self.status |= 0x40
                else:
                    #clear C, clear V
                    self.status &= 0b11111110
                    self.status &= 0b10111111

            self.pc += (opToLen[opcode]-1)
            self.pc %= 65536
        return self.cycle_this_ins
        #print("new PC=", hex(self.pc), "opcode=", hex(opcode))
        #print('reg.A=', hex(self.register_a))
        #print('reg.X=', hex(self.register_x))
        #print('reg.Y=', hex(self.register_y))
        #print('SP=', hex(self.sp))
        #print('reg.status=', bin(self.status))
        
        #print("stack content:", memory[self.sp+0x100:0x200])
    #end of cpu run
    def reset_reg(self):
        self.pc = 0b0                 # 16 bit
        self.register_a = 0b0         # 8 bit
        self.sp = 0b11111111          # 8 bit
        self.register_x = 0b0         # 8 bit
        self.register_y = 0b0         # 8 bit
        self.status = 0b00110000      # 8 bit  
#def render:

#def io:

def clear_mem():
    for i in range(len(memory)):
        print("asd")
        memory[i] = 0
    return

def load_mapper0():
    with open("rom/test2.nes", 'rb') as f:
        binaryData = f.read()
        #print(binaryData)
        prgrom = list(binaryData)
        for i in range(16384):
            memory[0xC000+i] = prgrom[16+i]
        print(hex(memory[0xFFFC]))
        print(hex(memory[0xFFFD]))

def load_game():
    for i in range(len(gamecode)):
        memory[0x600+i] = gamecode[i]
    return

ADC = ["69", "65", "75", "6D", "7D", "79", "61", "71"]
SBC = ["E9", "E5", "F5", "ED", "FD", "F9", "E1", "F1"]

# snake game for test 6502
if __name__=="__main__":
    argv = sys.argv
    if len(sys.argv)<=1:
        exit()
    if sys.argv[1]=="run":
        #print("implemented:", len(opToLen))
        pg.init()
        screen = pg.display.set_mode((640, 480))
        color = [[255, 255, 255] for i in range(256)]
        color[0] = [0, 0, 0]
        colors = np.array(color)
        toRend = np.array(memory[0x0200:0x0600], dtype = np.int32)
        gridarray = np.reshape(toRend, (32, 32), order='F')
        #print('g ',gridarray[1][0])
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
            #print(memory[0xff])
            memory[0xfe] = random.randint(1, 255)
            #render image
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
            keys = pg.key.get_pressed()
            #print(keys)
            if keys[pg.K_LEFT]:
                memory[0xff] = 0x61
                #print("a")
            elif keys[pg.K_RIGHT]:
                memory[0xff] = 0x64
                #print("d")
            elif keys[pg.K_UP]:
                memory[0xff] = 0x77
                #print("w")
            elif keys[pg.K_DOWN]:
                memory[0xff] = 0x73
                #print("s")
            toRend = np.array(memory[0x0200:0x0600], dtype = np.int32)
            gridarray = np.reshape(toRend, (32, 32), order='F')
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
            #clock.tick(60)
            #inp = input("wait")
            #if inp=='m':
            #    print("mem content:", memory[:0x20])
            #time.sleep(1)
    elif argv[1]=="test":
        testset = implemented
        passed = []
        notpassed = []
        for test in testset:
            with open('6502test/'+test+'.json', 'r') as file:
                js = json.load(file)
                error = []
                i = 0
                for e in js:
                    if test in ADC or test in SBC:  #bypass DECIMAL mode test
                        if e["initial"]["p"] & 0b00001000:
                            continue
                    #print("batch = ", i)
                    i+=1
                    #print(e)
                    #print(e['name'])
                    cpu = CPU()
                    
                    memory = np.zeros(65536*2, dtype=int)
                    cpu.pc = e["initial"]["pc"]
                    cpu.register_a = e["initial"]["a"]
                    cpu.sp = e["initial"]["s"]
                    cpu.register_x = e["initial"]["x"]
                    cpu.register_y = e["initial"]["y"]
                    cpu.status = e["initial"]["p"]
                    for m in e["initial"]["ram"]:
                        memory[m[0]] = m[1]
                    cycle_took = cpu.run()
                    if cpu.pc != e["final"]["pc"] or cpu.sp != e["final"]["s"] or cpu.register_x != e["final"]["x"] or cpu.register_y != e["final"]["y"] or cpu.status != e["final"]["p"]:
                        error.append(e)
                        continue
                    for m in e["final"]["ram"]:
                        if memory[m[0]]!=m[1]:
                            error.append(e)
                            break
                    if not cycle_took == len(e["cycles"]):
                        error.append(e)
                if len(error):
                    print(test, "correct",len(js) - len(error), "wrong", len(error))
                if len(error)==0:
                    passed.append(test)
                else:
                    notpassed.append(test)
                #print(error)
        print("passed: ", passed)
        print("not passed: ", notpassed)            
        print("test")
    elif argv[1]=="testone":
        if len(argv)<3:
            print("no test")
        test = argv[2]
        with open('6502test/'+test+'.json', 'r') as file:
            js = json.load(file)
            error = []
            i = 0
            for e in js:
                if test in ADC or test in SBC:     #bypass DECIMAL mode test
                    if e["initial"]["p"] & 0b00001000:
                        continue    
                print("batch = ", i)
                i+=1
                #print(e)
                #print(e['name'])
                cpu = CPU()
                
                memory = np.zeros(65536*2, dtype=int)
                cpu.pc = e["initial"]["pc"]
                cpu.register_a = e["initial"]["a"]
                cpu.sp = e["initial"]["s"]
                cpu.register_x = e["initial"]["x"]
                cpu.register_y = e["initial"]["y"]
                cpu.status = e["initial"]["p"]
                for m in e["initial"]["ram"]:
                    memory[m[0]] = m[1]
                cycle_took = cpu.run()
                if cpu.pc != e["final"]["pc"] or cpu.sp != e["final"]["s"] or cpu.register_x != e["final"]["x"] or cpu.register_y != e["final"]["y"] or cpu.status != e["final"]["p"]:
                    print('init ', e['initial'])
                    print('answ ', e['final'])
                    resmem = [[ent[0], int(memory[ent[0]])] for ent in e['final']['ram']]
                    print("pc:",cpu.pc,"s:",cpu.sp,"a:",cpu.register_a,"x:",cpu.register_x,"y:",cpu.register_y,"p:",cpu.status, resmem)
                    print("=-------------------------------------------------------------=")
                    error.append(e)
                    continue
                for m in e["final"]["ram"]:
                    if memory[m[0]]!=m[1]:
                        print('init ', e['initial'])
                        print('answ ', e['final'])
                        resmem = [[ent[0], int(memory[ent[0]])] for ent in e['final']['ram']]
                        print("pc:",cpu.pc,"s:",cpu.sp,"a:",cpu.register_a,"x:",cpu.register_x,"y:",cpu.register_y,"p:",cpu.status, resmem)
                        print("=-------------------------------------------------------------=")
                        error.append(e)
                        break
                if not cycle_took == len(e["cycles"]):
                    print('init ', e['initial'])
                    print('answ ', e['final'])
                    print("cycle diff, ans = ", len(e["cycles"]), " but = ", cycle_took)
                    print("=-------------------------------------------------------------=")
                    error.append(e)
            #for err in error:
                #print(err)
            print(test, "correct",len(js) - len(error), "wrong", len(error))
    # test whole emulator
    elif sys.argv[1]=="runppu":
        #print("implemented:", len(opToLen))
        #pg.init()
        #screen = pg.display.set_mode((640, 480))
        #color = [[255, 255, 255] for i in range(256)]
        #color[0] = [0, 0, 0]
        #colors = np.array(color)
        #toRend = np.array(memory[0x0200:0x0600], dtype = np.int32)
        #gridarray = np.reshape(toRend, (32, 32), order='F')
        #print('g ',gridarray[1][0])
        #surface = pg.surfarray.make_surface(colors[gridarray])
        #surface = pg.transform.scale(surface, (400, 400))
        #clock = pg.time.Clock()

        cpu = CPU()
        load_mapper0()
        cpu.ppu.load_mapper0()
        lst_cycles = cpu.nes_init()
        
        running = True
        while running:
            '''
            #render image
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
            keys = pg.key.get_pressed()
            #print(keys)
            if keys[pg.K_LEFT]:
                memory[0xff] = 0x61
                #print("a")
            elif keys[pg.K_RIGHT]:
                memory[0xff] = 0x64
                #print("d")
            elif keys[pg.K_UP]:
                memory[0xff] = 0x77
                #print("w")
            elif keys[pg.K_DOWN]:
                memory[0xff] = 0x73
                #print("s")
            '''
            #print("pc=",hex(cpu.pc))
            if cpu.ppu.is_nmi_triggered:
                #print("handle nmi in cpu")
                cpu.handle_nmi()
                cpu.ppu.is_nmi_triggered = 0
            cpu.ppu.tick(lst_cycles*3)
            lst_cycles = cpu.run()

    print("init cpu")