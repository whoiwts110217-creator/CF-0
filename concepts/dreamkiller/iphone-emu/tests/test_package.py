"""Source-only checks for the original Dreamkiller Pocket iPhone emulator package."""
import json
import re
import unittest
from pathlib import Path

SITE=Path(__file__).resolve().parents[1] / 'site'

class PocketPackageTests(unittest.TestCase):
    def test_local_core_and_corresponding_source_are_bundled(self):
        self.assertGreater((SITE/'GameBoy.min.js').stat().st_size, 500000)
        self.assertGreater((SITE/'GameBoy.js').stat().st_size, 500000)
        self.assertIn('GNU GENERAL PUBLIC LICENSE', (SITE/'GPL-2.0.txt').read_text(encoding='utf-8'))
    def test_i_phone_launcher_references_existing_local_assets(self):
        index=(SITE/'index.html').read_text(encoding='utf-8')
        for item in ('GameBoy.min.js','app.js','styles.css','manifest.webmanifest','icon.svg','rom-input','demo-button','playing','save-button'):
            self.assertIn(item,index)
        self.assertNotIn('<script src="http',index)
        self.assertNotIn('icon-192.png',index)
    def test_rom_header_and_global_checksums(self):
        data=(SITE/'road-test.gb').read_bytes()
        self.assertEqual(len(data),32768)
        self.assertEqual(data[0x100:0x104],bytes((0,0xc3,0x50,1)))
        x=0
        for i in range(0x134,0x14d): x=(x-data[i]-1)&255
        self.assertEqual(data[0x14d],x)
        expected=(data[0x14e]<<8)|data[0x14f]
        actual=(sum(data[:0x14e])+sum(data[0x150:]))&65535
        self.assertEqual(expected,actual)
    def test_original_rom_rebuilds_byte_for_byte(self):
        import runpy
        source = runpy.run_path(str(SITE/'road-test-source.py'))
        self.assertEqual(source['build_rom'](), (SITE/'road-test.gb').read_bytes())

    def test_pwa_can_cache_all_required_local_assets(self):
        manifest=json.loads((SITE/'manifest.webmanifest').read_text(encoding='utf-8'))
        self.assertEqual(manifest['display'],'standalone')
        self.assertEqual(manifest['start_url'],'./')
        worker=(SITE/'service-worker.js').read_text(encoding='utf-8')
        for name in ['index.html','styles.css','app.js','GameBoy.min.js','icon.svg','road-test.gb','manifest.webmanifest']:
            self.assertIn(name,worker)
            self.assertTrue((SITE/name).is_file())
    def test_original_dreamkiller_road_prototype_is_exact_hosted_cartridge(self):
        import hashlib
        cartridge = SITE / "road-v01.gb"
        master = SITE.parents[1] / "rom_v0_1" / "dreamkiller_road_v0_1_2.gb"
        rom = cartridge.read_bytes()
        self.assertEqual(len(rom), 32768)
        self.assertEqual(rom, master.read_bytes())
        self.assertEqual(hashlib.sha256(rom).hexdigest(), "04370dae88b8ebcce9014063267d03b2bfb32dbbee3e2133daf31f6313cb08d6")
        self.assertEqual(rom[0x147], 0x03)  # MBC1+RAM+BATTERY
        self.assertEqual(rom[0x149], 0x02)  # 8KB SRAM
        h=0
        for byte in rom[0x134:0x14d]:
            h=(h-byte-1)&255
        self.assertEqual(rom[0x14d], h)
        self.assertEqual((sum(rom[:0x14e])+sum(rom[0x150:]))&65535, int.from_bytes(rom[0x14e:0x150],"big"))
        html=(SITE/"index.html").read_text(encoding="utf-8")
        app=(SITE/"app.js").read_text(encoding="utf-8")
        worker=(SITE/"service-worker.js").read_text(encoding="utf-8")
        self.assertIn('id="road-button"', html)
        self.assertIn('"road-button"', app)
        self.assertIn('fetch("./road-v01.gb")',app)
        self.assertIn('"./road-v01.gb"',worker)

    def test_local_file_only_not_upload(self):
        app=(SITE/'app.js').read_text(encoding='utf-8')
        self.assertIn('file.arrayBuffer()',app)
        self.assertIn('new KeyboardEvent',app)
        self.assertIn('downloadStateGameBoy',app)
        self.assertNotIn('fetch("http',app)
        self.assertTrue('showMobileControls:false' in app)
if __name__=='__main__': unittest.main()
