import bpy
from . import core


class BAMAT_PT_panel(bpy.types.Panel):
    bl_label = "Material Assign"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Toolbox"  # shared sidebar tab for all add-ons in this repository

    def draw(self, context):
        layout = self.layout
        s = context.scene.ba_material_assign

        row = layout.row(align=True)
        row.prop(s, "material", text="")
        row.operator("object.ba_mat_pick_from_active", text="", icon='EYEDROPPER')

        n = len(core.supported_targets(context.selected_objects))
        col = layout.column()
        col.scale_y = 1.4
        col.operator("object.ba_mat_assign", icon='MATERIAL', text=f"Assign to Selected ({n})")

        if s.material is None:
            layout.label(text="Pick a material first", icon='INFO')
        elif n == 0:
            layout.label(text="Select mesh or curve objects", icon='INFO')


def register():
    bpy.utils.register_class(BAMAT_PT_panel)


def unregister():
    bpy.utils.unregister_class(BAMAT_PT_panel)
