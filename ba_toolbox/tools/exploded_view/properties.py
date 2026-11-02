import bpy
from bpy.props import FloatProperty, EnumProperty, PointerProperty


def _on_change(self, context):
    # Live update: re-apply the explosion to everything currently exploded.
    from . import core
    core.reapply_all(context)


class BAEXV_Settings(bpy.types.PropertyGroup):
    distance: FloatProperty(
        name="Distance",
        description="Base explosion distance (Distance mode) or scale factor (Scale mode)",
        default=1.0,
        min=0.0,
        soft_max=20.0,
        subtype='DISTANCE',
        update=_on_change,
    )
    duration: FloatProperty(
        name="Animation",
        description="How long Explode and Reset take to animate, in seconds (0 = instant)",
        default=0.3,
        min=0.0,
        soft_max=2.0,
        subtype='TIME_ABSOLUTE',
        unit='TIME_ABSOLUTE',
    )
    center: EnumProperty(
        name="Center",
        description="Point the objects explode away from",
        items=(
            ('BOUNDS', "Bounds Center", "Center of the combined bounding box of the exploded objects"),
            ('ACTIVE', "Active Object", "Center of the active object"),
            ('CURSOR', "3D Cursor", "The 3D cursor location"),
        ),
        default='BOUNDS',
        update=_on_change,
    )
    mode: EnumProperty(
        name="Mode",
        description="How the offset is computed",
        items=(
            ('DISTANCE', "Distance", "Every object travels the same distance away from the center"),
            ('SCALE', "Scale", "Offset is proportional to the distance from the center (Houdini default)"),
        ),
        default='DISTANCE',
        update=_on_change,
    )


def register():
    bpy.utils.register_class(BAEXV_Settings)
    bpy.types.Scene.ba_exploded_view = PointerProperty(type=BAEXV_Settings)


def unregister():
    del bpy.types.Scene.ba_exploded_view
    bpy.utils.unregister_class(BAEXV_Settings)
