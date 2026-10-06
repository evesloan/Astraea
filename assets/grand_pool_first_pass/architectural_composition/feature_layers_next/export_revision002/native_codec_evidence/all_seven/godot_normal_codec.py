"""Source-derived float32 model of Godot 4.6.3 uncompressed-attribute normal codec.
Not an acceptance tolerance. Actual native arrays must independently confirm it.
"""
import numpy as np
SOURCES={
 'normal_encode':'https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/servers/rendering/rendering_server.cpp#L557',
 'normal_decode':'https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/servers/rendering/rendering_server.cpp#L1377',
 'octahedron':'https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/core/math/vector3.cpp#L84',
 'float32_normalize':'https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/core/math/vector3.h#L500'}
def roundtrip(normals):
 n=np.asarray(normals,dtype=np.float32);shape=n.shape;n=n.reshape(-1,3)
 den=(np.abs(n[:,0])+np.abs(n[:,1]))+np.abs(n[:,2]);u=n/den[:,None]
 ox=np.where(u[:,2]>=0,u[:,0],(np.float32(1)-np.abs(u[:,1]))*np.where(u[:,0]>=0,np.float32(1),np.float32(-1)))
 oy=np.where(u[:,2]>=0,u[:,1],(np.float32(1)-np.abs(u[:,0]))*np.where(u[:,1]>=0,np.float32(1),np.float32(-1)))
 oct=np.stack([ox*np.float32(.5)+np.float32(.5),oy*np.float32(.5)+np.float32(.5)],axis=1).astype(np.float32)
 # C++ cast truncates after clamped float32 multiplication, not nearest rounding.
 packed=np.clip(oct*np.float32(65535),0,65535).astype(np.uint16)
 # RenderingServer uses double division into float32 Vector2 components.
 dec=(packed.astype(np.float64)/65535.0).astype(np.float32)
 f=dec*np.float32(2)-np.float32(1)
 z=(np.float32(1)-np.abs(f[:,0]))-np.abs(f[:,1]);t=np.clip(-z,np.float32(0),np.float32(1))
 x=f[:,0]+np.where(f[:,0]>=0,-t,t);y=f[:,1]+np.where(f[:,1]>=0,-t,t)
 vec=np.stack([x,y,z],axis=1).astype(np.float32);length=np.sqrt((x*x+y*y)+z*z).astype(np.float32)
 decoded=(vec/length[:,None]).astype(np.float32)
 return decoded.reshape(shape),packed.reshape(shape[:-1]+(2,))
