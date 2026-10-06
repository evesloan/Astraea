"""Pure float32 model of Blender 4.3.2 mathutils Matrix arithmetic.
Source references: mathutils_Matrix.cc inverse cofactor and Matrix_matmul;
math_matrix_c.cc determinant_m2/m3/m4 and adjoint_m4_m4. This does not invoke
Blender, load a blend or substitute geometry. Float32 products, float64 dot sum,
then float32 storage match Matrix @ Matrix (different from numpy float32 BLAS).
"""
import numpy as np
F=np.float32

def determinant(m):
    m=np.asarray(m,dtype=np.float32);n=len(m)
    if n==2:return F(F(m[0,0]*m[1,1])-F(m[0,1]*m[1,0]))
    # Blender's determinant_m3/m4 expand down the first column, left-to-right.
    terms=[F(m[i,0]*determinant(np.delete(np.delete(m,i,axis=0),0,axis=1))) for i in range(n)]
    r=terms[0]
    for i in range(1,n):r=F(r+terms[i]) if i%2==0 else F(r-terms[i])
    return r

def inverted_safe_nonsingular(m):
    m=np.asarray(m,dtype=np.float32);d=determinant(m);assert d!=0
    adj=np.empty((4,4),dtype=np.float32)
    for i in range(4):
        for j in range(4):
            v=determinant(np.delete(np.delete(m,j,axis=0),i,axis=1))
            adj[i,j]=F((v if (i+j)%2==0 else -v)/d)
    return adj

def mathutils_matmul(a,b):
    a=np.asarray(a,dtype=np.float32);b=np.asarray(b,dtype=np.float32)
    return np.array([[sum(float(F(a[i,k]*b[k,j])) for k in range(4)) for j in range(4)]for i in range(4)],dtype=np.float32)
