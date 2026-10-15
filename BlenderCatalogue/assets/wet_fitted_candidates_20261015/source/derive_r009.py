from pathlib import Path
import json
D=Path(__file__).resolve().parent;s=(D/'build_fitted_r008.py').read_text().replace('r008','r009').replace('R008','R009').replace('F008','F009');s=s.replace('meshes_by_kit={}','meshes_by_kit={};fixture_mounts=[]');old="  box(col,kit+'_F009_RaisedCanopyLightMount',(73.945,107.38,-379.055),(74.055,107.46,-378.945),metal)\n";assert old in s;s=s.replace(old,'')
anchor=' bpy.context.view_layer.update()\n for row in original_data'
insert=''' # Positive fixture-to-ceiling adapters;original fixture parts and source exit markers are unchanged.
 from mathutils.bvhtree import BVHTree
 bpy.context.view_layer.update()
 for name in[n for n in made if n.endswith('_Mount')and n.startswith(('WetLight','DryLight'))]:
  a,b=bounds(made[name]);cx=(a.x+b.x)/2;cz=(a.z+b.z)/2;target='';top=None
  if name.startswith('DryLight'):
   top=106.02 if kit=='TIDAL'and name=='DryLight-2_Mount'else 105.4;target='Retained_TG_Batch_283'if top>106 else 'ChangingRoof'
  elif kit=='QUIET'and name=='WetLight-6_Mount':top=107.4;target='Retained_QG_Batch_172_Raised2.2m'
  else:
   hits=[]
   for roof_name in['RoofPanel0','RoofPanel1']:
    roof=made[roof_name];verts=[Gv(roof.matrix_world@v.co)for v in roof.data.vertices];polys=[list(p.vertices)for p in roof.data.polygons];tree=BVHTree.FromPolygons(verts,polys);loc,normal,index,distance=tree.ray_cast(Vector((cx,b.y+.001,cz)),Vector((0,1,0)),2)
    if loc is not None:hits.append((loc.y,roof_name))
   assert hits,(kit,name,'No actual overhead face');top,target=min(hits)
  assert top>=b.y-.001,(kit,name,top,b.y)
  adapter=kit+'_F009_FixtureAdapter_'+name
  if kit=='TIDAL'and name=='DryLight-2_Mount':adapter=kit+'_F009_UtilityLightMount'
  else:box(col,adapter,(cx-.045,b.y-.02,cz-.045),(cx+.045,top+.02,cz+.045),metal)
  fixture_mounts.append({'kit':kit,'source_mount':made[name].name,'adapter':adapter,'base_y':b.y-.02,'ceiling_pin_xyz':[cx,top,cz],'target':target,'positive_contact_m':.02})
'''
assert anchor in s;s=s.replace(anchor,insert+anchor);s=s.replace("'lights':lights,'doors':doors", "'lights':lights,'doors':doors,'fixture_mounts':fixture_mounts");(D/'build_fitted_r009.py').write_text(s)
p=json.loads((D/'FITTED_SUCCESSOR_PLAN_r008.json').read_text());p.update(schema='astraea.wet_fitted_successor.r009',status='R009_POSITIVE_FIXTURE_MOUNTS_AND_READING_GROUP_NATIVE_PENDING');p['QUIET']['existing_reading_group_translation_xyz']=[-2.5,0,.8];p['both']['physical_fixture_ceiling_mounts']=14;(D/'FITTED_SUCCESSOR_PLAN_r009.json').write_text(json.dumps(p,indent=2)+'\n');(D/'verify_rigid_r009.py').write_text((D/'verify_rigid_r008.py').read_text().replace('r008','r009'))
