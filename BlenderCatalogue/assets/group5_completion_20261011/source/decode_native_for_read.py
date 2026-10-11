"""Lossless Zstandard transport decoding only; do not save with older Blender.
Originals remain byte-identical. Every decoded mesh is compared separately at read.
Uses the installed system libzstd without installation or network transfer.
"""
from pathlib import Path
import ctypes as C,ctypes.util,hashlib,json
P=Path(__file__).resolve().parents[1];OLD=P.parent/'shopping_promenade_20261009/source/natives'
OUT=Path('/tmp/group5-native-read');OUT.mkdir(exist_ok=True)
lib=C.CDLL(ctypes.util.find_library('zstd'))
class Buffer(C.Structure):_fields_=[('src',C.c_void_p),('size',C.c_size_t),('pos',C.c_size_t)]
lib.ZSTD_createDStream.restype=C.c_void_p
lib.ZSTD_initDStream.argtypes=[C.c_void_p];lib.ZSTD_initDStream.restype=C.c_size_t
lib.ZSTD_decompressStream.argtypes=[C.c_void_p,C.POINTER(Buffer),C.POINTER(Buffer)];lib.ZSTD_decompressStream.restype=C.c_size_t
lib.ZSTD_isError.argtypes=[C.c_size_t];lib.ZSTD_isError.restype=C.c_uint
lib.ZSTD_freeDStream.argtypes=[C.c_void_p]
records=[]
for native in OLD.glob('*.blend'):
    compressed=native.read_bytes();src=C.create_string_buffer(compressed);inp=Buffer(C.cast(src,C.c_void_p),len(compressed),0)
    stream=lib.ZSTD_createDStream();assert not lib.ZSTD_isError(lib.ZSTD_initDStream(stream))
    decoded=bytearray()
    while inp.pos<inp.size:
        dst=C.create_string_buffer(4*1024*1024);out=Buffer(C.cast(dst,C.c_void_p),len(dst),0)
        ret=lib.ZSTD_decompressStream(stream,C.byref(out),C.byref(inp));assert not lib.ZSTD_isError(ret)
        decoded.extend(dst.raw[:out.pos])
    lib.ZSTD_freeDStream(stream)
    assert decoded[:7]==b'BLENDER'
    (OUT/native.name).write_bytes(decoded)
    records.append({'native':str(native.relative_to(P.parents[2])),'original_sha256':hashlib.sha256(compressed).hexdigest(),'decoded_sha256':hashlib.sha256(decoded).hexdigest(),'decoded_header':bytes(decoded[:12]).decode('ascii'),'decoded_bytes':len(decoded),'scope':'lossless container decoding for read only; no native authoring/resave'})
(P/'qa/READ_ONLY_NATIVE_TRANSPORT.json').write_text(json.dumps(records,indent=2)+'\n')
print('DECODED_READ_ONLY',len(records))
