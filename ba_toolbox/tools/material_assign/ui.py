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

        targets = core.supported_targets(context.selected_objects)
        n = len(targets)
        col = layout.column()
        col.scale_y = 1.4
        col.operator("object.ba_mat_assign", icon='MATERIAL', text=f"Assign to Selected ({n})")

        if s.material is None:
            layout.label(text="Pick a material first", icon='INFO')
            return
        if n == 0:
            layout.label(text="Select mesh or curve objects", icon='INFO')
            return

        rows, kept, removed = core.material_changes(targets, s.material)
        box = layout.box()
        header = box.row()
        header.label(text=f"Keep {kept}", icon='CHECKMARK')
        sub = header.row()
        sub.alert = removed > 0
        sub.label(text=f"Remove {removed}", icon='X')

        for obj, entries in rows[:MAX_ROWS]:
            box.label(text=obj.name, icon=_OBJ_ICONS.get(obj.type, 'OBJECT_DATA'))
            if not entries:
                r = box.row()
                r.active = False
                r.label(text="(no material)  →  " + s.material.name, icon='ADD')
                continue
            for mat, keep in entries:
                r = box.row(align=True)
                r.separator(factor=2.0)
                name = mat.name if mat is not None else "(empty slot)"
                if keep:
                    r.label(text=name, icon='CHECKMARK')
                else:
                    r.alert = True
                    r.label(text=name, icon='X')
        if len(rows) > MAX_ROWS:
            box.label(text=f"... and {len(rows) - MAX_ROWS} more object(s)")


MAX_ROWS = 25
_OBJ_ICONS = {
    'MESH': 'OUTLINER_OB_MESH',
    'CURVE': 'OUTLINER_OB_CURVE',
    'SURFACE': 'OUTLINER_OB_SURFACE',
    'FONT': 'OUTLINER_OB_FONT',
    'META': 'OUTLINER_OB_META',
}


def register():
    bpy.utils.register_class(BAMAT_PT_panel)


def unregister():
    bpy.utils.unregister_class(BAMAT_PT_panel)
