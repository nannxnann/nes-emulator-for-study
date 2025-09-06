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

snake game 目前一路走到 PC 0x641 都正確

todo:
Harte test set
snake game 0x641 0x719
還得再深入了解 ADC SBC 實作，雖然現在被我矇對了
架構肯定得改寫，提高附用率，重複造太多輪子了

run:
python .\cpu.py test
python .\cpu.py testone CC