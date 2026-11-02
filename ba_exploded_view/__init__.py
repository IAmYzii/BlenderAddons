# Reload support: when Blender runs "Reload Scripts" (F3 > Reload Scripts, or
# bpy.ops.script.reload()), this file is executed again with its previous
# globals. Reload every submodule explicitly, otherwise the old versions stay
# cached in sys.modules and edits appear to have no effect.
if "bpy" in locals():
    import importlib
    for _m in (core, properties, operators, ui):  # noqa: F821  (core first: others import it)
        importlib.reload(_m)
else:
    import bpy  # noqa: F401
    from . import core, properties, operators, ui

_modules = (properties, operators, ui)


def register():
    for m in _modules:
        m.register()


def unregister():
    for m in reversed(_modules):
        m.unregister()
