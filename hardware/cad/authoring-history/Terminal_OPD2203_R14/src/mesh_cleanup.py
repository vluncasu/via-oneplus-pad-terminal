"""Remove paired, opposite duplicate triangles generated on coincident CAD seams."""
from collections import defaultdict

def clean(mesh):
    verts,faces=mesh.Topology
    grouped=defaultdict(list)
    for i,f in enumerate(faces):grouped[tuple(sorted(f))].append(i)
    remove=[]
    for ids in grouped.values():
        if len(ids)!=2:continue
        a,b=(faces[i] for i in ids)
        na=(verts[a[1]]-verts[a[0]]).cross(verts[a[2]]-verts[a[0]])
        nb=(verts[b[1]]-verts[b[0]]).cross(verts[b[2]]-verts[b[0]])
        if na.dot(nb)<0:remove.extend(ids)
    if remove:
        mesh.removeFacets(remove)
        mesh.removeDuplicatedPoints()
        mesh.harmonizeNormals()
        mesh.fixIndices()
    return len(remove)
