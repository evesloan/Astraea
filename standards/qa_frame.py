"""Cheap conservative framing check before a full-silhouette component render.

Ignore inspection floors/lights/proxies unless they are meant to fit in frame.
Ordinary eye-height views may intentionally crop; record the report instead of
asserting full framing for those. This never moves a camera or edits a source.
"""
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
def frame_report(scene,camera,objects,margin=.04):
 for layer in scene.view_layers:layer.update()
 points=[world_to_camera_view(scene,camera,o.matrix_world@Vector(c)) for o in objects if o.type in ('MESH','CURVE') for c in o.bound_box]
 if not points:return {'passes':False,'reason':'No component bounds supplied'}
 lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
 return {'passes':lo[0]>=margin and lo[1]>=margin and hi[0]<=1-margin and hi[1]<=1-margin and lo[2]>=camera.data.clip_start and hi[2]<=camera.data.clip_end,'uv_depth_min':lo,'uv_depth_max':hi,'margin':margin,'bounds_points':len(points),'scope':'Conservative component-bounds framing only, not visibility or collision'}
def assert_full_frame(scene,camera,objects,margin=.04):
 result=frame_report(scene,camera,objects,margin)
 if not result['passes']:raise ValueError('Component framing preflight failed: '+str(result))
 return result
