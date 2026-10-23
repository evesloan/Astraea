"""Read-only Godot PCK v2/v3 index and exact entry extraction.
Format reference: https://raw.githubusercontent.com/godotengine/godot/4.6-stable/core/io/file_access_pack.cpp
No Godot process, resource import, script execution, or source conversion.
"""
from pathlib import Path,PurePosixPath
import struct,hashlib,json,sys
def index(path):
 p=Path(path);size=p.stat().st_size
 with p.open("rb")as f:
  def u32():return struct.unpack("<I",f.read(4))[0]
  def u64():return struct.unpack("<Q",f.read(8))[0]
  magic=u32();assert magic==0x43504447,"Not standalone Godot PCK"
  version=u32();engine=[u32(),u32(),u32()];flags=u32();base=u64()
  assert version in (2,3)and flags & 1 == 0,"Unsupported/encrypted pack"
  if version==3:directory=u64();f.seek(directory)
  else:directory=96;f.seek(96)
  count=u32();assert 0<count<1000000
  rows={}
  for i in range(count):
   n=u32();assert n<100000
   name=f.read(n).rstrip(bytes([0])).decode("utf-8");offset=u64()+base;length=u64();md5=f.read(16).hex();entry_flags=u32()
   name=name.removeprefix("res://");target=PurePosixPath(name)
   assert not target.is_absolute()and ".."not in target.parts and name not in rows
   assert offset>=0 and offset+length<=size and entry_flags==0,(name,offset,length,entry_flags)
   rows[name]={"path":name,"offset":offset,"bytes":length,"md5":md5,"flags":entry_flags}
 return {"path":str(p.resolve()),"bytes":size,"version":version,"engine":engine,"flags":flags,"file_base":base,"directory":directory,"entries":rows}
def extract(pack,row,destination,expected_sha256=None):
 out=Path(destination);out.parent.mkdir(parents=True,exist_ok=True);assert not out.exists(),"Refuse overwrite "+str(out)
 h=hashlib.sha256();m=hashlib.md5();remaining=row["bytes"]
 with Path(pack).open("rb")as f,out.open("xb")as w:
  f.seek(row["offset"])
  while remaining:
   b=f.read(min(16*1024*1024,remaining));assert b;remaining-=len(b);h.update(b);m.update(b);w.write(b)
 assert m.hexdigest()==row["md5"],row["path"]
 if expected_sha256:assert h.hexdigest()==expected_sha256,row["path"]
 return {"pack_path":row["path"],"local_path":str(out.resolve()),"bytes":row["bytes"],"md5":m.hexdigest(),"sha256":h.hexdigest()}
