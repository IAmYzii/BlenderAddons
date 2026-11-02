# BA Toolbox: one Blender extension bundling several small tools. Each tool is a package
# under tools/ with its own register()/unregister(); the add-on preferences let you switch
# individual tools on and off.
#
# Reload support: when Blender runs "Reload Scripts" (F3 > Reload Scripts), this file is
# executed again with its previous globals. Reload our modules and every loaded tool
# package explicitly, otherwise the old versions stay cached in sys.modules.
if "bpy" in locals():
    import importlib
    registry = importlib.reload(registry)  # noqa: F821
    preferences = importlib.reload(preferences)  # noqa: F821
    registry.reload_tools()
else:
    import bpy  # noqa: F401
    from . import registry, preferences


def register():
    preferences.register()
    registry.register_enabled(preferences.enabled_in_prefs)


def unregister():
    registry.unregister_all()
    preferences.unregister()
