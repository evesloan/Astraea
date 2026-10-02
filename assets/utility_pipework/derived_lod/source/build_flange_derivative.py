"""Run Blender -b -t 1 --python this file; saves only derived_lod outputs."""
import bpy,bmesh,json,hashlib,importlib.util,math
from pathlib import Path
from mathutils import Vector,Matrix
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[2]
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
p=load('ports',CAT/'standards/utility_ports.py');lod=load('economical',BASE/'source/utility_flange_economical.py');mats=load('staff_materials',CAT/'standards/staff_materials.py').materials()
def reset():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1

def export(obs,path):
 groups={}
 for o in obs:groups.setdefault(o['material_role'],[]).append(o)
 for role,group in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in group:o.select_set(True)
  bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();o=bpy.context.object;o.name=path.stem+'__'+role;p.metric_uv(o,o.data.materials[0])
 bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)

def save(obs,name,records):
 rows=[]
 for o in obs:
  me=o.data;me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me)
  rows.append({'name':o.name,'vertices':len(me.vertices),'triangles':len(me.loop_triangles),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'uv_layer':me.uv_layers.active.name,'material_role':o['material_role'],'modifiers':len(o.modifiers)});bm.free()
 scene=bpy.context.scene;scene['derivative_revision']=lod.REVISION;scene['scope']='Bounded economical flange derivative and inspection fixture only; not a new artistic design or game integration';scene['source_frame']='Blender Z-up metres';scene['exchange_frame']='GLB Y-up, (x,y,z) -> (x,z,-y)'
 bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source'/f'{name}.blend'),compress=True)
 export(obs,BASE/'exports'/f'{name}.glb')
 return {'name':name,'source_parts':rows,'source_triangle_count':sum(r['triangles']for r in rows),'source_all_parts_closed':all(r['nonmanifold_edges']==0 for r in rows),'ports':records}

def main():
 for directory in ('source','exports','qa'):
  (BASE/directory).mkdir(parents=True,exist_ok=True)
 bpy.context.preferences.filepaths.save_version=0
 reset();row=lod.add_flange('INLET',(0,0,0),(-1,0,0),mats,hole_segments=24);p.add_port_marker('INLET',(0,0,0),(-1,0,0),row['record']);baseline=save(row['objects'],'utility_flange_exact_profile_baseline',[row['record']])
 reset();row=lod.add_flange('INLET',(0,0,0),(-1,0,0),mats);p.add_port_marker('INLET',(0,0,0),(-1,0,0),row['record']);result=[baseline,save(row['objects'],'utility_flange_economical',[row['record']])]
 # Six actual opposed flange pairs at a nonzero source height; no visual proxy.
 # Each isolated pair has 0.035 m of flange on either side of its seam. Hollow
 # pipe segments connect the pairs; caps and supports are omitted QA context.
 reset();objects=[];records=[]
 for i in range(6):
  face=(0,i*.8,.7)
  for side,n in [('A',(0,-1,0)),('B',(0,1,0))]:
   name=f'PAIR_{i+1}_{side}';row=lod.add_flange(name,face,n,mats);objects+=row['objects'];records.append(row['record']);p.add_port_marker(name,face,n,row['record'])
 for i in range(5):objects.append(p.annular('QA_CONTEXT_hollow_link_'+str(i),(0,i*.8,.7),(0,1,0),[(.085,.08,.1),(.715,.08,.1)],mats['staff_bluegrey_paint'],48))
 result.append(save(objects,'utility_flange_repeated_context',records))
 (BASE/'qa/source_geometry.json').write_text(json.dumps({'revision':lod.REVISION,'results':result},indent=2)+'\n')
 print('FLANGE_DERIVATIVE_COMPLETE',[(r['name'],r['source_triangle_count'])for r in result])
if __name__=='__main__':main()
