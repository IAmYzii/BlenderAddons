import bpy
from . import core


class BAMAT_OT_assign(bpy.types.Operator):
    """Delete all materials on the selected objects and assign the chosen material to the whole object"""
    bl_idname = "object.ba_mat_assign"
    bl_label = "Assign to Selected"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (
            context.mode == 'OBJECT'
            and context.scene.ba_material_assign.material is not None
            and bool(context.selected_objects)
        )

    def execute(self, context):
        mat = context.scene.ba_material_assign.material
        targets = core.supported_targets(context.selected_objects)
        if not targets:
            self.report({'WARNING'}, "No editable mesh/curve objects in the selection")
            return {'CANCELLED'}
        n = core.assign_single_material(targets, mat)
        skipped = len(context.selected_objects) - n
        msg = f"Assigned '{mat.name}' to {n} object(s)"
        if skipped:
            msg += f", skipped {skipped} unsupported/linked"
        self.report({'INFO'}, msg)
        return {'FINISHED'}


class BAMAT_OT_pick_from_active(bpy.types.Operator):
    """Use the active object's active material as the material to assign"""
    bl_idname = "object.ba_mat_pick_from_active"
    bl_label = "Pick from Active"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ob = context.view_layer.objects.active
        return ob is not None and ob.active_material is not None

    def execute(self, context):
        context.scene.ba_material_assign.material = context.view_layer.objects.active.active_material
        return {'FINISHED'}


classes = (BAMAT_OT_assign, BAMAT_OT_pick_from_active)


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
