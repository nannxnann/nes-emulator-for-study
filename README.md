# nes-emulator-for-study
nes emulator for study purpose
# REF
https://www.nesdev.org/obelisk-6502-guide/reference.html
http://www.6502.org/tutorials/6502opcodes.html
https://bugzmanov.github.io/nes_ebook/chapter_3.html
https://www.cnblogs.com/chzarles/articles/15816145.html

to verify snake game:
PC 696 CMP <= Carry flag


NOTE:
status 更新待驗證
數值計算應該採用 2's complement
harte test set for documented opcode implemented done


todo:
還得再深入了解 ADC SBC 實作，雖然現在被我矇對了
架構肯定得改寫，提高附用率，重複造太多輪子了
extra cpu cycle 判斷 - cross page
cpu memory mapping
harte test set test cpu cycle
undocumented opcode implemented
run ppu first than cpu, since the register value of ppu is update after the cpu cycle

run:
python .\cpu.py test
python .\cpu.py testone CC
python .\ppu.py # show tile map

cycle error:
'10', '30', '50', '70', '90', 'B0', 'D0', 'F0',
why no extra on this op 
no_extra_absx = [0x1E, 0xFE, 0xDE, 0x5E, 0x3E, 0x7E, 0x9D]
no_extra_absy = [0x99]
no_extra_indy = [0x91]