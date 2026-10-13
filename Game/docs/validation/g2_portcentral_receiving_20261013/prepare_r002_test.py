from pathlib import Path
P=Path(__file__).parent;f=P/'validate_central_receiving.gd';s=f.read_text()
s=s.replace('55.98','25.02').replace('p.guard_preimages[0].name,p.guard_preimages[1].name','p.guard_preimages[0].name,p.guard_preimages[1].name,p.guard_preimages[2].name')
a=s.index(' for part in p.parts:')
s=s[:a]+''' var receiving:Node=ship.get_node("ShipSpace/Districts/StarAtlasD17StandardBatch")
 for mesh:MeshInstance3D in receiving.find_children("*","MeshInstance3D",true,false):
  if str(mesh.name)in[p.guard_preimages[0].name,p.guard_preimages[1].name,p.guard_preimages[2].name]:continue
  var shapes:Array=[]
  for shape:CollisionShape3D in mesh.find_children("*","CollisionShape3D",true,false):shapes.append({"node":shape,"shape":shape.shape,"pose":shape.transform})
  old.append({"node":mesh,"mesh":mesh.mesh,"pose":mesh.global_transform,"material":mesh.material_override,"shapes":shapes})
'''+s[a:]
s=s.replace('Vector3(-63.5,102,-15.1),Vector3(-61.8,102,-14.5),Vector3(-61.8,102,-10),Vector3(-61.8,102,-6),Vector3(-61.8,102,-3.3)','Vector3(-68,102,-15.1)')
s=s.replace('upper_bearings==10','upper_bearings==5').replace('Sixlowerstub andtenupperarrival','Sixlowerstub andfiveupperarrival')
s=s.replace('Vector3(-61.8,102,-2)','Vector3(-65.5,102,-15.1)').replace('Vector3(-61.8,102.03,-2)','Vector3(-65.5,102.03,-15.1)')
s=s.replace('Vector3(-61.8,102,-8),Vector3(-61.8,102,-15.1),','Vector3(-68,102,-15.1),').replace('Vector3(-61.8,102,-15.1),Vector3(-61.8,102,-8),','Vector3(-68,102,-15.1),')
f.write_text(s)
print('R002_ALL_EXISTING_RECEIVING_RESOURCES_PRESERVED_TEST')
