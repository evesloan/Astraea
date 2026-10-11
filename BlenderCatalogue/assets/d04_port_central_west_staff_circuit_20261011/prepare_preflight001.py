from pathlib import Path
import json,hashlib,subprocess,copy
R=Path('/workspace/astraea-recovered-532087b9-20261010T083844Z');W=R/'BlenderCatalogue/assets/d04_port_central_west_staff_circuit_20261011';old=R/'BlenderCatalogue/assets/d04_port_central_staff_work_links_20261011';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P=json.load(open(old/'AUDIT_INPUT_PLAN.json'))
P.update(base_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),active=False,cuts=[],moves=[],gates=[],parts=[],source_protected_native_exports={f:sha(R/f) for f in subprocess.check_output(['git','ls-files','Game','BlenderCatalogue'],cwd=R,text=True).splitlines() if f.endswith(('.blend','.glb'))})
assert len(P['source_protected_native_exports'])==4321
P['source_pins']={f:sha(R/f)for f in P['source_pins']};P['source_pins']['Game/data/architecture/D04_PORT_CENTRAL_COURT_WORK_LINKS.json']=sha(R/'Game/data/architecture/D04_PORT_CENTRAL_COURT_WORK_LINKS.json')
P['limits']=['Five west-court work thresholds and one enclosed west perimeter staff circuit only; commons and two southern east court links remain held by public crossing/vertical allocation constraints.','This is a used-side branch; complete separate clean-supply/used-return coverage remains unfinished. Upstream corridor/lobbies/cabin are shared.','Production private-consent/vacancy provider remains absent; all new private gates closed without valid visit. Temporary known consent tests only.','Narrow0.75m west court receives a protected worker stance at its edge using a deep collar; no full-court or loaded cart access claim.','No original public route, individual home wall/entry, floor/ceiling/roof, capacity, hull or Training allocation is cut.','Engineering/load sizing, loaded cart, stock/refill, habitat/biology, ordinary-game/CRT/hardware/final and whole ship/eight groups remain unfinished; historical two unpublished r004 native losses unchanged.']
pc=json.load(open(R/'BlenderCatalogue/assets/d04_port_central_neighborhood_20261011/PLAN.json'));st=json.load(open(R/'BlenderCatalogue/assets/d04_port_central_staff_riser_20261011/PLAN.json'));by={q['name']:q for q in pc['assemblies']['CombinedStructure']+st['parts']}
for i,(prefix,z,wallx,stance)in enumerate([('PCK_D04HC_west',-43.2,-102.6,-100.8),('PCK_D04HC2_west',-63.2,-99.7,-99.5),('PCK_D04HC3_west',-71.6,-102.6,-101.2),('PCK_D04HC4_west',43.2,-102.2,-100.6),('PCK_D04HC5_west',57.6,-102.2,-100.6)]):
 x=-101.2 if i==1 else wallx-.12
 P['gates'].append({'name':'PortCentralWestCourtGate'+str(i),'id':'D04_port_central_west_court_work_gate_'+str(i),'z':z,'wall_x':wallx,'pivot':[x,16.5,z-.574],'closed_center':[x,17.85,z],'private_side_normal':[1,0,0],'candidate_open_degrees':-90 if i==1 else 90,'requires_visit':True,'sweep_min':[x-1.3 if i==1 else x-.1,16.5,z-.7],'sweep_max':[x+.1 if i==1 else x+1.3,19.25,z+.72],'members':[],'control_members':[],'court_prefix':prefix,'court_stance':[stance,16.5,z]})
 for suffix in ['_PrivacyScreen','_GlassUpper']:
  q=by[prefix+suffix];P['cuts'].append({'source_root':'D04PortCentralHabitatNeighborhood','source_model':'D04_PORT_CENTRAL_COMBINEDSTRUCTURE_r002.glb','name':q['name'],'preimage':q,'boxes':[{'min':[wallx-.05,16.495,z-.7],'max':[wallx+.25,19.2,z+.7]}]})
for name,q in by.items():
 if name.startswith('PCK_D04HC3_west_')and(name.endswith('_Planter_1')or name.endswith('_Soil_1')or '_LeafMass_1_'in name):P['moves'].append({'source_root':'D04PortCentralHabitatNeighborhood','source_model':'D04_PORT_CENTRAL_COMBINEDSTRUCTURE_r002.glb','name':name,'preimage':q,'delta':[1.6,0,0]})
q=by['PCS_D04Boundary0'];P['cuts'].append({'source_root':'D04PortCentralStaffCatchment','source_model':'D04_PORT_CENTRAL_STAFF_STRUCTURE_r001.glb','name':q['name'],'preimage':q,'boxes':[{'min':[-64.7,16.495,-101.3],'max':[-64.5,19.2,-99.9]}]})
P['new_floor_m2']=None
(W/'AUDIT_INPUT_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'prepare_preflight001.py').write_bytes(Path(__file__).read_bytes())
script=(old/'probe_site001.gd').read_text();start=script.index(' for gate in p.gates:');end=script.index(' FileAccess.open(',start)
script=script[:start]+''' for gate in p.gates:
  for x in [-104,gate.pivot[0],gate.wall_x,gate.court_stance[0]]:
   var at:=Vector3(x,16.5,gate.z);var cap:=CapsuleShape3D.new();cap.height=1.8;cap.radius=.3;cap.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=cap;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925);var hits:=space.intersect_shape(q,64);stances.append({"gate":gate.name,"at":[x,16.5,gate.z],"blockers":hits.map(func(h):return str(h.collider.get_path()))})
'''+script[end:];script=script.replace('d04_port_central_staff_work_links_20261011','d04_port_central_west_staff_circuit_20261011');(W/'probe_site001.gd').write_text(script)
print('Pinned',len(P['source_protected_native_exports']),'originals;',len(P['cuts']),'local cuts',len(P['moves']),'rigid planter meshes')
