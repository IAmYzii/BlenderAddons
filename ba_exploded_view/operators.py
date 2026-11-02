import bpy
from . import core


class BAEXV_OT_explode(bpy.types.Operator):
    """Explode selected objects (or all visible objects if nothing is selected) away from the center"""
    bl_idname = "object.ba_exv_explode"
    bl_label = "Explode"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        objs = core.collect_targets(context)
        if not objs:
            self.report({'WARNING'}, "No objects to explode")
            return {'CANCELLED'}
        n = core.apply_explosion(context, objs, context.scene.ba_exploded_view, animate=True)
        self.report({'INFO'}, f"Exploded {n} object(s)")
        return {'FINISHED'}


class BAEXV_OT_reset(bpy.types.Operator):
    """Restore exploded objects to their original positions (selection, or all if nothing is selected)"""
    bl_idname = "object.ba_exv_reset"
    bl_label = "Reset"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and any(core.is_exploded(o) for o in context.scene.objects)

    def execute(self, context):
        sel = [o for o in context.selected_objects if core.is_exploded(o)]
        objs = sel if sel else [o for o in context.scene.objects if core.is_exploded(o)]
        n = core.reset_objects(objs, context.scene.ba_exploded_view.duration)
        self.report({'INFO'}, f"Reset {n} object(s)")
        return {'FINISHED'}


classes = (BAEXV_OT_explode, BAEXV_OT_reset)


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
