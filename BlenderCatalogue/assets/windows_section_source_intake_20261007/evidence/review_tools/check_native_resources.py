"""Receiving-side resource closure. Read-only native/GLB; isolated QA output only."""
import bpy,json,struct,hashlib,sys,argparse
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--package',required=True);ap.add_argument('--native',required=True);ap.add_argument('--glb',required=True);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
P=Path(a.package).resolve();BASE=Path(__file__).resolve().parents[1];assert P.is_relative_to(BASE)
def inside(rel):
 p=(P/rel).resolve();assert p.is_relative_to(P);return p
native=inside(a.native);export=inside(a.glb);before=hashlib.sha256(native.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(native))
images=[]
for i in bpy.data.images:
 if i.type!='IMAGE':continue
 packed=bool(i.packed_file);data=bytes(i.packed_file.data) if packed else b'';was_loaded=bool(i.has_data)
 first=list(i.pixels[:4]) if packed else [];size=list(i.size)
 images.append({'name':i.name,'source':i.source,'packed':packed,'packed_bytes':len(data),'packed_sha256':hashlib.sha256(data).hexdigest() if data else None,'size':size,'loaded_before_decode':was_loaded,'loaded_after_decode':bool(i.has_data),'first_pixel':first})
bad=[r for r in images if not r['packed'] or not r['packed_bytes'] or not r['loaded_after_decode'] or min(r['size'])<=0 or len(r['first_pixel'])!=4]
raw=export.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);names={o.get('name') for o in g['nodes'] if 'mesh' in o};fonts=[o.name for o in bpy.context.scene.objects if o.type=='FONT'];missing=sorted(set(fonts)-names)
external_images=[r for r in g.get('images',[]) if 'uri' in r and not r['uri'].startswith('data:')];external_buffers=[r for r in g.get('buffers',[]) if 'uri' in r and not r['uri'].startswith('data:')]
checks={'native_images_present':bool(images),'all_native_images_packed_and_decodable':not bad,'no_native_external_libraries':len(bpy.data.libraries)==0,'export_images_present':bool(g.get('images')),'export_resources_embedded':not external_images and not external_buffers,'all_native_authored_fonts_in_export':not missing,'native_bytes_unchanged':before==hashlib.sha256(native.read_bytes()).hexdigest()}
r={'scope':'Fresh native reopen and packed pixel decoding; exported resource/sign-name closure. No visual, physics or load acceptance.','checks':checks,'pass':all(checks.values()),'native_sha256':before,'glb_sha256':hashlib.sha256(raw).hexdigest(),'images':images,'bad_images':bad,'external_libraries':[l.filepath for l in bpy.data.libraries],'export_embedded_images':len(g.get('images',[])),'export_punctual_lights':len(g.get('extensions',{}).get('KHR_lights_punctual',{}).get('lights',[])),'native_fonts':fonts,'missing_export_fonts':missing,'external_images':external_images,'external_buffers':external_buffers}
out=inside('qa/receiving_source_review/NATIVE_RESOURCE_CLOSURE.json');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='images'}));assert r['pass']
