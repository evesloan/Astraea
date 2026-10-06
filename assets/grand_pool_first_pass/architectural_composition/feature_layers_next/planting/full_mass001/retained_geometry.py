"""Pure, deterministic pool botanical derivative geometry. No bpy or source writes.

The shaped blade, pleated fan and tapered closed tube formulae are derived from
the pinned BOT-002/003/007 authoring scripts. This recomposes their construction;
it does not append/export unchanged plants, flatten a complete crown, or copy
reference-image pixels. Coordinates here are local Blender X/right Y/depth Z/up.
"""
import json, math, hashlib, sys
sys.dont_write_bytecode=True
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAT = Path('/workspace/shared/astraea-catalogue-continuation-20261002')
AUDIT = HERE.parent/'reference_audit'
if not AUDIT.is_dir():
    AUDIT = Path('/workspace/scratch/375c2e438292/pool-seating-greenery-audit')
TAU = math.tau
def add(a,b): return [x+y for x,y in zip(a,b)]
def sub(a,b): return [x-y for x,y in zip(a,b)]
def mul(a,s): return [x*s for x in a]
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
def norm(a): return mul(a,1/math.sqrt(dot(a,a)))
def world(p,position): return [position[0]+p[0], position[1]+p[2], position[2]-p[1]]
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def bounds(points): return [[min(p[k] for p in points) for k in range(3)], [max(p[k] for p in points) for k in range(3)]]
def fitted_length(base,angle,length,width,kind,xmin,xmax,ymin,ymax):
    """Solve the actual shaped-blade sample inequalities for length.

    The leaf keeps its full-width source profile; only its authored reach is
    chosen. This avoids treating full half-width as though it occurred at tips.
    """
    a=math.radians(angle);di=[math.cos(a),math.sin(a)];side=[-di[1],di[0]]
    for t in [.12,.29,.49,.69,.87,1]:
        profile=math.sin(math.pi*t)**(.78 if kind=='broad' else .95)*(1.15-.38*t)
        for u in [-1,1]:
            for axis,(lo,hi) in enumerate([(xmin,xmax),(ymin,ymax)]):
                constant=base[axis]+side[axis]*u*width*.5*profile;factor=di[axis]*t
                if factor>.00001:length=min(length,(hi-constant)/factor)
                elif factor<-.00001:length=min(length,(lo-constant)/factor)
    assert length>.075,(base,angle,length)
    return length

class Geometry:
    def __init__(self, ident, parent, position, support, kind, variant):
        self.a = dict(name=ident, parent_design_id=parent, family='botanical_cluster' if parent=='AST-BOT-007' else 'botanical_understory', position_xyz=position, yaw_radians=0, support=support, kind=kind, variant=variant, parts=[], joints=[], root_parts=[], markers=[], source=f'source/{ident}.blend', export=f'exports/{ident}.glb', collision='none; retain planter collider, never a foliage AABB')
    def mesh(self,name,vs,fs,role,thin=False,uvs=None,controls=None):
        # Per-loop UVs survive normal recalculation and separate runtime consolidation.
        loops=[]
        for f in fs:
            if uvs: loops.extend([uvs[i] for i in f])
            else:
                n=cross(sub(vs[f[1]],vs[f[0]]),sub(vs[f[2]],vs[f[0]])); axis=max(range(3),key=lambda k:abs(n[k])); axes=[k for k in range(3) if k!=axis]
                tile=(.6,1.2) if role=='botanical_bark' else (.4,.4)
                loops.extend([[vs[i][axes[0]]/tile[0],vs[i][axes[1]]/tile[1]] for i in f])
        part=dict(name=name,vertices=vs,faces=fs,loop_uvs=loops,material_role=role,surface_kind='open_shaped_leaf' if thin else 'closed_support',shape_controls=controls or {})
        self.a['parts'].append(part); return part
    def tube(self,name,points,radii,role='botanical_bark',sides=8,flat=False):
        vs=[]; fs=[]
        for i,(p,r) in enumerate(zip(points,radii)):
            if flat:u,v=[1,0,0],[0,1,0]
            else:
                tangent=norm(sub(points[min(i+1,len(points)-1)],points[max(i-1,0)])); seed=[0,0,1] if abs(tangent[2])<.85 else [1,0,0]; u=norm(cross(tangent,seed)); v=cross(tangent,u)
            vs.extend([add(p,mul(add(mul(u,math.cos(TAU*j/sides)),mul(v,math.sin(TAU*j/sides))),r)) for j in range(sides)])
        for k in range(len(points)-1): fs.extend([[k*sides+j,k*sides+(j+1)%sides,(k+1)*sides+(j+1)%sides,(k+1)*sides+j] for j in range(sides)])
        fs.extend([list(reversed(range(sides))),[(len(points)-1)*sides+j for j in range(sides)]])
        p=self.mesh(name,vs,fs,role,controls=dict(centerline=points,radii=radii,sides=sides,flat_rings=flat))
        # Same distance-around/distance-along UV construction as retained source.
        lengths=[0]
        for a,b in zip(points,points[1:]): lengths.append(lengths[-1]+math.dist(a,b))
        uv=p['loop_uvs']; cursor=0; tile=(.6,1.2) if role=='botanical_bark' else (.4,.4)
        for fi,f in enumerate(fs):
            if fi<(len(points)-1)*sides:
                edge=fi%sides
                for li,vi in enumerate(f):
                    k,j=divmod(vi,sides); j=sides if edge==sides-1 and j==0 else j
                    uv[cursor+li]=[TAU*radii[k]*j/sides/tile[0],lengths[k]/tile[1]]
            cursor+=len(f)
        return name
    def joint(self,child,parent,point,kind='physical_overlap'):
        self.a['joints'].append(dict(child=child,parent=parent,probe_local=point,kind=kind))
    def blade(self,name,base,angle,length,width,rise,arch,cup,role,twist=0,kind='broad',parent=None):
        a=math.radians(angle); direction=[math.cos(a),math.sin(a),0]; side=[-math.sin(a),math.cos(a),0]
        def center(t): return add(add(base,mul(direction,length*t)),[0,0,rise*t+arch*math.sin(math.pi*t)-.020*t**3])
        vs=[base]; uvs=[[.5,0]]; rows=[]
        for t in [.12,.29,.49,.69,.87]:
            rows.append(list(range(len(vs),len(vs)+5)))
            for u in [-1,-.55,0,.55,1]:
                profile=math.sin(math.pi*t)**(.78 if kind=='broad' else .95)*(1.15-.38*t)
                vs.append(add(add(center(t),mul(side,u*width*.5*profile)),[0,0,cup*u*u*math.sin(math.pi*t)+twist*u*t*math.sin(math.pi*t)])); uvs.append([.5+u*.5,t])
        tip=len(vs);vs.append(center(1));uvs.append([.5,1]); fs=[]
        fs.extend([[0,rows[0][j],rows[0][j+1]] for j in range(4)])
        for x,y in zip(rows,rows[1:]): fs.extend([[x[j],y[j],y[j+1],x[j+1]] for j in range(4)])
        fs.extend([[rows[-1][j],tip,rows[-1][j+1]] for j in range(4)])
        self.mesh(name,vs,fs,role,True,uvs,dict(base=base,angle=angle,length=length,width=width,rise=rise,arch=arch,cup=cup,twist=twist,kind=kind))
        if parent:self.joint(name,parent,base,'leaf_base_buried_in_support')
        return name
    def fan(self,name,base,azimuth,pitch,radius,half_angle,pleat,role,parent):
        az=math.radians(azimuth); pi=math.radians(pitch); out=[math.cos(az),math.sin(az),0]; axis=add(mul(out,math.cos(pi)),[0,0,math.sin(pi)]); side=[-math.sin(az),math.cos(az),0]; normal=norm(cross(side,axis))
        vs=[base];uvs=[[.5,0]];rows=[];n=12
        for t in [.26,.61,1]:
            row=[]
            for j in range(n+1):
                a=math.radians(-half_angle+2*half_angle*j/n); rr=radius*t*(1 if j%2==0 else(.94 if t==1 else 1)); p=add(add(base,mul(add(mul(axis,math.cos(a)),mul(side,math.sin(a))),rr)),mul(normal,pleat*t*(1 if j%2==0 else -.28))); row.append(len(vs));vs.append(p);uvs.append([j/n,t])
            rows.append(row)
        fs=[[0,rows[0][j],rows[0][j+1]] for j in range(n)]
        for x,y in zip(rows,rows[1:]): fs.extend([[x[j],y[j],y[j+1],x[j+1]] for j in range(n)])
        self.mesh(name,vs,fs,role,True,uvs,dict(base=base,azimuth=azimuth,pitch=pitch,radius=radius,half_angle=half_angle,pleat=pleat));self.joint(name,parent,base,'fan_base_in_petiole_cap')
    def root(self,name,x,y,radius=.04):
        self.tube(name,[[x,y,0],[x,y,.028],[x,y,.065]],[radius,radius*.93,radius*.58],flat=True,sides=9)
        self.a['root_parts'].append(name);self.a['markers'].append(dict(name=name+'_SOIL_CONTACT',point_local=[x,y,0],physical_part=name,kind='soil_contact'))
    def flowers(self,prefix,root,base,height,rot=0):
        top=add(base,[.025*math.cos(rot),.025*math.sin(rot),height]); mid=add(base,[.010,0,height*.50]); st=prefix+'_stem';self.tube(st,[base,mid,top],[.005,.004,.0028],'botanical_leaf_olive',6);self.joint(st,root,base)
        rec=prefix+'_receptacle'; self.tube(rec,[add(top,[0,0,-.006]),top,add(top,[0,0,.012])],[.005,.012,.006],'botanical_leaf_olive',7,True);self.joint(rec,st,top)
        for k in range(5):self.blade(prefix+'_petal_'+str(k),add(top,[0,0,.004]),rot+k*72,.048,.038,.026,.012,.007,'botanical_flower',kind='petal',parent=rec)
        self.tube(prefix+'_pollen', [add(top,[0,0,.006]),add(top,[0,0,.019])],[.007,.004],'botanical_flower',6,True);self.joint(prefix+'_pollen',rec,add(top,[0,0,.006]))
    def finish(self):
        a=self.a;a['bounds_local']=bounds([p for m in a['parts'] for p in m['vertices']]); a['bounds_world']=bounds([world(p,a['position_xyz']) for m in a['parts'] for p in m['vertices']]);a['planned_triangle_count']=sum(len(f)-2 for m in a['parts'] for f in m['faces']);a['part_count']=len(a['parts']);return a

def basal(i,candidate):
    z=sum(q[2] for q in candidate['soil_bounds'])/2;g=Geometry(f'AST-BOT-003_pool_basal_{i:02d}','AST-BOT-003',[-49.45,53.2,z],candidate['support'],'basal',i)
    # A staggered, overlapping living bank, not a row of unchanged library pots.
    groups=[(-.82,-.115),(-.42,-.13),(-.015,-.10),(.38,-.13),(.78,-.11),(-.63,.145),(-.215,.155),(.205,.14),(.615,.16)]
    for j,(x,y) in enumerate(groups):
        root=f'basal_{j:02d}_crown';g.root(root,x,y,.043)
        for k in range(15):
            ring=k//6;ang=(k%6)*60+ring*27+i*7+j*19; h=.035+ring*.012
            le=[.355,.295,.235][ring]*(.94+.045*((j+k+i)%3));width=[.232,.218,.178][ring]
            # Fit blade reach and width by authored angle/radius, not mesh squash.
            le=fitted_length([x,y,h],ang,le,width,'rosette',-1.085,1.085,-.43,.43)
            color=['jade','sage','jade','olive','jade'][(k+j+i)%5]
            g.blade(f'basal_{j:02d}_spoon_{k:02d}',[x,y,h],ang,le,width,[.055,.09,.145][ring],.068,.025,'botanical_leaf_'+color,(-1 if k%2 else 1)*.009,'rosette',root)
        if j in [0,2,4,6,8]:g.flowers(f'basal_{j:02d}_flower',root,[x,y,.038],.225+.015*((j+i)%4),rot=j*32+i*11)
    return g.finish()

def middle(i,candidate):
    z=sum(q[2] for q in candidate['soil_bounds'])/2;special=candidate['is_market_rest_0_view_bed'];g=Geometry(f'AST-BOT-002_pool_middle_{i:02d}','AST-BOT-002',[-49.45,53.2,z],candidate['support'],'middle',i)
    groups=[(.20,-.015,.85),(.67,.025,1.01)] if special else [(-.63,.01,.80+.018*i),(-.04,-.015,1.14-.012*i),(.58,.025,.94+.012*i)]
    xmin=-.15 if special else -1.10; xmax=1.10
    for j,(x,y,height) in enumerate(groups):
        root=f'middle_{j}_root';g.root(root,x,y,.05);stem=f'middle_{j}_curved_stem';pts=[[x,y,.035],[x-.018,y-.025,.23],[x+.015,y,.46],[x-.025,y+.02,height-.19]];g.tube(stem,pts,[.032,.029,.022,.012]);g.joint(stem,root,pts[0])
        # Alternate leaves connect from a substantial base to unequal crown heights.
        for k in range(14):
            t=(k+.7)/15;seg=min(2,int(t*3));q=t*3-seg;attach=add(pts[seg],mul(sub(pts[seg+1],pts[seg]),q));ang=(k*137.5+i*9+j*43)%360
            le=.36+.055*((k+j)%3);width=.265+.018*((k+i)%3);ca,sa=math.cos(math.radians(ang)),math.sin(math.radians(ang));reach=.030
            base=add(attach,[ca*reach,sa*reach,.026]);le=fitted_length(base,ang,le,width,'broad',xmin+.025,xmax-.025,-.37,.37)
            pet=f'middle_{j}_petiole_{k:02d}';g.tube(pet,[attach,base],[.010,.006],'botanical_leaf_olive',7);g.joint(pet,stem,attach)
            g.blade(f'middle_{j}_cupped_leaf_{k:02d}',base,ang,le,width,.08+.018*(k%3),.095,.043,'botanical_leaf_'+['jade','sage','jade','olive'][(k+j+i)%4],(.014 if k%2 else -.011),'broad',pet)
    return g.finish()

def crown(i,candidate):
    z=sum(q[2] for q in candidate['soil_bounds'])/2;special=candidate['is_market_rest_0_view_bed'];g=Geometry(f'AST-BOT-007_pool_fitted_crown_{i:02d}','AST-BOT-007',[-49.45,53.2,z],candidate['support'],'crown',i)
    rx=.49 if special else .035;root='fitted_joined_root_crown';g.tube(root,[[rx,0,0],[rx,0,.07],[rx,.005,.145]],[.115,.103,.070],flat=True,sides=12);g.a['root_parts'].append(root);g.a['markers'].append(dict(name='CROWN_SOIL_CONTACT',point_local=[rx,0,0],physical_part=root,kind='soil_contact'))
    xs=[.22,.51,.78] if special else [-.43,-.06,.48];heights=[[1.04,1.39,1.17],[1.00,1.39,1.12],[1.18,1.32,1.09],[1.10,1.38,1.23],[1.24,1.30,1.02],[.99,1.42,1.20]][i];paths=[]
    for j,(x,h) in enumerate(zip(xs,heights)):
        ps=[[rx,0,.07],[rx+(x-rx)*.48,.014*(j-1),.42],[x,-.015*(j-1),.78],[x+.025*((i+j)%3-1),.026*(j-1),h]];sn=f'fitted_lift_stem_{j}';g.tube(sn,ps,[.042,.035,.026,.012]);g.joint(sn,root,ps[0]);paths.append((sn,ps))
    # Near-upright original pleated fans keep actual fan curvature/UVs, with
    # changed petiole/azimuth/pitch/radius. No asset-wide depth scale is used.
    layout=[(0,2,270,75,.43),(0,3,90,82,.48),(1,2,90,74,.42),(1,3,270,86,.48),(2,2,270,78,.44),(2,3,90,82,.47),(0,2,90,83,.34),(1,2,270,87,.40),(2,2,90,84,.37),(1,3,90,88,.40),(2,3,270,86,.36)]
    for k,(j,ix,az,pitch,radius) in enumerate(layout):
        sn,ps=paths[j];p=list(ps[ix]);p[2]-=.08 if k>=6 else 0
        # Intermediate attachment lies on actual last stem segment, not near it.
        if k>=6:
            start,end=ps[ix-1],ps[ix];t=(p[2]-start[2])/(end[2]-start[2]);p=add(start,mul(sub(end,start),t))
        if special:radius*=.68
        else:radius*=.96+.02*((i+k)%3)
        a=math.radians(az);base=add(p,[math.cos(a)*.047,math.sin(a)*.047,.045]);pet=f'fitted_fan_petiole_{k:02d}';g.tube(pet,[p,add(p,[0,math.sin(a)*.024,.027]),base],[.013,.010,.006],'botanical_leaf_olive',7);g.joint(pet,sn,p)
        g.fan(f'fitted_pleated_fan_{k:02d}',base,az,pitch,radius,58+((k+i)%3)*4,.027,'botanical_leaf_'+['jade','sage','jade','olive'][(k+i)%4],pet)
    return g.finish()

def wet(i,candidate):
    g=Geometry(f'AST-BOT-003_pool_wet_fullness_{i:02d}','AST-BOT-003',candidate['position_xyz'],candidate['support'],'wet_whorl',i)
    # An additive narrow sleeve intersects the retained .031 m radius crown.
    root='additive_crown_sleeve';g.tube(root,[[.002,.001,.027],[.002,.001,.043],[.002,.001,.064]],[.022,.024,.014],flat=True,sides=9)
    g.a['root_parts'].append(root);g.a['markers'].append(dict(name='RETAINED_ROSETTE_CROWN_CONTACT',point_local=[.002,.001,.034],physical_part=root,kind='retained_crown_overlap',retained_part='rosette_basal_crown',retained_instance=f'wet_pot_rosette_{i}'))
    for k in range(19):
        ring=k//8;angle=k*45+ring*24+i*13;le=[.248,.215,.155][ring];width=[.139,.137,.111][ring];base=[.002,.001,.033+ring*.013]
        g.blade(f'fullness_spoon_{k:02d}',base,angle,le,width,[.067,.12,.184][ring],.075,.026,'botanical_leaf_'+['jade','sage','jade','olive'][(k+i)%4],(.009 if k%2 else -.008),'rosette',root)
    for j in range(3):g.flowers(f'fullness_flower_{j}',root,[.002,.001,.038],.275+.028*((j+i)%3),j*105+i*17)
    return g.finish()

def build_plan():
    beds=json.loads((AUDIT/'PLANTING_ENVELOPE_CANDIDATES.json').read_text())['candidates'];wetpots=json.loads((AUDIT/'WET_POT_FULLNESS_CANDIDATES.json').read_text())['candidates'];support=json.loads((CAT/'assets/grand_pool_orchard_section/source/connected_contract.json').read_text());parts={p['name']:p for p in support['source_parts']}
    assets=[]
    for i,c in enumerate(beds):
        soil=parts[c['support']];top=max(v[1] for v in soil['world_vertices']);poly=[[v[0],v[2]] for v in soil['world_vertices'] if abs(v[1]-top)<1e-6];assert len(poly)==8
        for fn in [basal,middle,crown]:
            a=fn(i,c);a['soil_polygon_xz']=poly;a['approved_reservations']=c['layers'];a['special_screen_bed']=c['is_market_rest_0_view_bed'];assets.append(a)
    for i,c in enumerate(wetpots):
        a=wet(i,c);a['approved_reservations']=[dict(name='compact_wet_whorl',bounds=c['bounds'])];assets.append(a)
    return dict(schema='astraea_pool_comfort_greenery_v1',status='unbuilt_source_candidate',coordinate_mapping='local Blender (x,y,z) -> world glTF position + (x,z,-y)',ownership='New comfort_greenery sibling. 23 separately placed derivatives of retained IDs. No new catalogue ID.',budget=dict(installed_retained=51,earlier_planned_retained=48,botanical_additions=23,media_additions_parent_owned=4,prospective_total_cap=126),assets=assets,not_claimed=['Source QA until reopened in Blender','Export or engine import','Visual acceptance or loaded circulation','Horticulture, species, structural soil depth or drainage','Shared renderer/material/palette/light-budget changes'])

def main():
    p=build_plan();(HERE/'greenery_contract.json').write_text(json.dumps(p,indent=2)+'\n');print(json.dumps({'assets':len(p['assets']),'parts':sum(a['part_count'] for a in p['assets']),'triangles':sum(a['planned_triangle_count'] for a in p['assets'])}))
if __name__=='__main__':main()
