"""AST-ENG-008: pure geometry plan; optional Blender execution only under parent slot.
World XYZ is Godot metres. Blender maps (x,y,z) -> (x,-z,y).
Never reads or writes another asset; never changes catalogue registry.
"""
from pathlib import Path
import json, math, hashlib, argparse, sys
R=Path(__file__).resolve().parents[1]; C=R.parents[1]
P=Path('/workspace/shared/astraea-godot-production-20261003')
parts=[]; markers=[];doors=[]
def mesh(n,v,f,role='staff_white_paint',kind='static_architecture',preview=False):
    parts.append(dict(name=n,vertices_xyz=v,faces=f,material_role=role,kind=kind,export=not preview,collision='none' if preview or kind in ['lens'] else 'static_surface'))
def box(n,x0,x1,y0,y1,z0,z1,role='staff_white_paint',kind='static_architecture',preview=False):
    assert x1>x0 and y1>y0 and z1>z0,n
    mesh(n,[(x,y,z) for y in [y0,y1] for x,z in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,kind,preview)
def beam(n,a,b,width,height,role='staff_white_paint'):
    dx=b[0]-a[0];dz=b[2]-a[2];l=math.hypot(dx,dz);nx=-dz/l*width/2;nz=dx/l*width/2
    v=[(p[0]+s*nx,p[1]+h,p[2]+s*nz) for h in [-height/2,height/2] for p,s in [(a,-1),(b,-1),(b,1),(a,1)]]
    mesh(n,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role)
def slab(n,poly,y0,y1,preview=False):
    N=len(poly);mesh(n,[(x,y,z) for y in [y0,y1] for x,z in poly],[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],'staff_bluegrey_paint',preview=preview)
def axiswall(n,axis,plane,lo,hi,y1=9.6,opening=None,glass=False,t=.18):
    def piece(s,a,b,ya,yb,role,kind='static_architecture'):
        if axis=='x':box(n+s,plane-t/2,plane+t/2,ya,yb,a,b,role,kind)
        else:box(n+s,a,b,ya,yb,plane-t/2,plane+t/2,role,kind)
    cuts=[lo,hi]
    if opening:
        cuts += list(opening);doors.append(dict(id=n+'_aperture',axis=axis,plane=plane,range=opening,floor_y=6,clear_height=2.7,leaf_owner='future runtime dynamic door; no leaf mesh exported',hinge_sweep='none: reserved sliding pocket outside cart clearance',threshold_floor_owner='compiler D02_directory_02',ramp='none; level Y6'))
    for i,(a,b) in enumerate(zip(sorted(set(cuts)),sorted(set(cuts))[1:])):
        if opening and opening[0]<=(a+b)/2<=opening[1]:piece('_header',a,b,8.7,y1,'staff_bluegrey_paint');continue
        if glass:piece('_sill'+str(i),a,b,6,7.0,'staff_bluegrey_paint');piece('_glass'+str(i),a,b,7.0,y1-.25,'section_sealed_glass','glazing');piece('_head'+str(i),a,b,y1-.25,y1,'staff_white_paint')
        else:piece('_wall'+str(i),a,b,6,y1,'staff_white_paint')
def room(n,x0,x1,z0,z1,ceiling,doorface,doorcenter):
    for axis,plane,lo,hi,face in [('x',x0,z0,z1,'west'),('x',x1,z0,z1,'east'),('z',z0,x0,x1,'north'),('z',z1,x0,x1,'south')]:
        axiswall(n+'_'+face,axis,plane+(.09 if face in ['west','north'] else -.09),lo,hi,ceiling,(doorcenter-1.2,doorcenter+1.2) if face==doorface else None,glass=n=='control' and face=='south')
    slab(n+'_ceiling',[(x0,z0),(x1,z0),(x1,z1),(x0,z1)],ceiling,ceiling+.15)
def fixture(n,x,y,z):
    box(n+'_mount',x-.75,x+.75,y+.06,y+.16,z-.18,z+.18,'staff_zinc')
    box(n+'_housing',x-.65,x+.65,y-.05,y+.06,z-.14,z+.14,'staff_bluegrey_paint')
    box(n+'_opal',x-.55,x+.55,y-.075,y-.05,z-.10,z+.10,'staff_opal','lens')
    ceiling=9.3 if n=='control_task' else (9.6 if n in ['entry','workbay_task'] else (11.1 if n=='isolation_task' else 9.9))
    if ceiling>y+.16:box(n+'_ceiling_stem',x-.035,x+.035,y+.16,ceiling,z-.035,z+.035,'staff_zinc')
    markers.append(dict(name='DATUM_'+n,position_xyz=[x,y-.075,z],housing=n+'_housing',support=n+'_mount',purpose=n))
def axial(n,rings,role):
    N=24;v=[(34.5+x,8.05+r*math.sin(2*math.pi*i/N),-432+r*math.cos(2*math.pi*i/N)) for x,r in rings for i in range(N)]
    mesh(n,v,[tuple(reversed(range(N))),tuple(range((len(rings)-1)*N,len(rings)*N))]+[(j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for j in range(len(rings)-1) for i in range(N)],role,'fictional_contained_machine')
def build():
    hall=[(21,-445),(27,-451),(41.7,-451),(47.7,-445),(47.7,-419),(41.7,-413),(27,-413),(21,-419)]
    # Hall bearing ribs are independent of glazing; no slab exports.
    for i,(a,b) in enumerate(zip(hall,hall[1:]+hall[:1])):
        if a[0]==b[0]:axiswall('hall_face_'+str(i),'x',a[0],min(a[1],b[1]),max(a[1],b[1]),11.1,(-433.8,-430.2) if a[0]==47.7 else None,glass=a[0]==21)
        elif a[1]==b[1]:axiswall('hall_face_'+str(i),'z',a[1]+(.09 if a[1]==-451 else -.09),min(a[0],b[0]),max(a[0],b[0]),11.1,(36.8,39.2),glass=a[1]==-451)
        else:
            length=math.hypot(b[0]-a[0],b[1]-a[1]);ox=-(b[1]-a[1])/length*.12;oz=(b[0]-a[0])/length*.12
            beam('hall_facet_'+str(i),(a[0]+ox,8.55,a[1]+oz),(b[0]+ox,8.55,b[1]+oz),.24,5.1)
        box('hall_bearing_'+str(i),a[0]-.18,a[0]+.18,6,11.52,max(a[1]-.18,-451),min(a[1]+.18,-413),'staff_bluegrey_paint')
    slab('hall_faceted_soffit',hall,11.1,11.52)
    # Programme boundary reserve. Exact service handoffs stop at X54.
    axiswall('boundary_west','x',8.15,-465.7,-398.3,9.6,(-433.8,-430.2))
    axiswall('boundary_east','x',53.85,-465.7,-398.3,9.6,(-433.2,-430.8))
    # Second exit explicitly cut separately, rather than hidden behind wall.
    parts[:]=[p for p in parts if not p['name'].startswith('boundary_east')];doors[:]=[d for d in doors if d['id']!='boundary_east_aperture']
    axiswall('boundary_east_n','x',53.85,-465.7,-405.2,9.6,(-433.2,-430.8))
    axiswall('boundary_east_s','x',53.85,-405.2,-398.3,9.6,(-405.2,-402.8))
    for z in [-465.85,-398.15]:axiswall('boundary_end_'+str(z),'z',z,8.3,53.7)
    room('visitor',8.4,17,-447,-417,9.6,'west',-432)
    # Recut visitor west side to match 3.6m receiving aperture.
    parts[:]=[p for p in parts if not p['name'].startswith('visitor_west')];doors[:]=[d for d in doors if d['id']!='visitor_west_aperture'];axiswall('visitor_west','x',8.4,-447,-417,9.6,(-433.8,-430.2))
    parts[:]=[p for p in parts if not p['name'].startswith('visitor_east')];axiswall('visitor_view','x',17,-447,-417,9.6,glass=True)
    # Controlled opaque dogleg is programme-local and deliberately inaccessible to visitors.
    axiswall('transfer_north','z',-440,17,21,9.2);axiswall('transfer_south','z',-424,17,21,9.2)
    axiswall('transfer_return','x',19,-440,-436,9.2)
    room('control',20,34,-464,-454.6,9.3,'south',30)
    room('technical_staging',35,47,-464,-454.6,9.3,'south',40)
    room('workbay',20,34,-409.4,-400,9.6,'north',30)
    room('clean_returns',35,47,-409.4,-400,9.3,'north',40)
    # Seal only the fictional machine enclosure; external ring remains usable.
    for axis,plane,lo,hi in [('x',25,-441,-423),('x',44,-441,-423),('z',-441,25,44),('z',-423,25,44)]:axiswall('containment_'+str(plane),axis,plane,lo,hi,10.6,glass=True,t=.12)
    slab('containment_cap',[(25,-441),(44,-441),(44,-423),(25,-423)],10.48,10.6)
    axial('machine_contained_sleeve',[(-4.4,1.35),(-3.7,1.48),(3.7,1.48),(4.4,1.35)],'staff_bluegrey_paint')
    for side in [-1,1]:
        r=[(side*x,y) for x,y in [(3.7,1.52),(4,1.73),(5.8,1.73),(6.5,1.42),(7.8,1.12),(8.15,.8),(8.28,.65)]]
        axial('machine_profiled_end_'+str(side),r if side==1 else list(reversed(r)),'staff_white_paint')
    for i,x in enumerate([-3.5,-2.1,-.7,.7,2.1,3.5]):axial('machine_induction_band_'+str(i),[(x-.09,1.57),(x,1.66),(x+.09,1.57)],'staff_zinc')
    for x in [29,40]:
        for z in [-434,-430]:box('plant_bearing_leg_'+str(x)+str(z),x-.18,x+.18,6,10.4,z-.18,z+.18,'staff_bluegrey_paint');box('bearing_pad_'+str(x)+str(z),x-.35,x+.35,6,6.24,z-.35,z+.35,'staff_zinc')
        for z in [-433,-431]:box('suspension_yoke_link_'+str(x)+str(z),x-.12,x+.12,9.35,10.4,z-.09,z+.09,'staff_zinc')
        box('bearing_crossmember_'+str(x),x-.2,x+.2,10.26,10.6,-434.2,-429.8,'staff_white_paint')
    for z in [-433.45,-430.55]:beam('supported_manifold_'+str(z),(28.5,8.8,z),(40.5,8.8,z),.14,.14,'staff_zinc')
    # Purpose-required furniture only; protected floor routes remain empty.
    for x in [23,26,29]:box('control_console_'+str(x),x-.9,x+.9,6,7.05,-463.2,-462.4,'staff_bluegrey_paint');box('control_display_'+str(x),x-.65,x+.65,7.05,7.65,-463.1,-462.95,'staff_zinc')
    for n,x,z in [('spares',36,-462.5),('quarantine',44,-462.5),('consumables',36,-401.5),('bagged_returns',44,-401.5)]:box(n+'_closed_cabinet',x-.6,x+.6,6,8.2,z-.65,z+.65,'staff_white_paint')
    box('maintenance_bench',21,27,6,6.9,-402,-400.7,'staff_bluegrey_paint');box('bench_supported_instrument',22,23,6.9,7.45,-401.8,-401.0,'staff_zinc')
    box('isolation_face',35,37,6,7.6,-441.4,-441.15,'staff_bluegrey_paint')
    box('visitor_pause_bench',9,10,6,6.48,-426,-422,'staff_white_paint')
    for n,p in [('entry',(12,9.35,-432)),('control_task',(26,9.0,-459)),('service_entry',(51,9.675,-432)),('workbay_task',(27,9.3,-405)),('isolation_task',(36,9.3,-443)),('cart_north',(51,9.675,-453)),('cart_south',(51,9.675,-411))]:fixture(n,*p)
    slab('east_street_ceiling',[(48.3,-465.7),(53.7,-465.7),(53.7,-398.3),(48.3,-398.3)],9.9,10.05)
    # Short overhead service supports anchor fixtures without low-hanging hazards.
    for z in [-453,-432,-411]:box('street_overhead_support_'+str(z),48.3,53.7,9.85,9.9,z-.12,z+.12,'staff_zinc')
    slab('PREVIEW_COMPILER_D02_FLOOR',[(8,-466),(54,-466),(54,-398),(8,-398)],5.76,6,True)
    slab('PREVIEW_COMPILER_D03_OPAQUE_CAP',[(8,-466),(54,-466),(54,-398),(8,-398)],11.76,12,True)
    return hall

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--blender',action='store_true');args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None);hall=build()
    contract=dict(catalogue_id='AST-ENG-008',registration='reserved only',stage='editable generator and pure geometry only; no engine/source-export acceptance',programme='D02_directory_02',world_bounds=[8,54,6,11.52,-466,-398],hall_polygon_xz=hall,rooms=dict(control=[20,34,-464,-454.6],technical_staging=[35,47,-464,-454.6],workbay=[20,34,-409.4,-400],clean_returns=[35,47,-409.4,-400]),local_dimensional_adjustment='Parent approved 0.6m room-depth reduction at 2026-10-06: north room outer edge -454.6, south room outer edge -409.4; service-facing wall thickness inset to rooms and hall; 3.6m is true face-to-face corridor clearance',floor_ownership=dict(compiler='single Y6 slab and opaque Y12 cap; preview-only objects excluded from export and collision',source='walls, ceilings, equipment bearing pads; no walkable slabs',door='clear empty apertures, runtime door leaves deferred',ramp='none: all circulation level Y6',visitor_connection='X0..8 unresolved; nothing built outside allocation',service_connection='handoff X54 at Z-432 and -404 only; external street not authored'),clearance=dict(east_street_x=[48.3,53.7],east_street_width=5.4,minimum_through_width=3.6,north_strip_z=[-454.6,-451],south_strip_z=[-413,-409.4],core_reservation=[25,44,6,10.6,-441,-423],module_xyz=[1.8,1.8,1.4],loaded_height=2.15,door_clear=[2.4,2.7],whole_machine_removal=False),doors=doors,fixtures=markers,fictional_machine='Purpose-built low-profile contained assembly with profiled end housings, induction bands, supported manifold spines and independent bearings; no operating reactor or physical engineering claim',evidence=dict(reference='technical_reference.png ASW-GV-04 native image inspected; paired core/control/service separation and supported machinery implemented; tall multi-storey silhouette explicitly not retained',source_sha256={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [P/'data/architecture/packages/engineering/MACHINE_SECTION_FIT.json',P/'data/architecture/packages/engineering/DETAILED_SERVICE_ROUTE_FIT.json',P/'data/architecture/packages/engineering/SECONDARY_FUSION_SECTION_SPEC.json']}),unfinished=['dynamic door leaves and exact pockets','live capsule and loaded-cart checks','species fit','control function','plant operation','visitor external floor handoff','second control and shipwide service routes','visual acceptance'])
    surface_rows=[]
    for p in parts:
        mins=[min(v[i] for v in p['vertices_xyz']) for i in range(3)];maxs=[max(v[i] for v in p['vertices_xyz']) for i in range(3)]
        surface_rows.append(dict(name=p['name'],aabb_xyz_min_max=mins+maxs,export=p['export'],collision=p['collision'],material_role=p['material_role'],kind=p['kind'],floor_contact_owner='compiler D02_directory_02 Y6' if p['export'] and abs(mins[1]-6)<1e-6 else None,walkable_floor=False))
    (R/'source/surface_manifest.json').write_text(json.dumps(dict(catalogue_id='AST-ENG-008',coordinate_system='world Godot XYZ metres; Blender x,-z,y',source_surfaces=surface_rows,door_and_threshold_owner=contract['floor_ownership']),indent=2)+'\n')
    (R/'source/section_contract.json').write_text(json.dumps(contract,indent=2)+'\n');(R/'source/geometry_plan.json').write_text(json.dumps(dict(parts=parts,markers=markers),indent=2)+'\n')
    if args.blender:blender()

def blender():
    import bpy,bmesh,sys
    from mathutils import Vector
    sys.path.insert(0,str(C/'standards'));import staff_materials
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    mats=staff_materials.materials();m=bpy.data.materials.new('section_sealed_glass');m.diffuse_color=(.12,.28,.32,.24);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.12,.28,.32,1);bs.inputs['Transmission Weight'].default_value=.65;bs.inputs['Roughness'].default_value=.22;mats['section_sealed_glass']=m
    for p in parts:
        me=bpy.data.meshes.new(p['name']);me.from_pydata([(x,-z,y) for x,y,z in p['vertices_xyz']],[],p['faces']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(p['name'],me);bpy.context.collection.objects.link(o);me.materials.append(mats[p['material_role']]);o['catalogue_id']='AST-ENG-008';o['collision_contract']=p['collision'];o['preview_only']=not p['export']
        uv=me.uv_layers.new(name='MetreScaled')
        for f in me.polygons:
            n=f.normal.normalized();u=Vector((1,0,0)) if abs(n.x)<.7 else Vector((0,1,0));u=(u-n*u.dot(n)).normalized();v=n.cross(u)
            for li in f.loop_indices:
                q=me.vertices[me.loops[li].vertex_index].co;tile=mats[p['material_role']].get('meters_per_tile_uv',[1,1]);uv.data[li].uv=(q.dot(u)/tile[0],q.dot(v)/tile[1])
    for d in markers:
        o=bpy.data.objects.new(d['name'],None);bpy.context.collection.objects.link(o);x,y,z=d['position_xyz'];o.location=(x,-z,y);o['housing']=d['housing']
    bpy.context.scene.unit_settings.system='METRIC';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/AST-ENG-008.blend'))
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.context.scene.objects:
        if not o.get('preview_only',False):o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(R/'exports/AST-ENG-008.glb'),export_format='GLB',export_yup=True,export_extras=True,use_selection=True)
if __name__=='__main__':main()
