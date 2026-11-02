"""Run with: blender -b --python tests/test_headless.py"""
import sys
import os
import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import ba_exploded_view  # noqa: E402
from ba_exploded_view import core  # noqa: E402

ba_exploded_view.register()
bpy.ops.wm.read_homefile(use_empty=True)
ctx = bpy.context
s = ctx.scene.ba_exploded_view


def close(a, b, eps=1e-5):
    return (Vector(a) - Vector(b)).length < eps


def cube(name, loc):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = ctx.active_object
    o.name = name
    return o


a = cube("A", (-2, 0, 0))
b = cube("B", (2, 0, 0))
c = cube("C", (0, 3, 0))
bpy.ops.object.light_add(type='POINT', location=(0, 0, 5))
light = ctx.active_object
bpy.ops.object.select_all(action='DESELECT')

# 1. Explode all (nothing selected), distance mode.
s.distance, s.extra, s.mode, s.center = 1.0, 0.0, 'DISTANCE', 'BOUNDS'
assert bpy.ops.object.ba_exv_explode() == {'FINISHED'}
# bounds center = (0, 1.5, 0)
assert close(a.location, Vector((-2, 0, 0)) + Vector((-2, -1.5, 0)).normalized())
assert close(b.location, Vector((2, 0, 0)) + Vector((2, -1.5, 0)).normalized())
assert close(c.location, (0, 4, 0))
assert close(light.location, (0, 0, 5)), "light must not move"
assert core.is_exploded(a) and not core.is_exploded(light)

# 2. Re-explode with bigger distance: no compounding.
s.distance = 3.0  # update callback re-applies
assert close(c.location, (0, 6, 0)), c.location
bpy.ops.object.ba_exv_explode()
assert close(c.location, (0, 6, 0)), "explode must not compound"

# 3. Extra adds on top.
s.extra = 1.0
assert close(c.location, (0, 7, 0))

# 4. Scale mode.
s.mode = 'SCALE'
s.distance, s.extra = 1.0, 0.0  # factor 1 => doubles offset from center
assert close(c.location, (0, 4.5, 0)), c.location

# 5. Reset all.
assert bpy.ops.object.ba_exv_reset() == {'FINISHED'}
assert close(a.location, (-2, 0, 0)) and close(b.location, (2, 0, 0)) and close(c.location, (0, 3, 0))
assert not any(core.is_exploded(o) for o in ctx.scene.objects)
assert not bpy.ops.object.ba_exv_reset.poll()

# 6. Selection only.
s.mode, s.distance = 'DISTANCE', 2.0
a.select_set(True)
b.select_set(True)
ctx.view_layer.objects.active = a
bpy.ops.object.ba_exv_explode()
assert close(a.location, (-4, 0, 0)) and close(b.location, (4, 0, 0))
assert close(c.location, (0, 3, 0)) and not core.is_exploded(c)

# 7. Reset selection only, then reset the rest.
bpy.ops.object.select_all(action='DESELECT')
a.select_set(True)
bpy.ops.object.ba_exv_reset()
assert close(a.location, (-2, 0, 0)) and close(b.location, (4, 0, 0))
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.ba_exv_reset()
assert close(b.location, (2, 0, 0))

# 8. Parented child with a rotated parent: world offset is correct, child not double-moved.
bpy.ops.object.empty_add(location=(5, 0, 0))
parent = ctx.active_object
parent.rotation_euler = (0, 0, 1.5707963)  # 90 deg about Z
d = cube("D", (5, 2, 0))
d.parent = parent
d.matrix_parent_inverse = parent.matrix_world.inverted()
ctx.view_layer.update()
before = core.world_bbox_center(d).copy()
bpy.ops.object.select_all(action='DESELECT')
parent.select_set(True)
d.select_set(True)
s.center = 'CURSOR'
ctx.scene.cursor.location = (5, 0, 0)
s.distance = 1.0
bpy.ops.object.ba_exv_explode()
ctx.view_layer.update()
assert core.is_exploded(parent) and not core.is_exploded(d), "nested child must be skipped"
# parent sits at the cursor -> zero direction -> no move; so D also stays.
assert close(core.world_bbox_center(d), before)
bpy.ops.object.ba_exv_reset()
# Now explode only the child; its world offset must be +Y by 1 regardless of parent rotation.
bpy.ops.object.select_all(action='DESELECT')
d.select_set(True)
bpy.ops.object.ba_exv_explode()
ctx.view_layer.update()
assert close(core.world_bbox_center(d), before + Vector((0, 1, 0))), core.world_bbox_center(d)
bpy.ops.object.ba_exv_reset()
ctx.view_layer.update()
assert close(core.world_bbox_center(d), before)

ba_exploded_view.unregister()
print("ALL TESTS PASSED")
