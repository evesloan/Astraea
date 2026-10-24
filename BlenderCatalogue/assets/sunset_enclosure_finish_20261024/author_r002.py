"""Additive Sunset enclosure profiles, derived from each retained solid wall.

No wall replacement, opening fill, floor, allocation or structural datum change.
Coordinates in PLAN are Godot Y-up; editable Blender geometry is Z-up.
"""
from pathlib import Path
import bpy, json, hashlib, math, struct
from mathutils import Vector
N=Path(__file__).resolve().parent; R=N.parents[2]
P=R/'Game/sunset_enclosure_finish_20261024'
for d in [P/'evidence_r002',P/'runtime']:d.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=R/'BlenderCatalogue/assets/sunset_lift_receiving_20261009/LIFT_GEOMETRY_PLAN.json'
native=R/'BlenderCatalogue/assets/sunset_lift_receiving_20261009/source/architecture_lift_fit.blend'
library=R/'BlenderCatalogue/assets/tidal_court_finish_20261023/TidalCourtSurfaceAndFixtures_r001.blend'
model=R/'Game/assets/models/SUNSET_ARCHITECTURE_lift_r003.glb'
assert sha(native)=='630615777cc9aea3b09910d77471bf4f15d48484f365f917c0f80da6a841da7d'
assert sha(model)=='a6f6646dce45a5cda6b8562be2b0c768c734591021fe1b39c713310c94a7b21f'
assert sha(library)=='5f2a6a8db9922b241a0c7676ced4cf4e5c34ab71d5d7ec9e674e38c8f54d086e'
out=N/'SunsetEnclosure_r002.blend';glb=P/'SunsetEnclosure_r002.glb'
assert not out.exists() and not glb.exists(),'Immutable successor exists'
d=json.loads(source.read_text());bpy.ops.wm.read_factory_settings(use_empty=True)
roles=['ivory_enamel','warm_walnut','champagne_metal','oatmeal_weave']
with bpy.data.libraries.load(str(library),link=False) as(a,b):b.materials=['TidalCourtSurface_r001_'+r for r in roles]
materials={r:bpy.data.materials['TidalCourtSurface_r001_'+r] for r in roles}
lens=bpy.data.materials.new('SunsetEnclosure_Opal');lens.use_nodes=True
bs=lens.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(1,.91,.74,1);bs.inputs['Roughness'].default_value=.55;bs.inputs['Emission Color'].default_value=(1,.85,.61,1);bs.inputs['Emission Strength'].default_value=.5
materials['opal_lens']=lens
parts=[];walls=[];lights=[]
def mesh(name,verts,faces,role,wall,cell,contact=True):
    m=bpy.data.meshes.new(name);m.from_pydata([(x,-z,y)for x,y,z in verts],[],faces);m.update()
    o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);m.materials.append(materials[role])
    # Per-metre planar UVs; the retained native textures remain editable/packed.
    uv=m.uv_layers.new(name='ArchitecturalMetres')
    for poly in m.polygons:
        normal=poly.normal;axis=max(range(3),key=lambda i:abs(normal[i]));axes=[i for i in range(3)if i!=axis]
        for li in poly.loop_indices:
            co=m.vertices[m.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]],co[axes[1]])
    o['role']=role;o['cell']=cell;o['runtime_collision']=contact;o['retained_owner']=wall['source_part'];o['deck']=wall['deck']
    parts.append(dict(name=name,role=role,cell=cell,owner=wall['source_part'],deck=wall['deck'],contact=contact,
                      min=[min(v[i]for v in verts)for i in range(3)],max=[max(v[i]for v in verts)for i in range(3)]))
def point(w,u,y,n):return [w['a'][0]+w['t'][0]*u+w['normal'][0]*n,y,w['a'][1]+w['t'][1]*u+w['normal'][1]*n]
def prism(name,w,u0,u1,y0,y1,n0,n1,role,cell,contact=True):
    verts=[point(w,u,y,n)for n in[n0,n1]for y in[y0,y1]for u in[u0,u1]]
    mesh(name,verts,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],role,w,cell,contact)
def ribbon(name,w,path,width,n0,n1,role,cell):
    verts=[]
    for i,(u,y)in enumerate(path):
        a=path[max(0,i-1)];b=path[min(len(path)-1,i+1)];du,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(du,dy);ox,oy=-dy/length*width/2,du/length*width/2
        for n in[n0,n1]:
            for side in[-1,1]:verts.append(point(w,u+side*ox,y+side*oy,n))
    faces=[(0,1,3,2)]
    for i in range(len(path)-1):
        a=i*4;b=a+4;faces.extend([(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
    a=(len(path)-1)*4;faces.append((a,a+2,a+3,a+1));mesh(name,verts,faces,role,w,cell)
for src in d['parts']:
    if not src['name'].startswith('SC_OuterEnclosure'):continue
    vv=src['verts'];lo=min(v[1]for v in vv);hi=max(v[1]for v in vv);deck=13+round((lo-84)/4.5)
    xs=[v[0]for v in vv];zs=[v[2]for v in vv]
    if src['name'].split('_')[2]=='3':a=[max(xs),min(zs)];b=[max(xs),max(zs)];normal=[1,0]
    elif src['name'].split('_')[2]=='2':a=[min(xs),max(zs)];b=[max(xs),max(zs)];normal=[0,1]
    else:
        # Use the actual interior edge, including the clipped D17 start.
        xz=sorted(set((v[0],v[2])for v in vv));a=list(sorted(xz,key=lambda v:(v[1],-v[0]))[0]);b=list(sorted(xz,key=lambda v:(-v[0],v[1]))[0]);normal=[(b[1]-a[1]),-(b[0]-a[0])];q=math.hypot(*normal);normal=[v/q for v in normal]
    length=math.dist(a,b);t=[(b[i]-a[i])/length for i in range(2)]
    w=dict(source_part=src['name'],a=a,b=b,t=t,normal=normal,y_min=lo,y_max=hi,deck=deck,length=length,maximum_projection_m=.36)
    walls.append(w);count=max(1,round(length/17));bay=length/count
    for j in range(count):
        cell=f"D{deck}_{src['name']}_{j:02d}";u0=j*bay+.40;u1=(j+1)*bay-.40;mid=(u0+u1)/2
        # Broad shallow arch springing from two tapered cheeks, not a false door.
        # All new components are attached directly to retained opaque enclosure.
        path=[(u0,lo+.30),(u0+.09,lo+1.4),(u0+.32,lo+2.6)]
        path += [(u0+.32+(u1-u0-.64)*k/24,lo+2.6+1.22*math.sin(math.pi*k/24))for k in range(1,25)]
        path += [(u1-.09,lo+1.4),(u1,lo+.30)]
        ribbon(cell+'_SculptedArch',w,path,.23,.015,.24,'ivory_enamel',cell)
        crown=[(u0+.45+(u1-u0-.9)*k/24,lo+2.64+1.08*math.sin(math.pi*k/24))for k in range(25)]
        ribbon(cell+'_WalnutInnerReveal',w,crown,.13,.02,.17,'warm_walnut',cell)
        ribbon(cell+'_BronzeShadowLine',w,[(u,y-.12)for u,y in crown],.025,.03,.12,'champagne_metal',cell)
        # Alternating broad absorbent reliefs, set within the wall-side reveal.
        width=(u1-u0)*(.48 if j%3==0 else .38)
        prism(cell+'_TextileRelief',w,mid-width/2,mid+width/2,lo+.65,lo+2.35,.005,.045,'oatmeal_weave',cell)
        prism(cell+'_LowWallPlinth',w,u0,u1,lo+.10,lo+.24,.01,.16,'warm_walnut',cell)
        if j%2==0:
            prism(cell+'_FixtureBack',w,mid-.45,mid+.45,lo+3.35,lo+3.58,.02,.26,'champagne_metal',cell)
            prism(cell+'_OpalLens',w,mid-.35,mid+.35,lo+3.38,lo+3.53,.26,.28,'opal_lens',cell,False)
            pos=point(w,mid,lo+3.44,.31);target=point(w,mid,lo+1.2,13)
            lights.append(dict(name=cell+'_CourtWash',position=pos,target=target,range=25,energy=1.4,angle=68,attenuation=.8,color=[1,.92,.78],source_fixture=cell+'_OpalLens',deck=deck))
    # Cornice follows this exact solid section; no span across D17 openings.
    prism(src['name']+'_UpperSoffit',w,.20,length-.20,hi-.24,hi-.10,.01,.36,'warm_walnut',f'D{deck}_{src["name"]}_cornice')
    prism(src['name']+'_CrownLip',w,.20,length-.20,hi-.10,hi-.03,.015,.20,'ivory_enamel',f'D{deck}_{src["name"]}_cornice')
for row in lights:
    data=bpy.data.lights.new(row['name'],'SPOT');data.energy=120;data.color=row['color'];data.spot_size=math.radians(row['angle']*2);data.spot_blend=.55
    o=bpy.data.objects.new(row['name'],data);bpy.context.scene.collection.objects.link(o);x,y,z=row['position'];o.location=(x,-z,y);tx,ty,tz=row['target'];o.rotation_euler=(Vector((tx,-tz,ty))-o.location).to_track_quat('-Z','Y').to_euler();o['runtime_parameters']=json.dumps(row)
for im in bpy.data.images:
    if im.source=='FILE'and not im.packed_file:im.pack()
bpy.context.scene['status']='UNFINISHED additive enclosure, original wall/roof/hull remains external immutable owner'
bpy.context.scene['preserved_programme']='83 ordinary homes;47 specialty allocations;59 rest identities;133 original landscape placements'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:o.select_set(o.type=='MESH')
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
raw=model.read_bytes();size=struct.unpack_from('<I',raw,12)[0];gltf=json.loads(raw[20:20+size]);assign=[]
for node in gltf['nodes']:
    e=node.get('extras',{});cat=e.get('category');role=e.get('role');name=node.get('name','')
    if 'mesh'not in node:continue
    if (cat=='enclosure'and name!='SC_Batch_316')or name=='SC_Batch_282'or cat in ['ceiling_rib','pier']:
        accessor=gltf['accessors'][gltf['meshes'][node['mesh']]['primitives'][0]['attributes']['POSITION']]
        assign.append(dict(node=name,role=role,category=cat,min=accessor['min'],max=accessor['max']))
plan=dict(status='UNFINISHED_SOURCE_CANDIDATE',parent_commit='913609a143d191b5fde3348cc3350280f8b9694c',source_plan=str(source.relative_to(R)),source_plan_sha256=sha(source),source_extras_plan_sha256='0df22f142f909c6bd1910e3681450e828147f63d59574c437119322ebd85b112',native_source=str(native.relative_to(R)),native_source_sha256=sha(native),model='res://assets/models/SUNSET_ARCHITECTURE_lift_r003.glb',model_sha256=sha(model),material_library=str(library.relative_to(R)),material_library_sha256=sha(library),parts=parts,walls=walls,lights=lights,surface_assignments=assign,glb_sha256=sha(glb),native_sha256=sha(out),selector_budget=8,new_floor_or_cut=False,new_capacity=0,ordinary_homes=83,specialty_allocations=47,rest_ids=59,retained_landscape=133,camera_exposure_changed=False,references=['Pixel-reviewed master image6 and image11','Master chapters21 and32; original Sunset solid-section boundaries'])
(P/'PLAN_r002.json').write_text(json.dumps(plan,indent=2)+'\n');(P/'evidence_r002/NATIVE.json').write_text(json.dumps(dict(parts=len(parts),wall_sections=len(walls),source_mounted_emitters=len(lights),surface_assignments=len(assign),native_bytes=out.stat().st_size,glb_bytes=glb.stat().st_size,native_sha256=sha(out),glb_sha256=sha(glb),status='NATIVE_EXPORT_ONLY'),indent=2)+'\n')
print('SUNSET_ENCLOSURE_NATIVE',len(parts),len(walls),len(lights),glb.stat().st_size)
