"""Toolbox-level test: whole package registers, tools can be toggled individually, and a
broken tool does not take the others down.

Run from the repository root: blender -b --factory-startup --python tests/test_toolbox.py
"""
import sys
import os
import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import ba_toolbox  # noqa: E402
from ba_toolbox import registry  # noqa: E402

# 1. Register everything (no preferences reachable headless -> all tools on).
ba_toolbox.register()
assert registry.is_active("exploded_view") and registry.is_active("material_assign")
assert hasattr(bpy.types, "BAEXV_PT_panel") and hasattr(bpy.types, "BAMAT_PT_panel")
assert hasattr(bpy.types.Scene, "ba_exploded_view") and hasattr(bpy.types.Scene, "ba_material_assign")
from ba_toolbox.preferences import BATOOLBOX_Preferences  # noqa: E402
assert BATOOLBOX_Preferences.is_registered
assert set(BATOOLBOX_Preferences.__annotations__) >= {"enable_exploded_view", "enable_material_assign"}

# 2. Toggle one tool off and on again; the other is untouched.
assert registry.set_tool_enabled("material_assign", False)
assert not registry.is_active("material_assign")
assert not hasattr(bpy.types, "BAMAT_PT_panel")
assert hasattr(bpy.types, "BAEXV_PT_panel"), "other tool must stay registered"
assert registry.set_tool_enabled("material_assign", True)
assert hasattr(bpy.types, "BAMAT_PT_panel")

# 3. The tools still work end to end through the toolbox registration.
bpy.ops.wm.read_homefile(use_empty=True)
bpy.ops.mesh.primitive_cube_add(location=(2, 0, 0))
bpy.ops.mesh.primitive_cube_add(location=(-2, 0, 0))
bpy.ops.object.select_all(action='DESELECT')
s = bpy.context.scene.ba_exploded_view
s.distance, s.duration = 1.0, 0.0
assert bpy.ops.object.ba_exv_explode() == {'FINISHED'}
assert abs(bpy.data.objects[0].location.x) == 3.0
assert bpy.ops.object.ba_exv_reset() == {'FINISHED'}
mat = bpy.data.materials.new("M")
bpy.context.scene.ba_material_assign.material = mat
bpy.ops.object.select_all(action='SELECT')
assert bpy.ops.object.ba_mat_assign() == {'FINISHED'}
assert all(o.data.materials[0] is mat for o in bpy.data.objects)

# 4. A tool whose register() raises is reported, not fatal.
class _Broken:
    label = "Broken"
    description = "always fails"

    @staticmethod
    def register():
        raise RuntimeError("boom")

    @staticmethod
    def unregister():
        pass

registry._modules["broken"] = _Broken
assert registry.set_tool_enabled("broken", True) is False
assert "boom" in registry.tool_error("broken")
assert not registry.is_active("broken")
del registry._modules["broken"]
registry._errors.pop("broken", None)

# 5. Full unregister cleans up.
ba_toolbox.unregister()
assert not registry.is_active("exploded_view") and not registry.is_active("material_assign")
assert not hasattr(bpy.types, "BAEXV_PT_panel") and not hasattr(bpy.types, "BAMAT_PT_panel")
assert not BATOOLBOX_Preferences.is_registered

# 6. Register again (simulates re-enable) to make sure nothing leaked.
ba_toolbox.register()
ba_toolbox.unregister()
print("ALL TESTS PASSED")
