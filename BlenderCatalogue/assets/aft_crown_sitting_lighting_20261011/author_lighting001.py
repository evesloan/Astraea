from pathlib import Path
import bpy,json,hashlib,sys,math
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
catalog=json.load(open(R/'BlenderCatalogue/catalogue_manifest.json'));registered=[q for q in catalog['assets']if q.get('catalogue_id')=='AST-LGT-001'];assert len(registered)==1 and registered[0]['source']=='assets/hospitality_lantern/source/AST-LGT-001.blend'
assert not any(P['structure_file']in str(q)for q in catalog['assets'])
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(R/P['source_native']),link=False)as(src,dst):dst.objects=src.objects
original=[]
for o in dst.objects:
 if o:bpy.context.collection.objects.link(o);original.append(o)
bpy.context.view_layer.update();source=[o for o in original if o.type=='MESH'];assert len(source)==8
rows=[]
for q in P['fixture_instances']:
 T=Matrix.Translation(Vector((q['origin'][0],-q['origin'][2],q['origin'][1])))@Matrix.Rotation(q['yaw'],4,'Z')
 for orig in source:
  o=orig.copy();o.data=orig.data.copy();o.parent=None;o.name=q['name']+'__'+orig.name;o.matrix_world=T@orig.matrix_world;bpy.context.collection.objects.link(o);o['category']='light_source'if 'OpalDiffuser'in orig.name else'fixture_housing';o['role']='source_lantern';o['runtime_collision']=False
  # Fixtures are wholly above the worker/cart envelope;mounts retain physical contact.
  rows.append({'name':o.name,'source_name':orig.name,'placement':q,'source_matrix':[list(v)for v in orig.matrix_world]})
 lo,hi=q['mount_bounds'];center=[(a+b)/2 for a,b in zip(lo,hi)];size=[b-a for a,b in zip(lo,hi)];bpy.ops.mesh.primitive_cube_add(size=1,location=(center[0],-center[2],center[1]));o=bpy.context.object;o.name=q['name']+'__PierMount';o.dimensions=(size[0],size[2],size[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(next(m for a in source for m in a.data.materials if m.name=='champagne_metal'));b=o.modifiers.new('Original_material_mount_edge','BEVEL');b.width=.012;b.segments=2;o['category']='fixture_mount';o['role']='source_lantern_mount';o['runtime_collision']=True
 marker=bpy.data.objects.new(q['name']+'__LightExit',None);bpy.context.collection.objects.link(marker);marker.location=(q['emitter'][0],-q['emitter'][2],q['emitter'][1]);marker['fixture_origin_source']='AST-LGT-001/DATUM_light_exit'
for o in original:bpy.data.objects.remove(o,do_unlink=True)
sys.path.insert(0,str(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011'));from immutable_revision import export_native
rec=export_native(bpy,W,R,'AftCrownSittingLighting_r001.blend',P['structure_file']);P['structure']=rec;P['model_pins']={rec['export']:rec['export_sha256']};P['fixture_meshes']=rows
for f,h in P['protected_native_exports'].items():assert sha(R/f)==h,f
for f in [W/'PLAN.json',R/'Game/data/architecture/AFT_CROWN_SITTING_LIGHTING.json']:f.write_text(json.dumps(P,indent=2)+'\n')
print('PASS_NEW_IMMUTABLE_SOURCE',len(rows),'rigid original fixture meshes',rec['mesh_count'],'total meshes')
