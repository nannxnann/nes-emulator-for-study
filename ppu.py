import pygame as pg
import numpy as np
import time
#import matplotlib.pyplot as plt
#from matplotlib.animation import FuncAnimation

lst_frame_time = [0]
ppuMemory = [0b00000000] * (65536*2) # 64K 定址
chrom = []
testtbl = []
pg.init()
screen = pg.display.set_mode((640, 480))
color = [[i, i, i] for i in range(256)]
colors = np.array(color)
clock = pg.time.Clock()
# to be implemented
class PPU:
    nparr = np.zeros((256, 256), dtype = np.uint8)
    display = [bytearray([0 for i in range(256)]) for j in range(256)]
    oam = [0 for i in range(256)]
    is_rend = 0
    frame = 0
    cycle = 21
    total_cycles = 21
    scanline = 0 # which line currently ppu render to (262*341)
    is_nmi_triggered = 0
    reg = 0
    reg_internal_vramaddr = 0 # 16bit address
    reg_internal_readbuffer = 0 # only changed after ppudata read
    reg_internal_v = 0  # 
    reg_internal_t = 0  # 
    reg_internal_x = 0  # 
    reg_internal_w = 0  # boolean, vramdata first byte or second
    reg_ctrl = 0     # $2000 write
    reg_mask = 0     # $2001 write
    reg_status = 0   # $2002 read
    reg_oamaddr = 0  # $2003 write
    reg_oamdata = 0  # $2004 read/write
    reg_scroll = 0   # $2005 write
    reg_vramaddr = 0 # $2006 write
    reg_vramdata = 0 # $2007 read/write
    reg_dma = 0      # $4014 write
    frame = 0
    # temporary for render ppu background
    chrom = []
    tbl = {0:0, 1: 90, 2: 180, 3: 255}

    def load_mapper0(self):
        with open("rom/test2.nes", 'rb') as f:
            binaryData = f.read()
            #print(binaryData)
            self.chrom = list(binaryData)
            #load pattern table
            print("ppu load rom size ", len(self.chrom ))
            for i in range(8192):
                ppuMemory[i] = self.chrom [i+16384+16]
            self.chrom  = bytearray(self.chrom [(16384+16):(16384+16+8192)])


    # since there's a dependency "cpu -> ppu" exist, we can't actively notify cpu nmi happened
    def trigger_nmi(self):
        self.is_nmi_triggered = 1
    
    # cpu instead call poll_nmi after every instruction done, to see if nmi happened
    def poll_nmi(self):
        return nmi_triggered==1

    def write_ctrl(self, data):
        #print("write ctrl", hex(data))
        old = self.reg_ctrl
        self.reg_ctrl = (data&0xff)
        # nmi trigger immediatly if vblank of PPUSTATUS = 1
        if self.reg_ctrl&0b10000000 and not (old&0b10000000) and self.reg_status&0b10000000:
            #todo trigger nmi
            #print("nmi triggered by ctrl")
            self.trigger_nmi()

    def write_mask(self, data):
        self.reg_mask = (data&0xff)
    
    def read_status(self):
        self.reg_internal_w = 0
        self.reg_status &= 0x80 # clear v flag
        return self.reg_status
            
    def write_vramaddr(self, data):
        #print("vramaddr w=", self.reg_internal_w,"internal =", self.reg_internal_vramaddr ,"data=", hex(data))
        data &= 0b11111111
        if self.reg_internal_w == 0:
            self.reg_internal_vramaddr &= 0b11111111
            self.reg_internal_vramaddr |= (data << 8)
            self.reg_internal_w = 1
        else:
            self.reg_internal_vramaddr &= 0b1111111100000000
            self.reg_internal_vramaddr |= data
            self.reg_internal_w = 0

    def write_oamaddr(self, data):
        self.reg_oamaddr = data & 0b11111111
    def write_oamdata(self, data):
        self.reg_oamdata = data & 0b11111111
        self.oam[self.reg_oamaddr] = self.reg_oamdata
    def write_oamdma(self, data):
        for i in range(256):
            self.oam[i] = data[i]
    def read_oamdata(self):
        return self.oam[self.reg_oamaddr]
    def read_vramdata(self):
        #print("read_vramdata", hex(write_addr), hex(data))
        read_addr = self.reg_internal_vramaddr
        addr_inc = True if (self.reg_ctrl&0b00000100) else False
        if addr_inc:
            self.reg_internal_vramaddr+=32
        else:
            self.reg_internal_vramaddr+=1
        self.reg_internal_vramaddr &= 0x3fff
        if read_addr < 0x3000:
            ret = self.reg_internal_readbuffer
            self.reg_internal_readbuffer = ppuMemory[read_addr]
        elif read_addr < 0x3eff:
            print("invlid, why?")
        elif read_addr < 0x3eff:
            print("pallete")
            ret = ppuMemory[read_addr]
        else:
            pass
            #print("unexpected memory access")
        return ret
    def write_vramdata(self, data):
        write_addr = self.reg_internal_vramaddr
        #print("write_vramdata", hex(write_addr), hex(data))
        if write_addr < 0x3000:
            ppuMemory[write_addr] = data&0b11111111
        elif write_addr < 0x3eff:
            print("invlid, why?")
        elif write_addr < 0x3eff:
            print("write pallete")
            ppuMemory[write_addr] = data&0b11111111
        else:
            pass
            #print("unexpected memory access")
        addr_inc = True if (self.reg_ctrl&0b00000100) else False
        if addr_inc:
            self.reg_internal_vramaddr+=32
        else:
            self.reg_internal_vramaddr+=1
        return
    def render(self):
        #pygame init
        if self.frame%60==0:
            cur_frame_time = time.perf_counter()
            frame_dur = cur_frame_time - lst_frame_time[0]
            lst_frame_time[0] = cur_frame_time
            print(f" 60 frame took: {frame_dur:.6f} sec")
        #toRend = np.array(memory[0x0200:0x0600], dtype = np.int32)
        #gridarray = np.reshape(toRend, (32, 32), order='F')
        #print('g ',gridarray[1][0])
        #surface = pg.surfarray.make_surface(colors[gridarray])
        #surface = pg.transform.scale(surface, (400, 400))
        
        # get status info
        nametbl_idx = self.reg_ctrl & 0b11
        bg_pattern_tbl = 0x1000 if (self.reg_ctrl & 0x10) else 0x0000
        sprite_pattern_tbl = 0x1000 if (self.reg_ctrl & 0x08) else 0x0000
        sprite_size = self.reg_ctrl & 0x20 # 0 for 8*8, 1 for 8*16

        # ppu render nametbl
        
        # start render 32 * 30 tiles
        for i in range(960): # total 960 tiles in one frame, took 960 byte in name table
                               # each tile is one 8x8 pixels graph
            r = i%32
            c = i//32
            idx = 0x2000+(0x400*nametbl_idx)+i
            #print("idx", hex(idx))
            pat = ppuMemory[idx]%256
            #print("pat", pat)
            #print(self.chrom)
            #print(pat)
            for x in range(64): # display a tile, pixel 0's bit0 = 0 bit in the 16 bytes, bit1 = 64 bit in the 16 bytes
                bit0 = 1 if (self.chrom [pat*16+x//8+bg_pattern_tbl] & (1 << (7-x%8))) else 0
                bit1 = 1 if (self.chrom [pat*16+8+x//8+bg_pattern_tbl] & (1 << (7-x%8))) else 0
                self.display[r*8+x%8][c*8+x//8] = self.tbl[bit1*2+bit0] # show in np image
        
        # render oam, not consider 16 bit sprite yet.
        sprite_pattern_idx = 0x1000 if self.reg_ctrl & 0b1000 else 0x0000
        for i in range(64):
            # y position
            byte0 = self.oam[(i*4)]
            # tile/index
            byte1 = self.oam[(i*4)+1]
            # attributes
            byte2 = self.oam[(i*4)+2]
            # x position
            byte3 = self.oam[(i*4)+3]
            for x in range(64): # display a tile, pixel 0's bit0 = 0 bit in the 16 bytes, bit1 = 64 bit in the 16 bytes
                bit0 = 1 if (self.chrom[byte1*16+x//8+sprite_pattern_idx] & (1 << (7-x%8))) else 0
                bit1 = 1 if (self.chrom[byte1*16+8+x//8+sprite_pattern_idx] & (1 << (7-x%8))) else 0
                if byte3+x%8 >= 256 or byte0+x//8 >= 256:
                    continue
                if byte3+x%8 <0 or byte0+x//8 < 0:
                    continue
                self.display[byte3+x%8][byte0+x//8] = self.tbl[bit1*2+bit0] # show in np image


        surface = pg.surfarray.make_surface(colors[self.display])
        surface = pg.transform.scale(surface, (400, 400))
        screen.blit(surface, (0, 0))
        pg.display.flip()
        

    def tick(self, cycle):
        # 262 * 341
        self.total_cycles += cycle
        self.cycle += cycle
        if self.cycle >= 341:
            self.cycle %= 341
            self.scanline += 1
        if self.scanline >= 262:  
            self.scanline %= 262
            self.frame+=1
            #print("frame= ", self.frame)
            # reset vblank flag
            self.reg_status &= 0b01111111
        
        # nmi is triggered at line 241 (idx from 0)
        # scanline 241, dot 1
        if self.scanline == 242 and self.is_rend==0:
            #print(self.frame, self.cycle, self.scanline)
            if self.reg_ctrl&0b10000000:
                self.trigger_nmi()
            self.reg_status |= 0b10000000
            # todo render image while every line of current frame have been scan over
            self.is_rend=1
            if self.frame>=0:
                self.render()
                #print("===========================================================================")
        if self.scanline > 242 and self.is_rend==1:
            self.is_rend=0
        
        
        
# 先嘗試把 ROM 內的 pattern 打印出來
if __name__=="__main__":
    # load cartridge (之後得獨立出來，這裡是為了演是方便先 load ppu 內容 CHROM)
    with open("rom/test2.nes", 'rb') as f:
        binaryData = f.read()
        #print(binaryData)
        chrom = list(binaryData)
        chrom = chrom[(16384+16):(16384+16+8192)]
    #print(''.join('{:02x} '.format(x) for x in chrom[:8]))
    tbl = {0:0, 1: 90, 2: 180, 3: 255}
    #fig, ax = plt.subplots()
    # Initialize an image plot with a dummy array
    
    #def update(frame):
        # Generate or modify your array here for each frame
        # Example: a random array that changes each second
    #    new_array = np.random.rand(10, 10)
    #    im.set_data(new_array)
    #    return [im]
    #ani = FuncAnimation(fig, update, frames=range(100), interval=1000, blit=True)

    # chrrom [0x0 .. 0x2000] 8K
    # each tile is a 8*8 pixel image
    # each pixel is represent in chrrom with 2 bits
    # a tile is 8*8*2 = 128 bits = 16 bytes
    # let's render them
    nparr = np.zeros((32*8, 16*8))
    for x in range(32*16): # total 16*32 tiles
        r = x//16
        c = x%16
        for i in range(64): # display a tile, pixel 0's bit0 = 0 bit in the 16 bytes, bit1 = 64 bit in the 16 bytes
            bit0 = 1 if (chrom[x*16+i//8] & (1 << (7-i%8))) else 0
            bit1 = 1 if (chrom[x*16+8+i//8] & (1 << (7-i%8))) else 0
            #print(x, bit1<<1+bit0, bit1, bit0)
            nparr[r*8+i//8][c*8+i%8] = tbl[bit1*2+bit0] # show in np image
            #print(r*8+i//8, c*8+i%8)
    #im = ax.imshow(nparr, cmap='gray')
    #plt.show()