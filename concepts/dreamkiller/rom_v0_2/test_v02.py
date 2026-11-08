"""Dreamkiller v0.2 real ROM opcode/map/save tests in LIMITED LR35902 model.
This is not cycle-accurate Gambatte nor physical Game Boy validation.
"""
import unittest
import random
from cpu_harness import CPU,ROM,LABEL
from art import MAPS,ART_ORDER,TILE_BY_NAME,MAP_TILES,COLLISION

SC=0xC000; PX=SC+1; PY=SC+2; FLAGS=SC+3;SEQ=SC+4; HP=SC+6; EHP=SC+7;EX=SC+8; EY=SC+9; PENDING=SC+15
BASE_TOWN=['right']*10+['right']*9+['up','a','down']+['right']*9+['right']*18+['right']*6
BASE_CAVE=BASE_TOWN+['a','a']+['right']*3+['down']*2+['a']

def press_sequence(actions,external_ram=None,max_ops=13_000_000):
    c=CPU(actions,external_ram=external_ram)
    c.run_until(lambda x:x.pc==LABEL['main'] and x.scans>=2*len(actions),max_ops)
    return c

class CartridgeV02Tests(unittest.TestCase):
 def test_header_and_sprite_tile_dimensions(self):
    self.assertEqual(len(ROM),32768)
    self.assertEqual(ROM[0x147],3)
    self.assertEqual(ROM[0x149],2)
    self.assertEqual(ROM[0x143],0)
    self.assertEqual(ROM[0x14D],(sum((256-b-1) for b in ROM[0x134:0x14d]))&255)
    self.assertEqual(int.from_bytes(ROM[0x14e:0x150],'big'),(sum(ROM[:0x14e])+sum(ROM[0x150:]))&65535)
    self.assertEqual(TILE_BY_NAME['hero_idle_head']%2,0)
    self.assertEqual(TILE_BY_NAME['hero_walk_head']%2,0)
 def test_first_fall_and_genuine_sprite_oam(self):
    c=press_sequence([])
    self.assertEqual(c.mem[PX],9)
    self.assertEqual(c.mem[PY],10)
    self.assertEqual(c.mem[0xff40]&0x06,0x06)
    self.assertEqual(c.mem[0xfe00],10*8+8)
    self.assertEqual(c.mem[0xfe01],9*8+8)
    self.assertEqual(c.mem[0xfe02],TILE_BY_NAME['hero_idle_head'])
    self.assertEqual(c.mem[0x9800+10*32+9],TILE_BY_NAME['crack'])
 def test_collisions_are_real_solid_grid_not_text_instructions(self):
    c=press_sequence(['up']*12)
    self.assertGreaterEqual(c.mem[PY],4)
    self.assertEqual(c.mem[SC],0)
    self.assertEqual(len(MAP_TILES),6)
    self.assertTrue(all(len(v)==300 for v in MAP_TILES))
    self.assertTrue(all(len(v)==300 for v in COLLISION))
 def test_fruit_consumed_only_once_and_recovered_from_battery(self):
    c=press_sequence(['left']*4+['up']+['a','a'])
    self.assertEqual(c.mem[FLAGS]&4,4)
    self.assertEqual(c.mem[SEQ],1)
    ram=c.saved_ram();second=press_sequence(['left']*4+['up']+['a'],ram)
    self.assertEqual(second.mem[FLAGS]&4,4)
    self.assertEqual(second.mem[SEQ],1)
    self.assertEqual(ram,second.saved_ram())
    self.assertEqual(second.mem[0x9800+7*32+5],TILE_BY_NAME['grass'])
 def test_sign_mark_and_breach_are_reproducible_not_multi_saved(self):
    s= ['right']*10+['right']*9+['up','a','down']+['right']*9
    c=press_sequence(s)
    self.assertEqual(c.mem[SC],2)
    self.assertEqual(c.mem[FLAGS]&3,3)
    self.assertEqual(c.mem[SEQ],2)
    self.assertEqual(c.mem[0x9800+8*32+10],TILE_BY_NAME['rune'])
    c2=press_sequence(s+['left']+['right']*2)
    self.assertEqual(c2.mem[SC],2)
    self.assertEqual(c2.mem[FLAGS]&3,3)
    self.assertEqual(c2.mem[SEQ],2)
 def test_pip_choice_is_genuine_and_mutually_exclusive(self):
    yes=press_sequence(BASE_TOWN+['a','a','a'])
    self.assertEqual(yes.mem[SC],3)
    self.assertEqual(yes.mem[FLAGS]&0x60,0x20)
    self.assertEqual(yes.mem[PENDING],0)
    no=press_sequence(BASE_TOWN+['a','b','a','a'])
    self.assertEqual(no.mem[FLAGS]&0x60,0x40)
    self.assertEqual(no.mem[PENDING],0)
 def test_movement_cancels_pending_pip_reply(self):
    c=press_sequence(BASE_TOWN+['a']+['left']*3+['a'])
    self.assertEqual(c.mem[PENDING],0)
    self.assertEqual(c.mem[FLAGS]&0x60,0)
 def test_growing_cave_and_gate_not_faked_by_messages(self):
    c=press_sequence(BASE_CAVE)
    self.assertEqual(c.mem[SC],4)
    self.assertEqual(c.mem[FLAGS]&8,8)
    self.assertEqual(c.mem[PX:PY+1],bytes((2,12)))
    self.assertEqual(c.mem[EHP],3)
    self.assertEqual(c.mem[0x9800+12*32+17],TILE_BY_NAME['sealed'])
 def test_encounter_has_collision_damage_victory_and_open_gate(self):
    moves=BASE_CAVE+['right']*12+['up']+['a']*3
    c=press_sequence(moves)
    self.assertEqual(c.mem[SC],4)
    self.assertEqual(c.mem[EHP],0)
    self.assertTrue(c.mem[FLAGS]&0x10)
    self.assertLess(c.mem[HP],8)
    self.assertEqual(c.mem[0x9800+12*32+17],TILE_BY_NAME['open'])
    reboot=press_sequence([],c.saved_ram())
    self.assertEqual(reboot.mem[FLAGS]&0x10,0x10)
    self.assertEqual(reboot.mem[EHP],0)
 def test_player_cannot_occupy_a_living_shade(self):
    c=press_sequence(BASE_CAVE+['right']*12+['up']*2)
    self.assertNotEqual((c.mem[PX],c.mem[PY]),(c.mem[EX],c.mem[EY]))
 def test_old_road_v013_save_flags_recover(self):
    old=bytearray(8192)
    flags=3;seq=201
    old[0:6]=bytes((0x44,0x4b,seq,flags,seq^flags^0x5a,0xa5))
    c=press_sequence([],old)
    self.assertEqual(c.mem[FLAGS]&3,3)
    self.assertEqual(c.mem[SEQ],seq)
 def test_journal_shows_real_flag_as_distinct_video_state(self):
    c=press_sequence(['left']*4+['up']+['a','b','a'])
    self.assertEqual(c.mem[FLAGS]&4,4)
    self.assertEqual(c.mem[0xc010],0)
 def test_many_deterministic_key_events_no_freeze(self):
    r=random.Random(370);choices=['right','left','up','down','a','b']
    a=[r.choice(choices) for _ in range(160)]
    c=press_sequence(a,max_ops=18_000_000)
    self.assertIn(c.mem[SC],range(6))
    self.assertIn(c.mem[HP],range(1,9))

if __name__=='__main__':unittest.main()