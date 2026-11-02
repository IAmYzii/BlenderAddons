import bpy
from bpy.props import PointerProperty


class BAMAT_Settings(bpy.types.PropertyGroup):
    material: PointerProperty(
        name="Material",
        description="Material that will replace every material on the selected objects",
        type=bpy.types.Material,
    )


def register():
    bpy.utils.register_class(BAMAT_Settings)
    bpy.types.Scene.ba_material_assign = PointerProperty(type=BAMAT_Settings)


def unregister():
    del bpy.types.Scene.ba_material_assign
    bpy.utils.unregister_class(BAMAT_Settings)
