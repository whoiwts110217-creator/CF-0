"""Independent small LR35902-instruction model for focused ROM smoke tests.
Not a complete or cycle-accurate Game Boy emulator. Tests original ROM opcodes,
map transitions, and battery SRAM flag serialization; no graphics timing proof.
"""
from __future__ import annotations
import runpy
import sys
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parent
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
s=runpy.run_path(str(ROOT/'build_v02.py'))
ROM=(ROOT/'dreamkiller_road_v0_2.gb').read_bytes()
LABEL=s['c'].labels

class CPU:
 def __init__(self,actions=None,external_ram=None):
  self.mem=bytearray(65536);self.mem[:32768]=ROM
  self.mem[0xA000:0xC000]=external_ram or bytes(8192)
  self.pc=0x150;self.sp=0xfffe
  self.a=self.b=self.c=self.d=self.e=self.h=self.l=self.f=0
  self.joysel=0x30;self.joykey=None;self.actions=list(actions or [])
  self.scans=0;self.instructions=0;self.ramenabled=False
 def hl(self):return (self.h<<8)|self.l
 def sethl(self,val):self.h=(val>>8)&255;self.l=val&255
 def bc(self):return (self.b<<8)|self.c
 def setbc(self,x):self.b=(x>>8)&255;self.c=x&255
 def de(self):return (self.d<<8)|self.e
 def setde(self,x):self.d=(x>>8)&255;self.e=x&255
 def rd(self,addr):
  addr&=65535
  if addr==0xff44:return 144  # tests read VRAM-access sequencing abstractly
  if addr==0xff00:
   low=0xf
   if self.joykey:
    key=self.joykey
    if self.joysel==0x20 and key in ('right','left','up','down'):
     low &= ~(1<<{'right':0,'left':1,'up':2,'down':3}[key])
    if self.joysel==0x10 and key in ('a','b'):
     low &= ~(1<<{'a':0,'b':1}[key])
   return low|0xc0|self.joysel
  if 0xa000<=addr<0xc000 and not self.ramenabled:return 0xff
  return self.mem[addr]
 def wr(self,addr,value):
  addr&=65535;value&=255
  if addr<0x2000:self.ramenabled=(value&0xf)==0xa;return
  if addr<0x8000:return
  if 0xa000<=addr<0xc000 and not self.ramenabled:return
  if addr==0xff00:self.joysel=value&0x30;return
  self.mem[addr]=value
 def u8(self):v=self.rd(self.pc);self.pc=(self.pc+1)&65535;return v
 def u16(self):lo=self.u8();hi=self.u8();return lo|(hi<<8)
 def push(self,x):self.sp=(self.sp-1)&65535;self.wr(self.sp,(x>>8)&255);self.sp=(self.sp-1)&65535;self.wr(self.sp,x&255)
 def pop(self):lo=self.rd(self.sp);self.sp=(self.sp+1)&65535;hi=self.rd(self.sp);self.sp=(self.sp+1)&65535;return lo|(hi<<8)
 def zz(self,yes):self.f=(0x80 if yes else 0)|(self.f&0x10)
 def zc(self,val,carry=False):self.f=(0x80 if (val&255)==0 else 0)|(0x10 if carry else 0)
 def cond(self,op):
  z=bool(self.f&0x80);carry=bool(self.f&0x10)
  return {0xC2:not z,0xCA:z,0xD2:not carry,0xDA:carry,0x20:not z,0x28:z,0x38:carry}.get(op,True)
 def scan(self):
  self.scans+=1
  if self.scans%2==1:
   self.joykey=self.actions.pop(0) if self.actions else None
  else:self.joykey=None
 def step(self):
  self.instructions+=1
  if self.instructions>20_000_000:raise RuntimeError('too many CPU instructions; stuck at %04x'%self.pc)
  if self.pc==LABEL['scan_key']:self.scan()
  op=self.u8()
  if op in (0x00,0xF3):pass
  elif op==0x31:self.sp=self.u16()
  elif op==0x01:self.setbc(self.u16())
  elif op==0x06:self.b=self.u8()
  elif op==0x0E:self.c=self.u8()
  elif op==0x05:self.b=(self.b-1)&255;self.zz(self.b==0)
  elif op==0x0D:self.c=(self.c-1)&255;self.zz(self.c==0)
  elif op==0x11:self.setde(self.u16())
  elif op==0x21:self.sethl(self.u16())
  elif op==0x3E:self.a=self.u8()
  elif op==0x26:self.h=self.u8()
  elif op==0x16:self.d=self.u8()
  elif op==0xEA:self.wr(self.u16(),self.a)
  elif op==0xFA:self.a=self.rd(self.u16())
  elif op==0xE0:self.wr(0xff00+self.u8(),self.a)
  elif op==0xF0:self.a=self.rd(0xff00+self.u8())
  elif op==0xAF:self.a=0;self.f=0x80
  elif op==0x2A:self.a=self.rd(self.hl());self.sethl(self.hl()+1)
  elif op==0x12:self.wr(self.de(),self.a)
  elif op==0x13:self.setde(self.de()+1)
  elif op==0x0B:self.setbc(self.bc()-1)
  elif op==0x78:self.a=self.b
  elif op==0x79:self.a=self.c
  elif op==0x7A:self.a=self.d
  elif op==0x7B:self.a=self.e
  elif op==0x87:
   x=self.a+self.a;self.a=x&255;self.zc(self.a,x>255)
  elif op==0xB8:self.zc((self.a-self.b)&255,self.a<self.b)
  elif op==0x90:
   x=self.a-self.b;self.a=x&255;self.zc(self.a,x<0)
  elif op==0x91:
   x=self.a-self.c;self.a=x&255;self.zc(self.a,x<0)
  elif op==0xC6:
   x=self.a+self.u8();self.a=x&255;self.zc(self.a,x>255)
  elif op==0x14:self.d=(self.d+1)&255;self.zz(self.d==0)
  elif op==0x93:
   out=self.a-self.e;self.a=out&255;self.zc(self.a,out<0)
  elif op==0xB1:self.a|=self.c;self.zc(self.a)
  elif op==0xB7:self.zc(self.a)
  elif op==0xBA:self.zc((self.a-self.d)&255,self.a<self.d)
  elif op==0xFE:
   arg=self.u8();self.zc((self.a-arg)&255,self.a<arg)
  elif op==0xE6:self.a&=self.u8();self.zc(self.a)
  elif op==0xF6:self.a|=self.u8();self.zc(self.a)
  elif op==0xEE:self.a^=self.u8();self.zc(self.a)
  elif op==0xA9:self.a^=self.c;self.zc(self.a)
  elif op==0xA7:self.zc(self.a)
  elif op==0x2F:self.a^=255
  elif op==0x3C:self.a=(self.a+1)&255;self.zz(self.a==0)
  elif op==0x3D:self.a=(self.a-1)&255;self.zz(self.a==0)
  elif op==0x47:self.b=self.a
  elif op==0x4F:self.c=self.a
  elif op==0x57:self.d=self.a
  elif op==0x5F:self.e=self.a
  elif op==0x6F:self.l=self.a
  elif op==0x7E:self.a=self.rd(self.hl())
  elif op==0x1A:self.a=self.rd(self.de())
  elif op==0x77:self.wr(self.hl(),self.a)
  elif op==0x22:self.wr(self.hl(),self.a);self.sethl(self.hl()+1)
  elif op==0x23:self.sethl(self.hl()+1)
  elif op==0x36:self.wr(self.hl(),self.u8())
  elif op==0x29:
   x=self.hl()*2;self.sethl(x);self.f=(self.f&0x80)|(0x10 if x>65535 else 0)
  elif op==0x19:
   x=self.hl()+self.de();self.sethl(x);self.f=(self.f&0x80)|(0x10 if x>65535 else 0)
  elif op==0xCB:
   arg=self.u8()
   if arg==0x7F:self.f=(0x80 if not(self.a&0x80) else 0)|(self.f&0x10)
   else:raise RuntimeError('Unhandled CB opcode '+hex(arg))
  elif op==0xC8:
   if self.f&0x80:self.pc=self.pop()
  elif op==0x37:self.f=(self.f&0x80)|0x10
  elif op==0xE5:self.push(self.hl())
  elif op==0xE1:self.sethl(self.pop())
  elif op==0xF5:self.push((self.a<<8)|self.f)
  elif op==0xF1:
   x=self.pop();self.a=x>>8;self.f=x&0xf0
  elif op==0xD6:
   arg=self.u8();delta=self.a-arg;self.a=delta&255;self.zc(self.a,delta<0)
  elif op in (0x18,0x20,0x28,0x38):
   off=self.u8();off=off-256 if off&128 else off
   if self.cond(op):self.pc=(self.pc+off)&65535
  elif op in (0xC3,0xC2,0xCA,0xD2,0xDA):
   addr=self.u16()
   if self.cond(op):self.pc=addr
  elif op==0xCD:
   addr=self.u16();self.push(self.pc);self.pc=addr
  elif op==0xC9:self.pc=self.pop()
  else:raise RuntimeError(f'Unsupported opcode {op:#x} at {self.pc-1:04x}')
 def run_until(self,condition,max_ops=1_000_000):
  for _ in range(max_ops):
   if condition(self):return
   self.step()
  raise AssertionError('condition not reached, pc=%04x scene=%s flags=%s scan=%s'%(self.pc,self.mem[0xc000],self.mem[0xc003],self.scans))
 def saved_ram(self):return bytes(self.mem[0xA000:0xC000])
