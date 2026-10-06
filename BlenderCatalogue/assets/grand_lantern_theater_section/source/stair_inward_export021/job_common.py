"""Scratch-only job constants and new-only output guards. No engine on import."""
from pathlib import Path
import json,hashlib,sys
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section')
S=P/'source/stair_inward_channels_020'
SOURCE=S/'AST-CUL-005_inward_stair_channels_020.blend'
SOURCE_SHA='fd454d55af4718f8cd3458223c87f0c8fa83f9fe3ad514c94486d7ce87885ef8'
OUT=R/'run001';GLB=OUT/'AST-CUL-005_inward_stair_channels_021.glb'
SNAPSHOT=OUT/'SOURCE_SNAPSHOT.json';EXPORT_RECEIPT=OUT/'EXPORT_RECEIPT.json';QA=OUT/'INDEPENDENT_BINARY_QA.json'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_new(p,data):
 with Path(p).open('x')as f:json.dump(data,f,indent=2,allow_nan=False);f.write('\n')
def verify_pins():
 manifest=read(R/'EXECUTION_MANIFEST.json')
 for path,expected in manifest['input_pins'].items():assert sha(path)==expected,('Pinned job input changed',path)
 assert sha(SOURCE)==SOURCE_SHA
 return manifest
