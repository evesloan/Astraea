exec(open(__file__.replace('check_interfaces.py','prepare_candidate.py')).read())
# Screen retained house meshes conservatively, exact extrusion footprint for floor/pier prisms.
hits=[];touches=[];floor_shapes={}
for p in A['parts']:
 b=bb(p)
 if not b:continue
 for q in parts:
  a=q['bounds'];ds=[min(a[k+3],b[k+3])-max(a[k],b[k]) for k in range(3)]
  if min(ds)>1e-6:hits.append({'source':p['name'],'candidate':q['id'],'test':'conservative AABB, requires exact geometry if nonempty'})
 if p['kind']=='mesh' and abs(b[1]-83.76)<1e-6:
  polys=[]
  for f in p['faces']:
   v=[p['verts'][i] for i in f]
   if all(abs(t[1]-83.76)<1e-7 for t in v):
    poly=Polygon([(t[0],t[2]) for t in v])
    if poly.area>1e-9:polys.append(poly)
  if polys:floor_shapes[p['name']]=unary_union(polys)
for p in pier:
 b=p['bounds'];shape=box(b[0],b[2],b[3],b[5]);p['retained_slab_contacts']=[{'id':n,'area_m2':shape.intersection(f).area} for n,f in floor_shapes.items() if shape.intersection(f).area>1e-8]
 assert abs(sum(t['area_m2'] for t in p['retained_slab_contacts'])-p['pier_footprint_m2'])<1e-6
capcontacts=[]
for c in caps:
 b=c['min_xyz']+c['max_xyz'];f=box(b[0],b[2],b[3],b[5]);overlaps=[]
 for q in parts:
  a=q['bounds'];ds=[min(a[k+3],b[k+3])-max(a[k],b[k]) for k in range(3)]
  if min(ds)>1e-7:overlaps.append(q['id'])
 capcontacts.append({'counterpart':c['id'],'cap_top':83.08,'root_bearing_bottom':83.08,'area_m2':f.area,'overlapping_candidate_solids':overlaps,'actual_counterpart_built':False})
programmes=json.load(open(B/'Game/data/whole_ship_layout.json'))['programmes'];gap=box(58.9,-480,63.57,-386)
neighbors=[p for p in programmes if p['deck'] in ['D11','D12'] and box(p['allocation_x'][0],p['allocation_z'][0],p['allocation_x'][1],p['allocation_z'][1]).distance(gap)<6]
save('SOURCE_INTERFACE_SCREEN.json',{'house_AABB_intrusions':hits,'cap_contacts':capcontacts,'tall_piers_with_exact_slab_contacts':pier,'outboard_gap':{'x_axes':[59.2,63.4],'z_stations':[-480,-386],'center_span_m':94,'candidate_ends_x':54,'nearest_rail_center_distance_m':5.2,'lower_programme_neighbors':neighbors,'contract_missing':'No bounded outboard transfer section, vertical support seats, lower owner clearance or terminal joints specified. Inboard R1 cannot receive this region. No geometry proposed outside R1.','old_rows_remain_omitted':[-459,-406]},'retained_longitudinal_boundary_gaps':{'axes_x':[12.1,42.2,45.8],'fore_source_end_z':-466.2,'fore_R1_start_z':-465.8,'aft_R1_end_z':-398.2,'aft_source_start_z':-397.8,'end_gap_m':0.4,'status':'Independent R1-cap-supported receiver; no claimed continuity to retained longitudinal ends. End splice needs root/house boundary addition beyond R1 envelope.'}})
print('House conservative intrusions',len(hits),'capcontacts',len(capcontacts))
