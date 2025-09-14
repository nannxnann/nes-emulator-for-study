import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

ppuMemory = [0b00000000] * (65536*2) # 64K 定址
chrom = []

# to be implemented
class PPU:
    reg = 0
    reg_internal_vramaddr # 16bit address
    reg_internal_readbuffer # only changed after ppudata read
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
    def write_vramaddr(self, data):
        data &= 0b11111111
        if reg_internal_w == 0:
            reg_internal_vramaddr &= 0b11111111
            reg_internal_vramaddr |= (data << 8)
        else:
            reg_internal_vramaddr &= 0b1111111100000000
            reg_internal_vramaddr |= data
            
    def read_vramdata(self):
        read_addr = self.reg_internal_vramaddr
        addr_inc = True if (self.reg_ctrl&0b00000100) else False
        if addr_inc:
            self.reg_internal_vramaddr+=32
        else:
            self.reg_internal_vramaddr+=1
        self.reg_internal_vramaddr &= 0x3fff
        if read_addr < 0x3000:
            ret = reg_internal_readbuffer
            reg_internal_readbuffer = ppuMemory[read_addr]
        elif read_addr < 0x3eff:
            print("invlid, why?")
        elif read_addr < 0x3eff:
            print("pallete")
            ret = ppuMemory[read_addr]
        else:
            print("unexpected memory access")
        return ret
    def write_vramdata(self, data):
        data &= 0b11111111
        if reg_internal_w == 0:
            reg_internal_vramaddr &= 0b11111111
            reg_internal_vramaddr |= (data << 8)
        else:
            reg_internal_vramaddr &= 0b1111111100000000
            reg_internal_vramaddr |= data
#todo: 目前完成 render chrom (但好像有bug need fix)
# 先嘗試把 ROM 內的 pattern 打印出來
if __name__=="__main__":
    # load cartridge (之後得獨立出來，這裡是為了演是方便先 load ppu 內容 CHROM)
    with open("rom/test1.nes", 'rb') as f:
        binaryData = f.read()
        #print(binaryData)
        chrom = list(binaryData)
        chrom = chrom[(16384+16+1):(16384+16+8096+1)]
    print(''.join('{:02x} '.format(x) for x in chrom[:8]))
    tbl = {0:0, 1: 90, 2: 180, 3: 255}
    fig, ax = plt.subplots()
    # Initialize an image plot with a dummy array
    
    #def update(frame):
        # Generate or modify your array here for each frame
        # Example: a random array that changes each second
    #    new_array = np.random.rand(10, 10)
    #    im.set_data(new_array)
    #    return [im]
    #ani = FuncAnimation(fig, update, frames=range(100), interval=1000, blit=True)
    nparr = np.zeros((32*8, 16*8))
    for x in range(16*32):
        r = x//16
        c = x%16
        for i in range(64):
            bit0 = 1 if (chrom[x*2+i//8] & 1 << (i%8)) else 0
            bit1 = 1 if (chrom[x*2+1+i//8] & 1 << (i%8)) else 0
            #print(x, bit1<<1+bit0, bit1, bit0)
            nparr[r*8+i//8][c*8+i%8] = tbl[bit1*2+bit0]
    im = ax.imshow(nparr, cmap='gray')
    plt.show()