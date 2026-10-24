#!/usr/bin/env python3
"""Focused source integrity, actual pad areas and fixed bridge-byte equivalence."""
from pathlib import Path
import hashlib, json, struct, sys
sys.dont_write_bytecode=True
import numpy as np
from triangle_gate import part_triangles
from screen_section import clip
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
checks=0

def check(value,label):
    global checks
    assert value,label
    checks+=1

def accessors(path):
    data=path.read_bytes();n=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+n]);b=data[28+n:]
    def payload(i):
        a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']]
        size={5126:4,5125:4,5123:2,5121:1}[a['componentType']]*{'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
        start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',size)
        return b''.join(b[start+j*stride:start+j*stride+size]for j in range(a['count']))
    return {node['name']:[{k:payload(i)for k,i in {'indices':p['indices'],**p['attributes']}.items()}for p in doc['meshes'][node['mesh']]['primitives']]for node in doc['nodes']if'mesh'in node}

def owners(x,z,width,depth,regions):
    matches=[]
    for region in regions:
        area=0.
        for triangle in region['triangles']:
            poly=[list(p)for p in triangle]
            for axis,value,above in [(0,x-width/2,True),(0,x+width/2,False),(1,z-depth/2,True),(1,z+depth/2,False)]:
                if poly:poly=clip(poly,axis,value,above)
            if len(poly)>2:area+=abs(sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(poly,poly[1:]+poly[:1])))*.5
        if area>1e-8:matches.append((region['id'],area))
    return matches

def main():
    result=HERE/'SOURCE_VALIDATION_r002.json';check(not result.exists(),'immutable output')
    plan=json.loads((HERE/'candidate_r002/CANDIDATE.json').read_text());parts=json.loads((HERE/'candidate_r002/MESHES.json').read_text())
    for path,pin in plan['source_pins'].items():
        data=(ROOT/path).read_bytes();check(hashlib.sha256(data).hexdigest()==pin['sha256'],'source pin '+path)
    check(not plan['active']and not any(plan[k]for k in ['integration_motion_admitted','integration_boarding_admitted','integration_joint_admitted']),'admission false')
    check(not plan['unresolved_receivers'],'receiver source bindings complete')
    layout=json.loads((ROOT/'Game/data/generated/structural_meshes.json').read_text())
    pads=[]
    for part in parts:
        t=part_triangles(part);volume=np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6
        check(volume>0,'outward nonzero volume '+part['name'])
        if 'Bearing_'not in part['name']and'SouthPad_'not in part['name']:continue
        points=np.array(part['vertices']);lo,hi=points.min(axis=0),points.max(axis=0);center=(lo+hi)/2
        floor=52.5 if 'SouthPad_' in part['name'] else 61.
        matches=owners(center[0],center[2],hi[0]-lo[0],hi[2]-lo[2],[r for r in layout['regions']if r['floor_y']==floor])
        area=(hi[0]-lo[0])*(hi[2]-lo[2]);check(len(matches)==1 and abs(matches[0][1]-area)<1e-6,'actual full pad footprint '+part['name'])
        pads.append({'part':part['name'],'owner':matches[0][0],'area_m2':area})
    old=accessors(ROOT/'Game/source_derivatives/group4_completion_20261011/AST-TRM-G4-019_boarding_bridge.glb')
    new=accessors(HERE/'runtime_r002/AST-TRM-BRIDGE-20261023-r002.glb')
    changed=set(json.loads((HERE/'runtime_r002/EXPORT_RECEIPT.json').read_text())['changed_moving_meshes'])
    check(old.keys()==new.keys(),'bridge exact source mesh identities')
    for name in old:
        if name not in changed:check(old[name]==new[name],'all fixed/knuckle accessor bytes '+name)
        else:
            check(len(old[name])==len(new[name]),'same bridge surface count')
            for a,b in zip(old[name],new[name]):
                check(a['indices']==b['indices'],'same bridge topology '+name)
                for attribute in a.keys()-{'POSITION','NORMAL'}:check(a[attribute]==b[attribute],'unchanged bridge attribute '+name+'/'+attribute)
    check(plan['central']['stationary_frames']==15 and plan['central']['docking_tolerance_m']==.005 and plan['central']['docking_tolerance_rad']==.001,'original dock precision/stationary criteria')
    check(plan['guideway']['running_width_m']==4 and plan['guideway']['running_clearance_top_y']-plan['guideway']['boarding_y']==4,'full upper envelope retained')
    report={'status':'PASS_SOURCE_ONLY','checks':checks,'full_actual_bearing_footprints':pads,'fixed_bridge_vertex_normal_uv_index_bytes_equal':True,'native_executed':False,'engine_executed':False,'not_proven':['Load capacity','moving body sweep','live station/controller integration','caster/joint','final visual/performance']}
    result.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'checks':checks,'actual_pads':len(pads)}))

if __name__=='__main__':main()
