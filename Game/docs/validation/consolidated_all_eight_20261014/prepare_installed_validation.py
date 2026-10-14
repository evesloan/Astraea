from pathlib import Path
P=Path(__file__).parent;src=(P/'validate_combined_default.gd').read_text().replace('var installed_mode:=false','var installed_mode:=true')
anchor=' FileAccess.open(P+"COMBINED_DEFAULT_RUNTIME.json"'
i=src.index(anchor)
extra=''' var receiver_plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"CONSOLIDATED_PLAN.json"));var floor_rows:Array=[];var entry_rows:Array=[];var wet_rows:Array=[]
 for row in receiver_plan.G2_floor_rows:
  var misses:=0
  for tri in row.triangles:
   var at_floor:=Vector3((tri[0][0]+tri[1][0]+tri[2][0])/3.,row.floor_y,(tri[0][1]+tri[1][1]+tri[2][1])/3.);var hit:Dictionary=ray(space,at_floor+Vector3.UP*.02,at_floor-Vector3.UP*.02)
   if hit.is_empty()or absf(hit.position.y-at_floor.y)>.002 or hit.normal.y<.99:misses+=1
  floor_rows.append({"owner":row.source_owner,"id":row.id,"samples":row.triangles.size(),"missing_samples":misses})
 for home in receiver_plan.G2_homes:
  var at_entry:=Vector3(home.entry[0],home.entry[1],home.entry[2]);var hit:Dictionary=ray(space,at_entry+Vector3.UP*.02,at_entry-Vector3.UP*.02);entry_rows.append({"key":home.key,"floor_present":not hit.is_empty()and absf(hit.position.y-at_entry.y)<.002})
 for candidate in receiver_plan.G2_wet.candidate_transforms:
  for dx in[-16.,0.,16.]:
   for dz in[-13.,0.,13.]:
    var x:float=candidate.world_xyz[0]+dx;var z:float=candidate.world_xyz[2]+dz;var at_floor:=Vector3(x,102,z);var at_roof:=Vector3(x,106.26,z);var floor:Dictionary=ray(space,at_floor+Vector3.UP*.02,at_floor-Vector3.UP*.02);var roof_hit:Dictionary=ray(space,at_roof+Vector3.UP*.02,at_roof-Vector3.UP*.02);wet_rows.append({"kit":candidate.kit,"x":x,"z":z,"receiving_floor_present":not floor.is_empty(),"required_roof_present":not roof_hit.is_empty(),"floor_path":str(floor.collider.get_path())if not floor.is_empty()else"","roof_path":str(roof_hit.collider.get_path())if not roof_hit.is_empty()else""})
 var group_presence:Dictionary={"G1":ship.find_child("StarAtlasD17StandardBatch",true,false)!=null,"G2":ship.get_node_or_null("ShipSpace/Group2PortCentralSupportedPair")!=null,"G3":clinical!=null,"G4":ship.get_node_or_null("ShipSpace/Districts/Group4Completion")!=null,"G5":ship.get_node_or_null("ShipSpace/Districts/ShoppingPromenadeChunks")!=null,"G6":ship.find_child("Group6Completion",true,false)!=null,"G7":n!=null,"G8":ship.find_child("Group8CrownInteriors",true,false)!=null}
 FileAccess.open(P+"INSTALLED_COMBINED_RECEIVER_SURVEY.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_INSTALLED_COMBINED_RECEIVER_SURVEY","G2_floor_rows":floor_rows,"G2_home_entries":entry_rows,"wet_roof_and_floor_witnesses":wet_rows,"all_eight_runtime_roots":group_presence,"further_source_geometry_adopted":false},"  "))
'''
src=src[:i]+extra+src[i:];src=src.replace('P+"COMBINED_DEFAULT_RUNTIME.json"','P+"INSTALLED_COMBINED_RUNTIME.json"');(P/'validate_installed_combined.gd').write_text(src)
print('INSTALLED_COMBINED_VALIDATION_AND_FINAL_RECEIVER_SURVEY_PREPARED')
