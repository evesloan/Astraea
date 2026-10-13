"""Metre-UV low-poly construction forms; world X/Y/Z -> editable Blender X/-Z/Y."""
import bpy,bmesh,math
from mathutils import Vector

class Forms:
    def __init__(self,materials,root,origin=(0,0,0)):
        self.M=materials;self.root=root;self.origin=origin
    def source(self,p):return (p[0]-self.origin[0],-p[2]+self.origin[2],p[1]-self.origin[1])
    def mesh(self,name,vertices,faces,role):
        d=bpy.data.meshes.new(name);d.from_pydata([self.source(p) for p in vertices],[],faces);d.update()
        bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free()
        d.materials.append(self.M[role]);uv=d.uv_layers.new(name='metric_material_uv');scale=self.M[role].get('meters_per_tile_uv',[1,1])
        for face in d.polygons:
            axis=max(range(3),key=lambda a:abs(face.normal[a]));axes=[a for a in range(3) if a!=axis]
            for li in face.loop_indices:
                v=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/scale[0],v[axes[1]]/scale[1])
        o=bpy.data.objects.new(name,d);bpy.context.scene.collection.objects.link(o);o.parent=self.root;o['material_role']=role
        return o
    def box(self,name,a,b,role,bevel=0):
        v=[(x,y,z) for x,y,z in [(a[0],a[1],a[2]),(b[0],a[1],a[2]),(b[0],b[1],a[2]),(a[0],b[1],a[2]),(a[0],a[1],b[2]),(b[0],a[1],b[2]),(b[0],b[1],b[2]),(a[0],b[1],b[2])]]
        o=self.mesh(name,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role)
        if bevel:
            m=o.modifiers.new('Soft folded or machined edge','BEVEL');m.width=bevel;m.segments=2;m.affect='EDGES'
            bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.modifier_apply(modifier=m.name);o.select_set(False)
        return o
    def cylinder(self,name,centre,radius,length,axis,role,n=16):
        axes=[i for i in range(3) if i!=axis];v=[]
        for side in [-1,1]:
            for i in range(n):
                p=list(centre);p[axis]+=side*length/2;p[axes[0]]+=radius*math.cos(i*2*math.pi/n);p[axes[1]]+=radius*math.sin(i*2*math.pi/n);v.append(p)
        return self.mesh(name,v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],role)
    def torus(self,name,centre,radius,tube,axis,role,n=16,m=6):
        axes=[i for i in range(3) if i!=axis];v=[]
        for i in range(n):
            a=i*2*math.pi/n
            for k in range(m):
                b=k*2*math.pi/m;p=list(centre);p[axis]+=tube*math.sin(b);r=radius+tube*math.cos(b);p[axes[0]]+=r*math.cos(a);p[axes[1]]+=r*math.sin(a);v.append(p)
        return self.mesh(name,v,[(i*m+k,((i+1)%n)*m+k,((i+1)%n)*m+(k+1)%m,i*m+(k+1)%m) for i in range(n) for k in range(m)],role)
    def beam(self,name,a,b,radius,role,n=8):
        direction=Vector(b)-Vector(a);length=direction.length;centre=(Vector(a)+Vector(b))/2
        o=self.cylinder(name,(0,0,0),radius,length,1,role,n)
        # Form vertices are already in source coordinates; rotate their source Y-up beam.
        source_dir=Vector((direction.x,-direction.z,direction.y));rotation=Vector((0,0,1)).rotation_difference(source_dir.normalized())
        offset=Vector(self.source(centre));zero=Vector(self.source((0,0,0)))
        for v in o.data.vertices:v.co=rotation@(v.co-zero)+offset
        return o
    def spool(self,name,x,y,z,role,r=.075,h=.16):
        self.cylinder(name+'_wound_thread',(x,y+h/2,z),r*.80,h-.025,1,role)
        for level in [y+.012,y+h-.012]:self.cylinder(name+'_flange',(x,level,z),r,.024,1,'warm_walnut')
        self.cylinder(name+'_core',(x,y+h/2,z),r*.16,h+.035,1,'ivory_enamel')
        for level in [y+h*.3,y+h*.6]:self.torus(name+'_thread_line_'+str(level),(x,level,z),r*.80,.0025,1,'oatmeal_weave')
    def folded(self,name,x0,x1,y,z0,z1,role,layers=3):
        base=None
        for i in range(layers):
            yy=y+i*.065;o=self.box(name if i==0 else name+'_layer_'+str(i),(x0+i*.007,yy,z0+i*.008),(x1-i*.008,yy+.06,z1-i*.008),role,.014)
            base=base or o
            self.box(name+'_turned_hem_'+str(i),(x0-.001,yy+.018,z0+.055),(x0+.020,yy+.042,z1-.055),'oatmeal_weave',.006)
        return base
    def text(self,name,label,p,size=.14,west=True,role='ivory_enamel'):
        d=bpy.data.curves.new(name,'FONT');d.body=label;d.size=size;d.align_x='CENTER';d.align_y='CENTER';d.extrude=.0006
        o=bpy.data.objects.new(name,d);bpy.context.scene.collection.objects.link(o);o.parent=self.root;o.location=self.source(p)
        o.rotation_euler=(math.pi/2,0,-math.pi/2 if west else math.pi/2);d.materials.append(self.M[role]);return o
