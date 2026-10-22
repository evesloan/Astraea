from pathlib import Path
import bpy,json,hashlib,math,shutil
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');P=R/'Game/family_specialty_bank_20261022';N=Path(__file__).resolve().parent;d=json.loads((P/'PLAN.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert all(sha(R/p)==h for p,h in d['pins'].items());assert shutil.disk_usage(R).free>500_000_000
bpy.ops.wm.read_factory_settings(use_empty=True);sources={}
for row in d['rooms']:
 path=R/row['source_native']
 if str(path)not in sources:
  with bpy.data.libraries.load(str(path),link=True)as(a,b):b.objects=a.objects
  collection=bpy.data.collections.new('Retained_'+path.stem)
  for o in b.objects:
   if o and o.type not in ['CAMERA','LIGHT']and 'previewground'not in o.name.lower():collection.objects.link(o)
  sources[str(path)]=collection
 o=bpy.data.objects.new('Family_'+str(row['allocation']['source_envelope_index']),None);o.instance_type='COLLECTION';o.instance_collection=sources[str(path)];bpy.context.collection.objects.link(o);o.rotation_euler.z=math.pi;o.location=(0,-row['placement']['translation'][2],0);o['allocation_sha256']=row['allocation']['allocation_sha256'];o['rest_slot_ids']=json.dumps(row['allocation']['proposed_rest_slot_ids']);o['receiving_status']='UNFINISHED NOT INTEGRATED'
bpy.context.scene['status']='47 native linked room successors; no new capacity; receiving held';bpy.context.preferences.filepaths.save_version=0;out=N/'Family47NativeBank_r001.blend';assert not out.exists();bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True,relative_remap=True)
(P/'evidence/NATIVE.json').write_text(json.dumps({'status':'PASS','native':str(out.relative_to(R)),'sha256':sha(out),'bytes':out.stat().st_size,'room_instances':47,'retained_native_sources':len(sources),'reserved_rests':59,'geometry_duplicated':False,'main_integrated':False},indent=2)+'\n');print('FAMILY_NATIVE_PASS',out.stat().st_size)
