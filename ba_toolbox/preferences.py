import bpy
from bpy.props import BoolProperty

from . import registry


def _make_update(tool_name):
    def _update(self, context):
        registry.set_tool_enabled(tool_name, getattr(self, registry.pref_name(tool_name)))
    return _update


class BATOOLBOX_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        layout.label(text="Enabled tools (each adds a panel to the Toolbox sidebar tab):")
        col = layout.column(align=True)
        for name in registry.tool_names():
            info = registry.tool_info(name)
            row = col.row(align=True)
            row.prop(self, registry.pref_name(name), text="")
            sub = row.row()
            sub.active = getattr(self, registry.pref_name(name))
            sub.label(text=info["label"])
            sub.label(text=info["description"])
            err = registry.tool_error(name)
            if err:
                erow = col.row()
                erow.alert = True
                erow.label(text=f"    {name}: {err}", icon='ERROR')


def _add_toggle_properties():
    for name in registry.tool_names():
        info = registry.tool_info(name)
        BATOOLBOX_Preferences.__annotations__[registry.pref_name(name)] = BoolProperty(
            name=info["label"],
            description=info["description"],
            default=True,
            update=_make_update(name),
        )


def enabled_in_prefs(tool_name):
    """Read the toggle for a tool; True when preferences are not reachable (e.g. headless)."""
    try:
        prefs = bpy.context.preferences.addons[__package__].preferences
    except (KeyError, AttributeError):
        return True
    return getattr(prefs, registry.pref_name(tool_name), True)


def register():
    _add_toggle_properties()
    bpy.utils.register_class(BATOOLBOX_Preferences)


def unregister():
    bpy.utils.unregister_class(BATOOLBOX_Preferences)
