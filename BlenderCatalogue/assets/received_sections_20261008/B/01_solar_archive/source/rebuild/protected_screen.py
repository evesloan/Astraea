import pathlib,json,sys,hashlib
B=pathlib.Path(__file__).resolve().parent;S=sys.argv[1];P=B/S;C=json.loads((P/'source/build_metadata.json').read_text())['section'];rows=json.loads((P/'qa/objects.json').read_text());gate=json.loads((P/'docs/source_gate.json').read_text());errors=[]
protected=gate['protected_crew_aabbs_in_envelope'];checks=[]
for r in rows:
 a=r['bounds_blender'];u=[min(C['sign']*a[0][0],C['sign']*a[0][1]),max(C['sign']*a[0][0],C['sign']*a[0][1])];v=[-a[1][1],-a[1][0]];h=a[2]
 if u[0]<2-.002 and u[1]>.002 and v[0]<36-.002 and v[1]>32+.002 and h[0]<2.65-.002 and h[1]>.002:errors.append('Protected portal invaded: '+r['name'])
 world=[a[0][0]+C['sign']*C['x'],a[0][1]+C['sign']*C['x'],h[0]+C['floor'],h[1]+C['floor'],v[0]+C['z'],v[1]+C['z']]
 if world[3]>C['roof']+.002:errors.append('Actual native roof cap: '+r['name'])
 for p in protected:
  b=p['world_aabb']
  if all(world[i]<b[i+1]-.002 and world[i+1]>b[i]+.002 for i in [0,2,4]):errors.append('Protected native AABB contact: '+r['name']+' / '+p['name'])
 checks.append({'name':r['name'],'actual_native_world_aabb':world})
report={'programme_key':C['key'],'source_sha256':hashlib.sha256((P/'source/native.blend').read_bytes()).hexdigest(),'export_sha256':hashlib.sha256((P/'exports/section.glb').read_bytes()).hexdigest(),'protected_portal_screen':'Actual evaluated source bounds against 2m inward threshold by 4m width and 2.65m headroom','crew_aabbs_checked':len(protected),'geometry':checks,'errors':errors,'limit':'Conservative source AABB screen plus imported GLB parity; external approach/root floor and installed traversal untested'}
(P/'qa/protected_screen.json').write_text(json.dumps(report,indent=2));print('Actual native protection screen',len(errors),'errors');assert not errors,errors
