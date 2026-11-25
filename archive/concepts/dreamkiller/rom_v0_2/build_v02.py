#!/usr/bin/env python3
"""Dreamkiller: The Road Remembers v0.2 - original LR35902 Game Boy cartridge.

The art is pixel-authored in art.py (44 8x8 tiles). No generated game assets.
The code is assembled by the tiny embedded offline assembler for reproducibility.
This is a compact gameplay slice, not a completed full RPG.
"""
from pathlib import Path
import hashlib
from pixel_font import tiles as font_tiles
from art import art_bytes, MAP_TILES, COLLISION, TILE_BY_NAME
OUT=Path(__file__).resolve().parent
ROM=bytearray([0]*32768)
NINTENDO_LOGO=bytes.fromhex('ce ed 66 66 cc 0d 00 0b 03 73 00 83 00 0c 00 0d 00 08 11 1f 88 89 00 0e dc cc 6e e6 dd dd d9 99 bb bb 67 63 6e 0e ec cc dd dc 99 9f bb b9 33 3e')
ROM[0x104:0x134]=NINTENDO_LOGO
ROM[0x100:0x104]=bytes([0x00,0xc3,0x50,0x01])
ROM[0x134:0x144]=b'DREAMKILLER'.ljust(16,b'\0')
ROM[0x143]=0x00 # DMG-compatible for Safari Gambatte rendering
ROM[0x144:0x146]=b'00';ROM[0x146]=0;ROM[0x147]=3;ROM[0x148]=0;ROM[0x149]=2;ROM[0x14A]=1;ROM[0x14B]=0x33;ROM[0x14C]=0

class Code:
 def __init__(self):self.pc=0x150;self.labels={};self.fixups=[];self.trace=[]
 def em(self,*bs):
  for b in bs:
   if b<0 or b>255:raise ValueError(f'invalid byte {b} at {self.pc:#04x}')
   if self.pc>=0x5000:raise ValueError(f'program too large {self.pc:x}')
   ROM[self.pc]=b;self.pc+=1
 def at(self,name):
  if name in self.labels:raise ValueError('duplicate label '+name)
  self.labels[name]=self.pc
 def ptr(self,name,op):self.em(op);self.fixups.append((self.pc,name,'abs'));self.em(0,0)
 def call(self,name):self.ptr(name,0xcd)
 def jp(self,name,cond=0xc3):self.ptr(name,cond)
 def jr(self,name,cond=0x18):self.em(cond);self.fixups.append((self.pc,name,'rel'));self.em(0)
 def ld_a(self,n):self.em(0x3e,n)
 def ld_b(self,n):self.em(0x06,n)
 def ld_c(self,n):self.em(0x0e,n)
 def ld_hl(self,n):self.em(0x21,n&255,(n>>8)&255)
 def ld_de(self,n):self.em(0x11,n&255,(n>>8)&255)
 def ld_bc(self,n):self.em(0x01,n&255,(n>>8)&255)
 def ld_hl_label(self,name):self.ptr(name,0x21)
 def ld_de_label(self,name):self.ptr(name,0x11)
 def ld_mem(self,n):self.em(0xea,n&255,n>>8)
 def ld_a_mem(self,n):self.em(0xfa,n&255,n>>8)
 def ldh_get(self,n):self.em(0xf0,n)
 def ldh_put(self,n):self.em(0xe0,n)
 def print_at(self,y,x,txt):
  self.ld_hl(0x9800+y*32+x);self.ld_de_label(txt);self.call('puts')
 def tile(self,x,y,tile):
  self.ld_hl(0x9800+y*32+x)
  self.em(0x36,tile)
 def done(self):
  for pos,name,mode in self.fixups:
   if name not in self.labels:raise ValueError('undefined: '+name)
   dst=self.labels[name]
   if mode=='abs':ROM[pos:pos+2]=dst.to_bytes(2,'little')
   else:
    rel=dst-(pos+1)
    if not -128<=rel<=127:raise ValueError(f'JR out of range: {name}, delta {rel} from {pos:#x}')
    ROM[pos]=rel&255

c=Code()
SC=0xC000;PX=0xC001;PY=0xC002;FLAGS=0xC003;SEQ=0xC004;SLOT=0xC005
HP=0xC006;EHP=0xC007;EX=0xC008;EY=0xC009;MSG=0xC00A;TICK=0xC00B;ROW=0xC00C;TX=0xC00D;TY=0xC00E;PENDING=0xC00F;JOURNAL=0xC010
MAXHP=8
# Status messages: two lines, uppercase <=20 chars for Game Boy text tiles
MESSAGES=[
 ('A LOOK   B JOURNAL','WALK THE OLD ROAD'),
 ('THIS WAS HERE BEFORE','ANYONE NAMED IT.'),
 ('THE FRUIT IS GONE.','ONE FRUIT. ONE HAND.'),
 ('SAME INK. SAME WOOD.','SOMETHING IS WRONG.'),
 ('CHALK ON OLD TIMBER','THE MARK REMAINS.'),
 ('PIP: MY BROTHER IS','LOST IN THE CAVE'),
 ('PIP: WILL YOU HELP?','A YES       B NO'),
 ('PIP: I WILL WAIT.','BRING BACK THE TRUTH'),
 ('PIP: I UNDERSTAND.','I WILL ASK THE GUILD'),
 ('A BLACK MOUTH OPENS','IN THE OLD ROAD.'),
 ('THE SHADE IS CLOSE.','A TO STRIKE NEAR IT'),
 ('YOU STRIKE THE SHADE','IT DOES NOT BLEED.'),
 ('DUST WHERE IT STOOD','THE GATE UNLATCHES.'),
 ('A RUSTED LATCH','SOMETHING HOLDS IT.'),
 ('TWO FIGURES WAIT','BEHIND THE ARCHIVE.'),
 ('ONE CAIRN MAY EXIT.','WHY ARE THERE TWO?'),
 ('THE ROAD REMEMBERS.','SO DOES THE CHALK.'),
 ('THE ROCK IS TOO HIGH','FIND ANOTHER WAY.'),
 ('YOU WERE RESCUED.','THE CAVE REMEMBERS.'),
 ('NOT HOW IT STARTED','JUST HOW YOU BEGAN.'),
 ('THE SIGN IS STILL','RIGHT WHERE IT WAS.'),
 ('NOTHING LEFT TO PICK','THE FRUIT IS TAKEN.'),
 ('NO ONE ANSWERS.','ONLY THE DRY WIND.'),
 ('KNUCKLE: FRESH BREAD','BUT NOT FOR FREE.'),
 ('THE ROOTS HOLD TIGHT','A NEW PATH IS NEAR.'),
 ('SOMEONE LEFT A MARK','BUT WHO MADE IT?'),
 ('THE ARCHIVE WHISPERS','NO RECORD OF YOU'),
 ('YOU HAVE SEEN IT.','YOU CANNOT UNSEE IT.'),
 ('A SMALL TOWN STILL','GOES ON WITHOUT YOU.'),
 ('THE GATE IS OPEN.','BEYOND IS A RECORD.'),
 ('THE ROAD ENDS HERE.','FOR NOW.'),
 ('THE SHADE STRIKES','YOUR BREATH IS COLD.'),
 ('B001: ROAD REPEATED','THE ATLAS IS WRONG.'),
]
for i,(a,b) in enumerate(MESSAGES):
 assert len(a)<=20 and len(b)<=20,(i,a,b)
 assert all(32<=ord(v)<=95 for v in a+b),(i,a,b)

# Boot and VRAM initialize
c.at('entry');c.em(0xF3,0x31,0xFE,0xDF)
c.call('safe_lcd_off')
c.ld_hl(0x5000);c.ld_de(0x8000);c.ld_bc(1024+len(art_bytes()))
c.at('copy_tiles');c.em(0x2A,0x12,0x13,0x0B,0x78,0xB1);c.jp('copy_tiles',0xC2)
c.call('clear_map')
c.ld_a(0xE4);c.ldh_put(0x47);c.ldh_put(0x48) # OBP0 sprite palette
c.ld_a(0x97);c.ldh_put(0x40) # OBJ enabled, 8x16 size, BG enabled
# init work RAM
c.em(0xAF)
for addr in [SC,FLAGS,SEQ,TICK,PENDING,JOURNAL,MSG]:c.ld_mem(addr)
c.ld_a(9);c.ld_mem(PX);c.ld_a(10);c.ld_mem(PY)
c.ld_a(MAXHP);c.ld_mem(HP)
c.ld_a(3);c.ld_mem(EHP)
c.ld_a(14);c.ld_mem(EX);c.ld_a(9);c.ld_mem(EY)
c.ld_a(0xFF);c.ld_mem(SLOT)
c.ld_a(0x0A);c.ld_mem(0x0000)
# load old compatible dual-slot commit format: flags only.
c.ld_hl(0xA000);c.call('read_slot');c.jp('load_slot1',0xDA)
c.em(0x78);c.ld_mem(SEQ);c.em(0x79);c.ld_mem(FLAGS);c.em(0xAF);c.ld_mem(SLOT)
c.at('load_slot1');c.ld_hl(0xA010);c.call('read_slot');c.jp('loaded',0xDA)
c.ld_a_mem(SLOT);c.em(0xFE,0xFF);c.jp('take_slot1',0xCA)
c.em(0x78,0x57);c.ld_a_mem(SEQ);c.em(0x5F,0x7A,0x93);c.jp('loaded',0xCA)
c.em(0xFE,0x80);c.jp('loaded',0xD2)
c.at('take_slot1');c.em(0x78);c.ld_mem(SEQ);c.em(0x79);c.ld_mem(FLAGS);c.ld_a(1);c.ld_mem(SLOT)
c.at('loaded')
c.ld_a_mem(FLAGS);c.em(0xE6,0x10);c.jp('shade_not_defeated',0xCA)
c.em(0xAF);c.ld_mem(EHP)
c.at('shade_not_defeated');c.ld_a(19);c.ld_mem(MSG)
c.call('intro_fall')
c.at('main');c.call('wait_key');c.em(0xF5);c.call('wait_release');c.em(0xF1)
for val,label in [(1,'right'),(2,'left'),(3,'up'),(4,'down'),(5,'action'),(6,'journal')]:
 c.em(0xFE,val);c.jp(label,0xCA)
c.jp('main')
# Movement keys; temp target coordinates; centralized collision.
c.at('right');c.ld_a_mem(PX);c.em(0xFE,18);c.jp('right_boundary',0xD2);c.em(0x3C);c.ld_mem(TX);c.ld_a_mem(PY);c.ld_mem(TY);c.jp('try_move')
c.at('left');c.ld_a_mem(PX);c.em(0xFE,1);c.jp('left_boundary',0xCA);c.em(0x3D);c.ld_mem(TX);c.ld_a_mem(PY);c.ld_mem(TY);c.jp('try_move')
c.at('up');c.ld_a_mem(PY);c.em(0xFE,1);c.jp('main',0xCA);c.em(0x3D);c.ld_mem(TY);c.ld_a_mem(PX);c.ld_mem(TX);c.jp('try_move')
c.at('down');c.ld_a_mem(PY);c.em(0xFE,13);c.jp('main',0xD2);c.em(0x3C);c.ld_mem(TY);c.ld_a_mem(PX);c.ld_mem(TX);c.jp('try_move')

# Right/left edge transitions. These have fixed, guaranteed routes.
c.at('right_boundary');c.ld_a_mem(PY);c.em(0xFE,9);c.jp('blocked',0xDA);c.em(0xFE,12);c.jp('blocked',0xD2)
c.ld_a_mem(SC)
for num,label in [(0,'go_s01'),(1,'go_e01'),(2,'go_s02')]:c.em(0xFE,num);c.jp(label,0xCA)
c.jp('main')
c.at('left_boundary');c.ld_a_mem(PY);c.em(0xFE,9);c.jp('blocked',0xDA);c.em(0xFE,12);c.jp('blocked',0xD2)
c.ld_a_mem(SC)
for num,label in [(1,'go_s00'),(2,'go_s01_back'),(3,'go_e01_back')]:c.em(0xFE,num);c.jp(label,0xCA)
c.jp('main')
def trans(name,scene,x,y,msg=None,flag=None):
 c.at(name)
 c.ld_a(scene);c.ld_mem(SC);c.ld_a(x);c.ld_mem(PX);c.ld_a(y);c.ld_mem(PY)
 if flag:
  c.ld_a_mem(FLAGS);c.em(0xF6,flag);c.ld_mem(FLAGS);c.call('write_save')
 if msg is not None:c.ld_a(msg);c.ld_mem(MSG)
 c.jp('refresh')
trans('go_s01',1,1,10,1)
c.at('go_e01')
c.ld_a(2);c.ld_mem(SC);c.ld_a(1);c.ld_mem(PX);c.ld_a(10);c.ld_mem(PY)
c.ld_a_mem(FLAGS);c.em(0xE6,1);c.jp('breach_already',0xC2)
c.ld_a_mem(FLAGS);c.em(0xF6,1);c.ld_mem(FLAGS);c.call('write_save')
c.at('breach_already');c.ld_a(32);c.ld_mem(MSG);c.jp('refresh')
trans('go_s02',3,1,10,28)
trans('go_s00',0,17,10,1)
trans('go_s01_back',1,17,10,3)
trans('go_e01_back',2,17,10,3)
trans('enter_cave',4,2,12,9,flag=8)
trans('return_town',3,10,12,28)
trans('enter_archive',5,2,12,14)
trans('return_cave',4,2,12,9)
# Deliberate opening: the Wayfarer falls into the world over eight held frames.
# Fixed-duration offline CPU delays; no wall-clock iPhone dependence.
c.at('intro_fall');c.ld_a(3);c.ld_mem(PY)
c.at('intro_frame');c.call('draw');c.call('intro_delay')
c.ld_a_mem(PY);c.em(0xFE,10);c.em(0xC8) # RET if arrived
c.em(0x3C);c.ld_mem(PY);c.jp('intro_frame')
c.at('intro_delay');c.ld_bc(12000)
c.at('intro_delay_loop');c.em(0x0B,0x78,0xB1);c.jp('intro_delay_loop',0xC2);c.em(0xC9)
# Collision lookup from data in ROM; two-phase: select scene collision ptr, offset y*20+x, read (HL).
c.at('select_collision')
c.ld_a_mem(SC)
for n in range(6):
 c.em(0xFE,n);c.jp('col_ptr_'+str(n),0xCA)
c.ld_hl_label('coll0');c.em(0xC9)
for n in range(6):
 c.at('col_ptr_'+str(n));c.ld_hl_label('coll'+str(n));c.em(0xC9)
c.at('lookup_collision');c.call('select_collision')
c.ld_a_mem(TY);c.em(0x4F);c.ld_de(20)
c.at('lookup_y');c.em(0x79,0xB7);c.jp('lookup_x',0xCA);c.em(0x19,0x0D);c.jp('lookup_y')
c.at('lookup_x');c.ld_a_mem(TX);c.em(0x5F,0x16,0x00,0x19,0x7E,0xC9)
# if collision nonzero, return blocked; but cleared enemy's old tile needs flag and target special.
c.at('try_move');c.call('lookup_collision');c.em(0xB7);c.jp('blocked',0xC2)
# The shade remains a solid living actor even after leaving its original map tile.
c.ld_a_mem(SC);c.em(0xFE,4);c.jp('try_move_clear',0xC2)
c.ld_a_mem(EHP);c.em(0xB7);c.jp('try_move_clear',0xCA)
c.ld_a_mem(TX);c.em(0x47);c.ld_a_mem(EX);c.em(0xB8);c.jp('try_move_clear',0xC2)
c.ld_a_mem(TY);c.em(0x47);c.ld_a_mem(EY);c.em(0xB8);c.jp('try_move_clear',0xC2)
c.ld_a(10);c.ld_mem(MSG);c.jp('refresh')
c.at('try_move_clear');c.em(0xAF);c.ld_mem(PENDING) # movement cancels a pending question
c.ld_a_mem(TX);c.ld_mem(PX);c.ld_a_mem(TY);c.ld_mem(PY)
c.ld_a_mem(TICK);c.em(0x3C);c.ld_mem(TICK)
c.ld_a_mem(SC);c.em(0xFE,4);c.jp('refresh',0xC2);c.call('enemy_turn');c.jp('refresh')
c.at('blocked');c.ld_a(17);c.ld_mem(MSG);c.jp('refresh')
# cardinal NPC/action interaction distances <=1 each coordinate.
c.at('near')
c.ld_a_mem(PX);c.em(0x90);c.jp('near_xpositive',0xD2);c.em(0x2F,0x3C)
c.at('near_xpositive');c.em(0xFE,2);c.jp('near_false',0xD2)
c.ld_a_mem(PY);c.em(0x91);c.jp('near_ypositive',0xD2);c.em(0x2F,0x3C)
c.at('near_ypositive');c.em(0xFE,2);c.jp('near_false',0xD2);c.ld_a(1);c.em(0xC9)
c.at('near_false');c.em(0xAF,0xC9)
# A context handler; scene-dependent, object/turn-based.
c.at('action');c.ld_a_mem(PENDING);c.em(0xB7);c.jp('pip_yes',0xC2)
c.ld_a_mem(SC)
for n,label in [(0,'fruit_action'),(1,'sign_action'),(2,'sign_action'),(3,'town_action'),(4,'cave_action'),(5,'archive_action')]:
 c.em(0xFE,n);c.jp(label,0xCA)
c.jp('main')

c.at('fruit_action');c.ld_b(5);c.ld_c(8);c.call('near');c.em(0xB7);c.jp('no_action',0xCA)
c.ld_a_mem(FLAGS);c.em(0xE6,4);c.jp('fruit_already',0xC2)
c.ld_a_mem(FLAGS);c.em(0xF6,4);c.ld_mem(FLAGS);c.call('write_save');c.ld_a(2);c.ld_mem(MSG);c.jp('refresh')
c.at('fruit_already');c.ld_a(21);c.ld_mem(MSG);c.jp('refresh')
c.at('sign_action');c.ld_b(10);c.ld_c(8);c.call('near');c.em(0xB7);c.jp('no_action',0xCA)
c.ld_a_mem(FLAGS);c.em(0xE6,2);c.jp('sign_already',0xC2)
c.ld_a_mem(FLAGS);c.em(0xF6,2);c.ld_mem(FLAGS);c.call('write_save');c.ld_a(4);c.ld_mem(MSG);c.jp('refresh')
c.at('sign_already');c.ld_a(3);c.ld_mem(MSG);c.jp('refresh')

c.at('town_action');c.ld_b(7);c.ld_c(9);c.call('near');c.em(0xB7);c.jp('town_cave',0xCA)
c.ld_a_mem(FLAGS);c.em(0xE6,0x60);c.jp('pip_already_decided',0xC2)
c.ld_a(1);c.ld_mem(PENDING);c.ld_a(6);c.ld_mem(MSG);c.jp('refresh')
c.at('pip_already_decided');c.ld_a(5);c.ld_mem(MSG);c.jp('refresh')
c.at('town_cave');c.ld_b(10);c.ld_c(13);c.call('near');c.em(0xB7);c.jp('town_baker',0xCA);c.jp('enter_cave')
c.at('town_baker');c.ld_b(15);c.ld_c(8);c.call('near');c.em(0xB7);c.jp('no_action',0xCA)
c.ld_a(23);c.ld_mem(MSG);c.jp('refresh')
c.at('pip_yes');c.em(0xAF);c.ld_mem(PENDING);c.ld_a_mem(FLAGS);c.em(0xF6,0x20);c.ld_mem(FLAGS);c.call('write_save')
c.ld_a(7);c.ld_mem(MSG);c.jp('refresh')
c.at('pip_no');c.em(0xAF);c.ld_mem(PENDING);c.ld_a_mem(FLAGS);c.em(0xF6,0x40);c.ld_mem(FLAGS);c.call('write_save')
c.ld_a(8);c.ld_mem(MSG);c.jp('refresh')

c.at('cave_action');c.ld_b(2);c.ld_c(12);c.call('near');c.em(0xB7);c.jp('cave_gate',0xCA);c.jp('return_town')
c.at('cave_gate');c.ld_b(17);c.ld_c(12);c.call('near');c.em(0xB7);c.jp('cave_enemy',0xCA)
c.ld_a_mem(FLAGS);c.em(0xE6,0x10);c.jp('cave_sealed',0xCA);c.jp('enter_archive')
c.at('cave_sealed');c.ld_a(13);c.ld_mem(MSG);c.jp('refresh')
c.at('cave_enemy');c.ld_a_mem(EHP);c.em(0xB7);c.jp('no_action',0xCA)
c.ld_a_mem(EX);c.em(0x47);c.ld_a_mem(EY);c.em(0x4F);c.call('near');c.em(0xB7);c.jp('no_action',0xCA)
c.ld_a_mem(EHP);c.em(0x3D);c.ld_mem(EHP);c.em(0xB7);c.jp('shade_falls',0xCA)
c.ld_a(11);c.ld_mem(MSG);c.call('enemy_attack');c.jp('refresh')
c.at('shade_falls');c.ld_a_mem(FLAGS);c.em(0xF6,0x10);c.ld_mem(FLAGS);c.call('write_save');c.ld_a(12);c.ld_mem(MSG);c.jp('refresh')
c.at('archive_action');c.ld_b(2);c.ld_c(12);c.call('near');c.em(0xB7);c.jp('archive_record',0xCA);c.jp('return_cave')
c.at('archive_record');c.ld_b(9);c.ld_c(6);c.call('near');c.em(0xB7);c.jp('no_action',0xCA)
c.ld_a_mem(FLAGS);c.em(0xF6,0x80);c.ld_mem(FLAGS);c.call('write_save')
c.ld_a(15);c.ld_mem(MSG);c.jp('refresh')
c.at('no_action');c.ld_a(22);c.ld_mem(MSG);c.jp('refresh')

c.at('journal');c.ld_a_mem(PENDING);c.em(0xB7);c.jp('pip_no',0xC2)
c.ld_a(1);c.ld_mem(JOURNAL);c.call('draw');c.call('wait_key');c.call('wait_release');c.em(0xAF);c.ld_mem(JOURNAL);c.jp('refresh')
c.at('refresh');c.call('draw');c.jp('main')
# Enemy pressure only in cave, and only alive. Collision/AI movement deliberately small.
c.at('enemy_turn');c.ld_a_mem(EHP);c.em(0xB7);c.em(0xC8) # RET Z
c.ld_a_mem(EX);c.em(0x47);c.ld_a_mem(EY);c.em(0x4F);c.call('near');c.em(0xB7);c.jp('enemy_chase',0xCA)
c.call('enemy_attack');c.em(0xC9)
c.at('enemy_chase')
# Dynamic enemy attempts one horizontal step; if x same, one vertical step.
# All target moves check the SAME collision grid as the player.
c.ld_a_mem(EX);c.ld_mem(TX);c.ld_a_mem(EY);c.ld_mem(TY)
c.ld_a_mem(PX);c.em(0x47)
c.ld_a_mem(EX);c.em(0xB8);c.jp('enemy_vertical',0xCA);c.jp('enemy_left',0xD2)
c.ld_a_mem(TX);c.em(0x3C);c.ld_mem(TX);c.jp('enemy_test_tile')
c.at('enemy_left');c.ld_a_mem(TX);c.em(0x3D);c.ld_mem(TX);c.jp('enemy_test_tile')
c.at('enemy_vertical');c.ld_a_mem(PY);c.em(0x47);c.ld_a_mem(EY);c.em(0xB8);c.jp('enemy_stop',0xCA);c.jp('enemy_up',0xD2)
c.ld_a_mem(TY);c.em(0x3C);c.ld_mem(TY);c.jp('enemy_test_tile')
c.at('enemy_up');c.ld_a_mem(TY);c.em(0x3D);c.ld_mem(TY)
c.at('enemy_test_tile');c.call('lookup_collision');c.em(0xB7);c.jp('enemy_stop',0xC2)
# Never occupy the same tile as the hero. Attack from its approach instead.
c.ld_a_mem(TX);c.em(0x47);c.ld_a_mem(PX);c.em(0xB8);c.jp('enemy_move_commit',0xC2)
c.ld_a_mem(TY);c.em(0x47);c.ld_a_mem(PY);c.em(0xB8);c.jp('enemy_move_commit',0xC2)
c.call('enemy_attack');c.em(0xC9)
c.at('enemy_move_commit');c.ld_a_mem(TX);c.ld_mem(EX);c.ld_a_mem(TY);c.ld_mem(EY)
c.at('enemy_stop');c.em(0xC9)
# Attack resets player if HP exhausted, carrying discovery flags intact.
c.at('enemy_attack');c.ld_a_mem(HP);c.em(0xB7);c.jp('enemy_rescue',0xCA)
c.em(0x3D);c.ld_mem(HP);c.em(0xB7);c.jp('enemy_rescue',0xCA)
c.ld_a(31);c.ld_mem(MSG);c.em(0xC9)
c.at('enemy_rescue');c.ld_a(3);c.ld_mem(SC);c.ld_a(10);c.ld_mem(PX);c.ld_a(12);c.ld_mem(PY)
c.ld_a(MAXHP);c.ld_mem(HP);c.ld_a(3);c.ld_mem(EHP);c.ld_a(14);c.ld_mem(EX);c.ld_a(9);c.ld_mem(EY);c.ld_a(18);c.ld_mem(MSG);c.em(0xC9)

# Old compatible, two-slot commit CRC (not cryptographic) save. Preserve previous state on partial write.
c.at('read_slot')
c.em(0x2A,0xFE,0x44);c.jp('bad_slot',0xC2)
c.em(0x2A,0xFE,0x4B);c.jp('bad_slot',0xC2)
c.em(0x2A,0x47,0x2A,0x4F,0x2A,0x57,0x7E,0xFE,0xA5);c.jp('bad_slot',0xC2)
c.em(0x78,0xA9,0xEE,0x5A,0xBA);c.jp('bad_slot',0xC2)
c.em(0xA7,0xC9)
c.at('bad_slot');c.em(0x37,0xC9)
c.at('write_save');c.ld_a_mem(SLOT);c.em(0xFE,0);c.jp('write_slot1',0xCA)
c.ld_hl(0xA000);c.em(0xAF);c.ld_mem(SLOT);c.jp('write_slot_start')
c.at('write_slot1');c.ld_hl(0xA010);c.ld_a(1);c.ld_mem(SLOT)
c.at('write_slot_start');c.em(0xE5);c.ld_de(5);c.em(0x19,0xAF,0x77,0xE1)
c.em(0x36,0x44,0x23,0x36,0x4B,0x23)
c.ld_a_mem(SEQ);c.em(0x3C);c.ld_mem(SEQ);c.em(0x47,0x22)
c.ld_a_mem(FLAGS);c.em(0x4F,0x22)
c.em(0x78,0xA9,0xEE,0x5A,0x22);c.ld_a(0xA5);c.em(0x77,0xC9)
# IO and timing
c.at('safe_lcd_off');c.ldh_get(0x40);c.em(0xCB,0x7F);c.em(0xC8);c.call('wait_vblank');c.em(0xAF);c.ldh_put(0x40);c.em(0xC9)
c.at('wait_vblank');c.ldh_get(0x44);c.em(0xFE,144);c.jp('wait_vblank',0xDA);c.em(0xC9)
c.at('clear_map');c.ld_hl(0x9800);c.ld_bc(1024)
c.at('clear_map_loop');c.em(0x36,0x00,0x23,0x0B,0x78,0xB1);c.jp('clear_map_loop',0xC2);c.em(0xC9)
c.at('scan_key');c.ld_a(0x20);c.ldh_put(0x00);c.em(0,0);c.ldh_get(0x00);c.em(0x2F,0xE6,0x0F,0x47)
for mask,label in [(1,'key_right'),(2,'key_left'),(4,'key_up'),(8,'key_down')]:c.em(0x78,0xE6,mask);c.jp(label,0xC2)
c.ld_a(0x10);c.ldh_put(0x00);c.em(0,0);c.ldh_get(0x00);c.em(0x2F,0xE6,0x03,0x47)
for mask,label in [(1,'key_a'),(2,'key_b')]:c.em(0x78,0xE6,mask);c.jp(label,0xC2)
c.em(0xAF,0xC9)
for label,val in [('key_right',1),('key_left',2),('key_up',3),('key_down',4),('key_a',5),('key_b',6)]:c.at(label);c.ld_a(val);c.em(0xC9)
c.at('wait_key');c.call('scan_key');c.em(0xB7);c.jp('wait_key',0xCA);c.em(0xC9)
c.at('wait_release');c.call('scan_key');c.em(0xB7);c.jp('wait_release',0xC2);c.em(0xC9)
# Draw loop: copy map from source ROM to VRAM, overlay persistent objects and moving player,
# plus restrained two-row HUD and journal. LCD disabled only in VBlank.
c.at('choose_map');c.ld_a_mem(SC)
for i in range(6):c.em(0xFE,i);c.jp('map_ptr_'+str(i),0xCA)
c.ld_hl_label('map0');c.em(0xC9)
for i in range(6):c.at('map_ptr_'+str(i));c.ld_hl_label('map'+str(i));c.em(0xC9)
c.at('draw');c.call('safe_lcd_off');c.call('clear_map')
c.em(0xAF);c.ld_mem(0xFE00) # hide OAM sprite on journal screen
c.ld_a_mem(JOURNAL);c.em(0xB7);c.jp('draw_journal',0xC2)
c.call('choose_map');c.ld_de(0x9800);c.ld_a(15);c.ld_mem(ROW)
c.at('copy_map_row');c.ld_b(20)
c.at('copy_map_col');c.em(0x2A,0x12,0x13,0x05);c.jp('copy_map_col',0xC2)
c.em(0x7B,0xC6,12,0x5F);c.jp('copy_map_no_carry',0xD2);c.em(0x14)
c.at('copy_map_no_carry');c.ld_a_mem(ROW);c.em(0x3D);c.ld_mem(ROW);c.jp('copy_map_row',0xC2)
# Persistent object transforms: cactus fruit, sign chalk, cave enemy and gate.
c.ld_a_mem(SC);c.em(0xB7);c.jp('overlay_fruit',0xCA)
c.em(0xFE,1);c.jp('overlay_sign',0xCA)
c.em(0xFE,2);c.jp('overlay_sign',0xCA)
c.em(0xFE,4);c.jp('overlay_cave',0xCA)
c.jp('draw_player')
c.at('overlay_fruit');c.ld_a_mem(FLAGS);c.em(0xE6,4);c.jp('draw_player',0xCA)
c.tile(5,7,TILE_BY_NAME['grass']);c.jp('draw_player')
c.at('overlay_sign');c.ld_a_mem(FLAGS);c.em(0xE6,2);c.jp('draw_player',0xCA)
c.tile(10,8,TILE_BY_NAME['rune']);c.jp('draw_player')
c.at('overlay_cave');c.tile(14,9,TILE_BY_NAME['floor'])
c.ld_a_mem(EHP);c.em(0xB7);c.jp('open_gate_graphic',0xCA)
c.ld_a_mem(EY);c.em(0x6F,0x26,0x00)
for _ in range(5):c.em(0x29)
c.ld_de(0x9800);c.em(0x19);c.ld_a_mem(EX);c.em(0x5F,0x16,0,0x19)
c.em(0x36,TILE_BY_NAME['enemy']);c.jp('draw_player')
c.at('open_gate_graphic');c.tile(17,12,TILE_BY_NAME['open'])
c.at('draw_player')
# OAM player: 8x16 sprite, separate from BG tiles (correct Game Boy layering).
# Sprite top is one tile above grounded feet at (PX,PY).
c.ld_a_mem(PY)
for _ in range(3):c.em(0x87) # ADD A,A * 3 = *8
c.em(0xC6,8);c.ld_mem(0xFE00) # Y pos = (PY*8+8)
c.ld_a_mem(PX)
for _ in range(3):c.em(0x87)
c.em(0xC6,8);c.ld_mem(0xFE01)
c.ld_a_mem(TICK);c.em(0xE6,1);c.jp('hero_idle',0xCA)
c.ld_a(TILE_BY_NAME['hero_walk_head']);c.jp('hero_sprite_tile')
c.at('hero_idle');c.ld_a(TILE_BY_NAME['hero_idle_head'])
c.at('hero_sprite_tile');c.ld_mem(0xFE02)
c.em(0xAF);c.ld_mem(0xFE03)
# HUD top row with scene and HP, two text lines from current MSG.
c.ld_a_mem(SC)
for i in range(6):c.em(0xFE,i);c.jp('hud_title_'+str(i),0xCA)
c.jp('hud_after_title')
TITLES=['CACTUS BRINK','FIRST SIGN','SIGN ECHO','CINDER FORD','DAMP CORRIDOR','ARCHIVE SLUICE']
for i,name in enumerate(TITLES):
 c.at('hud_title_'+str(i));c.print_at(15,1,'title_'+str(i));c.jp('hud_after_title')
c.at('hud_after_title')
c.print_at(15,16,'hp_title')
c.ld_a_mem(HP);c.em(0xC6,16);c.ld_hl(0x9800+15*32+19);c.em(0x77)
c.ld_a_mem(MSG)
for i in range(len(MESSAGES)):
 c.em(0xFE,i);c.jp('hud_msg_'+str(i),0xCA)
c.jp('hud_ready')
for i in range(len(MESSAGES)):
 c.at('hud_msg_'+str(i));c.print_at(16,0,'msg_'+str(i)+'a');c.print_at(17,0,'msg_'+str(i)+'b');c.jp('hud_ready')
c.at('hud_ready');c.ld_a(0x97);c.ldh_put(0x40);c.em(0xC9) # sprites/BG on
# Full screen journal page. The scene is not overwritten permanently; next draw returns.
c.at('draw_journal')
c.print_at(1,2,'journal_heading');c.print_at(3,1,'journal_sub')
c.ld_a_mem(FLAGS);c.em(0xE6,1);c.jp('log_no_breach',0xCA)
c.print_at(5,1,'log_breach');c.jp('log_mark')
c.at('log_no_breach');c.print_at(5,1,'log_no_breach_txt')
c.at('log_mark');c.ld_a_mem(FLAGS);c.em(0xE6,2);c.jp('log_no_mark',0xCA)
c.print_at(7,1,'log_yes_mark');c.jp('log_fruit')
c.at('log_no_mark');c.print_at(7,1,'log_no_mark_txt')
c.at('log_fruit');c.ld_a_mem(FLAGS);c.em(0xE6,4);c.jp('log_no_fruit',0xCA)
c.print_at(9,1,'log_taken');c.jp('log_cave')
c.at('log_no_fruit');c.print_at(9,1,'log_not_taken')
c.at('log_cave');c.ld_a_mem(FLAGS);c.em(0xE6,0x10);c.jp('log_no_sha',0xCA)
c.print_at(11,1,'log_sha');c.jp('log_last')
c.at('log_no_sha');c.print_at(11,1,'log_no_sha_txt')
c.at('log_last');c.ld_a_mem(FLAGS);c.em(0xE6,0x80);c.jp('log_no_arch',0xCA)
c.print_at(13,1,'log_arch');c.jp('log_end')
c.at('log_no_arch');c.print_at(13,1,'log_not_arch')
c.at('log_end');c.print_at(16,1,'log_exit');c.jp('hud_ready')
# Uppercase ascii font remains 64 chars (32..95); string data in ROM.
c.at('puts');c.em(0x1A,0xB7);c.jp('puts_ret',0xCA);c.em(0xD6,32,0x22,0x13);c.jp('puts')
c.at('puts_ret');c.em(0xC9)
for i,name in enumerate(TITLES):c.at('title_'+str(i));c.em(*name.encode('ascii'),0)
for name,value in [('hp_title','HP'),('journal_heading','THE ROAD REMEMBERS'),('journal_sub','WHAT YOU KNOW IS...'),('log_breach','B001: THE ROAD FOLDS'),('log_no_breach_txt','B001: NOT YET SEEN'),('log_yes_mark','SIGN: MARKED'),('log_no_mark_txt','SIGN: UNMARKED'),('log_taken','FRUIT: TAKEN'),('log_not_taken','FRUIT: STILL THERE'),('log_sha','SHADE: DISPERSED'),('log_no_sha_txt','SHADE: STILL THERE'),('log_arch','ARCHIVE: TWO FIGURES'),('log_not_arch','ARCHIVE: UNSEEN'),('log_exit','ANY KEY TO RETURN')]:
 assert len(value)<=20,(name,value)
 c.at(name);c.em(*value.encode('ascii'),0)
for i,(a,b) in enumerate(MESSAGES):
 c.at('msg_'+str(i)+'a');c.em(*a.encode('ascii'),0)
 c.at('msg_'+str(i)+'b');c.em(*b.encode('ascii'),0)

# Stub ROM map data pointers at 0x5800+ scene*300 (not in instruction stream).
for i in range(6):c.labels['map'+str(i)]=0x5800+i*300
for i in range(6):c.labels['coll'+str(i)]=0x6400+i*300
c.done()
assert c.pc<0x5000,(hex(c.pc),'CODE OVER ART REGION')
# High contrast 2bpp ink; glyphs are hand-drawn by the project.
font=bytearray(font_tiles())
for offset in range(0,len(font),2):font[offset+1]=font[offset]
ROM[0x5000:0x5400]=font
ROM[0x5400:0x5400+len(art_bytes())]=art_bytes()
for i,grid in enumerate(MAP_TILES):ROM[0x5800+i*300:0x5800+(i+1)*300]=grid
for i,grid in enumerate(COLLISION):ROM[0x6400+i*300:0x6400+(i+1)*300]=grid
# Cartridge checksum/hardware checksums.
ch=0
for i in range(0x134,0x14D):ch=(ch-ROM[i]-1)&0xFF
ROM[0x14D]=ch
s=sum(ROM[:0x14E])+sum(ROM[0x150:]);ROM[0x14E:0x150]=(s&0xFFFF).to_bytes(2,'big')
name=OUT/'dreamkiller_road_v0_2.gb'
name.write_bytes(ROM)
print('BUILD',name,'sha256',hashlib.sha256(ROM).hexdigest(),'code_end',hex(c.pc),'art_tiles',len(art_bytes())//16,'maps',len(MAP_TILES),'labels',len(c.labels))