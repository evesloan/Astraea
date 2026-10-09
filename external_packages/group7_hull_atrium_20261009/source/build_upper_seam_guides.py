"""Editable proposal guides only. Never install these as architecture/collision."""
import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];plan=json.loads((P/'docs/UPPER_PERIMETER_AND_TERMINAL_PROPOSALS.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
m=bpy.data.materials.new('G7 proposal amber');m.diffuse_color=(.9,.42,.08,1)
def guide(name,points,closed=True):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=.018;c.bevel_resolution=0;s=c.splines.new('POLY');s.points.add(len(points)-1)
 for q,v in zip(s.points,points):q.co=(v[0],-v[2],v[1],1)
 s.use_cyclic_u=closed;o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);c.materials.append(m);o['proposal_only']=True;o['collision']=False;o['architecture_installed']=False
for r in plan['rings']:guide(r['id'],[(x,r['datum_y'],z) for x,z in r['proposal_outer_contour_xz']])
for r in plan['private_pavilion_boundary_targets']:
 guide('OWNER_HELD_'+r['identity'],[(x,106.5,z) for x,z in r['outer_miter_polygon']]);guide('OWNER_HELD_ROOF_LIMIT_'+r['identity'],[(x,r['roof_limit'],z) for x,z in r['outer_miter_polygon']])
guide('Retained_AST_RES006_outer_side_target',[(119.5,102,28.2),(119.5,102,51.88),(119.5,106.3,51.88),(119.5,106.3,28.2)])
native=P/'source/natives/G7_UpperSeamProposals_r001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native))
for o in list(bpy.context.scene.objects):
 if o.type=='CURVE':
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
folder=P/'exports/proposals';folder.mkdir(exist_ok=True);f=folder/'G7_UpperSeamGuides_NOT_FOR_RUNTIME.glb';bpy.ops.export_scene.gltf(filepath=str(f),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
(P/'qa/upper_seam_guide_receipt.json').write_text(json.dumps({'source':native.relative_to(P).as_posix(),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'export':f.relative_to(P).as_posix(),'export_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'guide_objects':len(bpy.context.scene.objects),'runtime_adoption':False,'scope':'Visual/editable coordinate guide for reversible proposals. No architectural pressure walls, roof skins, supports, floors or accepted loft supplied. Do not register collision or install this GLB in Game.'},indent=2)+'\n');print('UPPER_SEAM_GUIDES',len(bpy.context.scene.objects))
