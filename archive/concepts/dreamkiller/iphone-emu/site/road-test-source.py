#!/usr/bin/env python3
"""Rebuild the original Dreamkiller Pocket diagnostic cartridge, byte for byte.

This 32 KiB GB ROM tests the emulation/display/input path. It is NOT a
Dreamkiller game or a third-party commercial ROM. Requires Python 3 only.
"""
import base64
from pathlib import Path

HEADER = "AMNQAc7tZmbMDQALA3MAgwAMAA0ACBEfiIkADtzMbubd3dmZu7tnY24O7Mzd3Jmfu7kzPkRLIFBPQ0tFVCBURVNUAAAAAAAAAAABMwDemb7zr+BAPuTgRyEABBEAgAHQASoSEwt4sSD4IdAFEQCYAQAEKhITC3ixIPg+keBAPhDgAPAAy0coBstPKAgY8D4b4EcY6j7k4EcY5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=="
TILES = "AAAAAAAAAAAAAAAAAAAAAAgICAgICAgI//8ICAgICAgAAAAAAAAAAP//AAAAAAAAAAAQECAgICBgYEBAQECAgAAAMDBISGhoSEhISDAwAAAAAGBgICAgICAgICBwcAAAAAAAAAAAICAAAAAAICAAAAAAMDAwMDAwMDB4eEhIAAAAAHBwSEhISHBwSEh4eAAAAAA4OEBAQEBAQEBAODgAAAAAcHBISEhISEhISHBwAAAAAHh4QEBAQHh4QEB4eAAAAAB4eEBAQEB4eEBAQEAAAAAAODhAQEBAWFhISDg4AAAAAEhISEhISHh4SEhISAAAAABwcCAgICAgICAgcHAAAAAASEhQUGBgUFBQUEhIAAAAAEBAQEBAQEBAQEB4eAAAAABISHh4eHh4eEhISEgAAAAASEhoaGhoWFhYWEhIAAAAADAwSEhISEhISEgwMAAAAAB4eEhIeHhAQEBAQEAAAAAAeHhISHBwWFhISEREAAAAADg4QEBwcBgYCAh4eAAAAAD4+CAgICAgICAgICAAAAAASEhISEhISEhISDAwAAAAAEhISEgwMDAwMDAwMAAAAACIiFBQICAgICAgICAAAAgICAgICAgICAgICAgICAg="
ROWS = ["+------------------+","|  DREAMKILLER     |","|  POCKET GB TEST  |","|------------------|","|                  |","|  CONTINUITY      |","|  THE ROAD IS HERE|","|                  |","|  A: INVERT       |","|  B: RESET        |","|                  |","|  TOUCH BUTTONS   |","|  TO TEST INPUT   |","|                  |","|  TEST ROM ONLY   |","|  NOT THE GAME    |","|     CF / 001     |","+------------------+"]

def build_rom():
    rom = bytearray(32768)
    rom[0x100:0x200] = base64.b64decode(HEADER)
    rom[0x400:0x5d0] = base64.b64decode(TILES)
    indexes = {c:i for i,c in enumerate(sorted(set(''.join(ROWS))))}
    m = bytearray([indexes[' ']] * 1024)
    for y, row in enumerate(ROWS):
        if len(row) != 20:
            raise ValueError("row width must be 20 tiles")
        for x,c in enumerate(row): m[y*32+x] = indexes[c]
    rom[0x5d0:0x9d0] = m
    return bytes(rom)

if __name__ == "__main__":
    output = Path(__file__).with_name("road-test.gb")
    output.write_bytes(build_rom())
    print(f"Wrote {output} ({output.stat().st_size} bytes)")
