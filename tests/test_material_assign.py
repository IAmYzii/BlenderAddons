"""Run from the repository root: blender -b --factory-startup --python tests/test_material_assign.py"""
import sys
import os
import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import ba_material_assign  # noqa: E402
from ba_material_assign import core  # noqa: E402

ba_material_assign.register()
bpy.ops.wm.read_homefile(use_empty=True)
ctx = bpy.context
s = ctx.scene.ba_material_assign

red = bpy.data.materials.new("Red")
green = bpy.data.materials.new("Green")
blue = bpy.data.materials.new("Blue")
target = bpy.data.materials.new("Target")


def cube(name, mats):
    bpy.ops.mesh.primitive_cube_add()
    o = ctx.active_object
    o.name = name
    for m in mats:
        o.data.materials.append(m)
    # spread faces across slots
    for i, p in enumerate(o.data.polygons):
        p.material_index = i % max(1, len(mats))
    return o


a = cube("A", [red, green, blue])
b = cube("B", [green])
c = cube("C", [])  # no slots at all
# object-level slot link on A's second slot
a.material_slots[1].link = 'OBJECT'
a.material_slots[1].material = blue

bpy.ops.curve.primitive_bezier_circle_add()
curve = ctx.active_object
curve.data.materials.append(red)
curve.data.materials.append(green)
curve.data.splines[0].material_index = 1

bpy.ops.object.light_add(type='POINT')
light = ctx.active_object

bpy.ops.object.empty_add()
empty = ctx.active_object

# 1. Poll: needs a material and a selection.
bpy.ops.object.select_all(action='DESELECT')
s.material = None
assert not bpy.ops.object.ba_mat_assign.poll()
s.material = target
assert not bpy.ops.object.ba_mat_assign.poll(), "no selection -> disabled"
for o in (a, b, c, curve, light, empty):
    o.select_set(True)
ctx.view_layer.objects.active = a
assert bpy.ops.object.ba_mat_assign.poll()

# 2. Assign.
assert bpy.ops.object.ba_mat_assign() == {'FINISHED'}
for o in (a, b, c):
    assert len(o.data.materials) == 1 and o.data.materials[0] is target, (o.name, list(o.data.materials))
    assert all(p.material_index == 0 for p in o.data.polygons), o.name
    assert all(sl.link == 'DATA' and sl.material is target for sl in o.material_slots), o.name
assert len(curve.data.materials) == 1 and curve.data.materials[0] is target
assert curve.data.splines[0].material_index == 0
assert core.supported_targets([light, empty]) == []

# 3. Materials themselves are not deleted from the file.
assert bpy.data.materials.get("Red") is red and bpy.data.materials.get("Blue") is blue

# 4. Shared mesh data: two objects, one mesh, processed once and consistently.
d1 = cube("D1", [red, green])
d2 = bpy.data.objects.new("D2", d1.data)
ctx.collection.objects.link(d2)
bpy.ops.object.select_all(action='DESELECT')
d1.select_set(True)
d2.select_set(True)
s.material = blue
bpy.ops.object.ba_mat_assign()
assert [m for m in d1.data.materials] == [blue]
assert all(sl.material is blue for sl in d2.material_slots)

# 5. Pick from active.
ctx.view_layer.objects.active = a  # A now has Target
a.select_set(True)
assert bpy.ops.object.ba_mat_pick_from_active.poll()
bpy.ops.object.ba_mat_pick_from_active()
assert s.material is target

# 6. Idempotent.
bpy.ops.object.ba_mat_assign()
assert len(a.data.materials) == 1 and a.data.materials[0] is target

ba_material_assign.unregister()
print("ALL TESTS PASSED")
