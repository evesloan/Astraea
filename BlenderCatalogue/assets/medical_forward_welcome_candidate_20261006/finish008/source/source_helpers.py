def world(p):return [p[0]-28,p[2]+21,-p[1]-446]

def mesh(name,verts,faces,role,bevel=0):
    if name.startswith('WAIT_'):
        verts=[(max(0,min(14,v[0])),max(-4,min(4,v[1])),v[2]) for v in verts]
    me=bpy.data.meshes.new(name+'_editable');me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);SCENE.collection.objects.link(ob);me.materials.append(MATS[role]);ob['source_package']='D05_forward_welcome_candidate';ob['material_role']=role
    uv=me.uv_layers.new(name='MetreScaled');scale=MATS[role]['metres_per_tile']
    for f in me.polygons:
        a=max(range(3),key=lambda i:abs(f.normal[i]));axes=[i for i in range(3) if i!=a]
        for li in f.loop_indices:
            p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]/scale,p[axes[1]]/scale)
    if bevel:
        spans=[max(v[i] for v in verts)-min(v[i] for v in verts) for i in range(3)]
        m=ob.modifiers.new('Editable eased use edges','BEVEL');m.width=min(bevel,min(spans)*.24);m.segments=2;m.limit_method='ANGLE'
        m=ob.modifiers.new('Editable weighted normals','WEIGHTED_NORMAL');m.keep_sharp=True
    PARTS.append(ob);return ob

def box(name,x0,x1,y0,y1,z0,z1,role='quiet_ivory',bevel=.015):
    return mesh(name,[(x,y,z) for z in [z0,z1] for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel)

def prism(name,poly,z0,z1,role='quiet_ivory',bevel=.012):
    n=len(poly);return mesh(name,[(x,y,z) for z in [z0,z1] for x,y in poly],[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],role,bevel)

def strip(name,points,width,z0,z1,role='quiet_ivory',bevel=.01):
    left=[];right=[]
    for i,p in enumerate(points):
        va=Vector(points[i]-Vector(points[i-1])) if i else Vector(points[1])-Vector(p)
        vb=Vector(points[i+1])-Vector(p) if i<len(points)-1 else va
        va.normalize();vb.normalize();na=Vector((-va.y,va.x));nb=Vector((-vb.y,vb.x));normal=na+nb;normal.normalize();den=max(.3,normal.dot(na));off=normal*(width*.5/den)
        left.append(tuple(Vector(p)+off));right.append(tuple(Vector(p)-off))
    return prism(name,left+list(reversed(right)),z0,z1,role,bevel)

def path(name,points,width,z0,z1,role='quiet_ivory',bevel=.01):
    return strip(name,[Vector(p) for p in points],width,z0,z1,role,bevel)

def arc(cx,cy,r,a,b,n=8):return [(cx+r*math.cos(math.radians(a+(b-a)*i/n)),cy+r*math.sin(math.radians(a+(b-a)*i/n))) for i in range(n+1)]

def marker(name,p,kind,normal=(0,0,1),owner=None):
    ob=bpy.data.objects.new('DATUM_'+name,None);SCENE.collection.objects.link(ob);ob.location=p;ob.empty_display_size=.08;ob['kind']=kind;ob['source_package']='D05_forward_welcome_candidate'
    RECEIVERS.append({'name':name,'kind':kind,'source_xyz':list(p),'world_xyz':world(p),'normal_source':list(normal),'receiver_part':owner})
    return ob

def text(name,label,at,size=.22,rotation=(math.pi/2,0,0),role='clinical_ink'):
    curve=bpy.data.curves.new(name,'FONT');curve.body=label;curve.size=size;curve.align_x='CENTER';curve.align_y='CENTER';curve.extrude=.0012;curve.resolution_u=2
    ob=bpy.data.objects.new(name,curve);SCENE.collection.objects.link(ob);ob.location=at;ob.rotation_euler=rotation;curve.materials.append(MATS[role]);ob['source_package']='D05_forward_welcome_candidate';ob['editable_label_text']=label
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');ob=bpy.context.object
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<1e-9],context='FACES_ONLY');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();ob.select_set(False)
    PARTS.append(ob);return ob

