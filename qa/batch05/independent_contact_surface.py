"""Actual final GLB contact-surface/support separation after breakthrough correction."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch05';p=ROOT/'assets/aquatic_lounge/exports/AST-AQU-001.glb'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p));g={}
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 m=o.data;m.calc_loop_triangles();vs=[o.matrix_world@v.co for v in m.vertices];fs=[tuple(t.vertices) for t in m.loop_triangles];role=o.data.materials[0].name;g[role]=BVHTree.FromPolygons(vs,fs,all_triangles=True)
rows=[]
for y in [-.9,-.54,-.13,.25,.58,.85]:
 for x in [-.16,.055,.16]:
  st=Vector((x,y,1.5));d=Vector((0,0,-1));clay=g['ASTRAEA_aquatic_clay_sling'].ray_cast(st,d)[0];metal=g['ASTRAEA_aquatic_satin_alloy'].ray_cast(st,d)[0]
  rows.append({'xy_m':[x,y],'clay_z_m':clay.z if clay else None,'metal_z_m':metal.z if metal else None,'clay_above_metal_m':clay.z-metal.z if clay and metal else None})
out={'glb_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scope':'Actual exported visual meshes, finite downward sample rays; this does not prove comfort, collision, load or universal actor contact.','samples':rows,'all_sampled_supports_below_clay':all(r['clay_above_metal_m'] is not None and r['clay_above_metal_m']>0 for r in rows),'minimum_separation_m':min(r['clay_above_metal_m'] for r in rows if r['clay_above_metal_m'] is not None)}
(OUT/'independent_contact_surface.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
