# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['src\\run.py'],
             pathex=['E:\\Python\\scripts\\arena-deck-assistant'],
             binaries=[],
             datas=[
				('src/get_arena_ids.py', '.'),
				('src/parse_arena_log.py', '.'),
				('src/scrape_decklists.py', '.'),
				('src/summary_strings.py', '.'),
				('data/settings.json', '.')
			 ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='arena-deck-assistant',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='src')
