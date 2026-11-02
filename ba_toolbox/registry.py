"""Loads tool packages and registers/unregisters them individually.

One failing tool must not take the whole toolbox down: register errors are caught, printed,
and shown in the add-on preferences.
"""
import importlib
import traceback

from .tools import TOOLS

_modules = {}    # name -> imported tool package
_active = set()  # names currently registered
_errors = {}     # name -> last error message


def pref_name(tool_name):
    return f"enable_{tool_name}"


def tool_names():
    return TOOLS


def _load(name):
    if name not in _modules:
        _modules[name] = importlib.import_module(f"{__package__}.tools.{name}")
    return _modules[name]


def tool_info(name):
    try:
        mod = _load(name)
        return {
            "label": getattr(mod, "label", name),
            "description": getattr(mod, "description", ""),
        }
    except Exception as ex:  # import error: still show the toggle, with the error
        _errors[name] = f"{type(ex).__name__}: {ex}"
        return {"label": name, "description": ""}


def tool_error(name):
    return _errors.get(name)


def is_active(name):
    return name in _active


def reload_tools():
    """Reload every imported tool package (their own __init__ reloads their submodules)."""
    for name, mod in list(_modules.items()):
        try:
            _modules[name] = importlib.reload(mod)
        except Exception:
            traceback.print_exc()


def set_tool_enabled(name, enabled):
    if enabled and name not in _active:
        try:
            _load(name).register()
        except Exception as ex:
            _errors[name] = f"{type(ex).__name__}: {ex}"
            print(f"[BA Toolbox] failed to register tool '{name}':")
            traceback.print_exc()
            return False
        _errors.pop(name, None)
        _active.add(name)
    elif not enabled and name in _active:
        try:
            _modules[name].unregister()
        except Exception:
            print(f"[BA Toolbox] error while unregistering tool '{name}':")
            traceback.print_exc()
        _active.discard(name)
    return True


def register_enabled(is_enabled):
    """Register every tool for which is_enabled(name) is True."""
    for name in TOOLS:
        if is_enabled(name):
            set_tool_enabled(name, True)


def unregister_all():
    for name in reversed(TOOLS):
        if name in _active:
            set_tool_enabled(name, False)
