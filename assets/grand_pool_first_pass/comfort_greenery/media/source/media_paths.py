"""Portable package paths and retained dependency names. No writes or app launch."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT.parent
CFG=json.loads((ROOT/'retained_roots.json').read_text())
CAT=next((p for p in ROOT.parents if (p/'catalogue_manifest.json').is_file()),Path(CFG['catalogue_fallback']))
GAME=Path(CFG['game_fallback'])
AUDIT=PACKAGE/'reference_audit'
assert (AUDIT/'REFERENCE_RELOCATION.json').is_file(),'Missing portable sibling reference audit archive'

def original_path(s):
 p=Path(s)
 for prefix,base in [(Path(CFG['original_catalogue_prefix']),CAT),(Path(CFG['original_game_prefix']),GAME)]:
  if p.is_relative_to(prefix):return base/p.relative_to(prefix)
 return p

def pin_name(p):
 p=Path(p).resolve()
 # Package wins before catalogue when installed inside the catalogue.
 for name,base in [('package',PACKAGE),('catalogue',CAT),('game',GAME)]:
  if p.is_relative_to(base.resolve()):return name+'://'+str(p.relative_to(base.resolve()))
 raise ValueError('Unrecognised retained dependency root: '+str(p))

def resolve_pin(s):
 for name,base in [('package',PACKAGE),('catalogue',CAT),('game',GAME)]:
  if s.startswith(name+'://'):
   p=(base/s.split('://',1)[1]).resolve();assert p.is_relative_to(base.resolve());return p
 return original_path(s)

def archived_reference(original):
 row=json.loads((AUDIT/'REFERENCE_RELOCATION.json').read_text())['paths'][original]
 p=(PACKAGE/row['relative_path']).resolve();assert p.is_relative_to(AUDIT.resolve());return p,row['sha256']

def new_catalogue_writes(paths):
 return [str(Path(p).resolve().relative_to(CAT.resolve()))for p in paths if Path(p).resolve().is_relative_to(CAT.resolve())]
