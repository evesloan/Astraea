"""Keep FONT text editable; discard only microscopic tessellation slivers.
The evaluated native and GLB use the same packed geometry-node modifier.
No label wording, size, placement or retained Catalogue asset is altered.
"""
import bpy
def repair_label(ob):
 assert ob.type=='FONT'
 ob.modifiers.clear()
 g=bpy.data.node_groups.new('EditableLabelSliverRepair','GeometryNodeTree')
 g.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
 g.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
 n=g.nodes;l=g.links;i=n.new('NodeGroupInput');o=n.new('NodeGroupOutput')
 t=n.new('GeometryNodeTriangulate');a=n.new('GeometryNodeInputMeshFaceArea')
 test=n.new('ShaderNodeMath');test.operation='LESS_THAN';test.inputs[1].default_value=1e-8
 d=n.new('GeometryNodeDeleteGeometry');d.domain='FACE';d.mode='ONLY_FACE'
 l.new(i.outputs['Geometry'],t.inputs['Mesh']);l.new(t.outputs['Mesh'],d.inputs['Geometry'])
 l.new(a.outputs['Area'],test.inputs[0]);l.new(test.outputs[0],d.inputs['Selection']);l.new(d.outputs['Geometry'],o.inputs['Geometry'])
 m=ob.modifiers.new('EditableLabelSliverRepair','NODES');m.node_group=g
 ob['label_repair']='Remove evaluated triangles below 1e-8 square metres; editable FONT body preserved'
