import bpy
from . import core


class BAEXV_PT_panel(bpy.types.Panel):
    bl_label = "Exploded View"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Exploded View"

    def draw(self, context):
        layout = self.layout
        s = context.scene.ba_exploded_view

        col = layout.column(align=True)
        col.prop(s, "distance")
        col.prop(s, "extra")
        layout.prop(s, "mode", expand=True)
        layout.prop(s, "center")

        row = layout.row(align=True)
        row.scale_y = 1.4
        row.operator("object.ba_exv_explode", icon='MOD_EXPLODE')
        row.operator("object.ba_exv_reset", icon='LOOP_BACK')

        n = sum(1 for o in context.scene.objects if core.is_exploded(o))
        sel = len([o for o in context.selected_objects if o.type not in core.SKIP_TYPES])
        target = "selection (%d)" % sel if sel else "all visible"
        box = layout.box()
        box.label(text="Exploded: %d" % n, icon='INFO')
        box.label(text="Target: " + target)


def register():
    bpy.utils.register_class(BAEXV_PT_panel)


def unregister():
    bpy.utils.unregister_class(BAEXV_PT_panel)
