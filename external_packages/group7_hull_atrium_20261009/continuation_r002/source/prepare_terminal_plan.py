"""Choose clear discrete terminal roof/wall fields against retained floors."""
import json,sys,hashlib
from pathlib import Path
sys.path.insert(0,'C:/Users/cered/Dolphin/AstraeaTools/pythondeps')
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
P=Path(__file__).resolve().parents[1];OLD=P.parent;D=OLD/'dependencies/canonical_77a745';L=OLD/'dependencies/canonical_9d6f85'
outline=json.loads((D/'Game/data/hull_envelope.json').read_text())['plan_xz_m'];top_outline=Polygon([(x*.985,z) for x,z in outline]);floors=[]
for f in [D/'Game/data/generated/structural_meshes.json',D/'Game/data/architecture/REMAINING_BATCH_FLOORS.json',L/'Game/data/generated/received_structural_meshes.json']:floors.extend(json.loads(f.read_text())['regions'])
terms=[]
for name,sgn,edges,width,topwidth in [('Fore',-1,[0,14,15],70.92,65),('Aft',1,[6,7,8],54.175,49)]:
 domain=box(-130,-550,130,-510) if sgn<0 else box(-130,510,130,550);notch=box(-6,-530.7,6,-509.2) if sgn<0 else box(-6,509.2,6,530.7)
 p=top_outline.intersection(domain);aprons=[box(6,-510,70.92,-509.2),box(-70.92,-510,-6,-509.2)] if sgn<0 else [box(6,509.2,54.175,510),box(-54.175,509.2,-6,510)]
 roof=unary_union([p,*aprons]).difference(notch);assert roof.geom_type=='Polygon' and not roof.interiors
 bridges=[box(4,sgn*517.5-1.5,6,sgn*517.5+1.5),box(-6,sgn*517.5-1.5,-4,sgn*517.5+1.5)]
 conflicts=[]
 for r in floors:
  if min(69.5,r['floor_y'])-max(69.2,r['floor_y']-r['thickness'])<=1e-6:continue
  q=unary_union([Polygon(t) for t in r['triangles']]);area=roof.intersection(q).area+sum(b.intersection(q).area for b in bridges)
  if area>1e-7:conflicts.append({'floor':r['id'],'area_m2':area})
 assert not conflicts,conflicts
 terms.append({'id':'G7C2_'+name,'sign_z':sgn,'outer_edges':edges,'roof_y':69.5,'roof_underside_y':69.2,'roof_boundary_xz':list(roof.exterior.coords)[:-1],'source_roof_area_m2':roof.area,'bridge_polygons_xz':[list(b.exterior.coords)[:-1] for b in bridges],'bridge_area_m2':sum(b.area for b in bridges),'protected_route_x':[-4,4],'protected_route_end_abs_z':530,'open_upper_route_aperture_x':[-6,6],'neck_side_outer_x':[-6.8,6.8],'neck_end_abs_z':531.5,'cutback_headwall_abs_z':510,'headwall_halfwidth_at_y69_5':width,'headwall_halfwidth_at_y106_5':topwidth,'headwall_y':[69.5,106.5],'portal_abs_z':517.5,'portal_family':'AST-STF-008','portal_world_bounds_z_width_m':2.76,'portal_y':[69.5,72.32],'roof_retained_floor_overlap_candidates':conflicts,'root_connector_receivers':[{'id':name+'_PortBridgeReceiver','retained_floor':'D11_'+('fore' if sgn<0 else 'aft')+'_route','contact_edge_x':-4,'z_interval':[sgn*517.5-1.5,sgn*517.5+1.5],'top_y':69.5},{'id':name+'_StarboardBridgeReceiver','retained_floor':'D11_'+('fore' if sgn<0 else 'aft')+'_route','contact_edge_x':4,'z_interval':[sgn*517.5-1.5,sgn*517.5+1.5],'top_y':69.5}],'remaining_interface':'No cap across retained D18 end route; actual upper route headroom/roof choice belongs to root. Adjacent general upper-body side seams atZ±510 remain open; no private face claimed.'})
out={'baseline':'9d6f8518f9ddbe5892711ca4eb4849a46fbd32be','source_authority':'Root continuation delegation; original overview and engineering pixels reopened; whole-ship section coordination re-read','new_local_design':'Discrete69.5m terminal roof wings and106.5m framed head/neck walls, not a loft of the first delivery guides or adoption of general taperA','terms':terms,'floor_input_regions':len(floors),'new_guest_units':0,'source_floor_policy':'Roof slabs and bridge plates are new source-owned architectural surfaces. Root may register their planning footprints but must not duplicate these meshes with another floor builder. Existing route floors are untouched; root owns their boundary collars/adoption.','scope':'Fit floor intersections before construction; remaining source meshes, contacts, materials and representative views checked after builder. No pressure/load, engine, cart or final-art acceptance.'}
(P/'docs').mkdir(exist_ok=True);(P/'docs/TERMINAL_PLAN_R002.json').write_text(json.dumps(out,indent=2)+'\n');print('TERMINAL_PLAN',[(t['id'],t['source_roof_area_m2'],t['bridge_area_m2']) for t in terms])
