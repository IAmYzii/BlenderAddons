# BlenderAddons

Collection of Blender add-ons. Each add-on lives in its own top-level folder.

| Add-on | Folder | Description |
|---|---|---|
| BA Exploded View | [`ba_exploded_view/`](ba_exploded_view/) | Houdini-style exploded view for selected or all objects |

## Repository conventions

### Branching

- `main` holds only tested, working features. Nothing is developed directly on `main`.
- Every add-on (feature) has its own active branch, named after the add-on, for example `exploded-view`.
  All work on that add-on happens on its branch.
- Merge a feature branch into `main` only when the feature is tested and working. Use a merge
  commit (`git merge --no-ff <branch>`) so the branch history stays visible.
- After merging, keep the feature branch alive and continue development there. Merge into `main`
  again when the next batch of changes is tested.

### Add-on layout

- Each add-on folder is a complete Blender extension: `blender_manifest.toml`, `__init__.py`,
  its modules, and its own `README.md`.
- The add-on's `README.md` documents that add-on only: what it does, how to use it, how to
  install it, and how to test it. This root README only lists the add-ons and the conventions.
- Every add-on puts its 3D Viewport sidebar panel in the shared **Toolbox** tab
  (`bl_category = "Toolbox"`), with the add-on name as the panel label. One tab for all tools
  keeps the sidebar tidy as the collection grows.
- Tests for an add-on go in `tests/` and run headless, for example
  `blender -b --factory-startup --python tests/test_headless.py`.

### Development install and live reload

Link the add-on folder into Blender's user extensions repository (a directory junction on
Windows) and enable it in Preferences > Add-ons. Blender then reads the code straight from
this repository:

```
%APPDATA%\Blender Foundation\Blender\<version>\extensions\user_default\<addon_folder>
```

PowerShell, from the repository root:

```
New-Item -ItemType Junction -Path "$env:APPDATA\Blender Foundation\Blender\4.5\extensions\user_default\<addon_folder>" -Target "$PWD\<addon_folder>"
```

- After editing, run **Reload Scripts** in Blender (F3, type "Reload Scripts") instead of
  restarting. For this to pick up submodule edits, every add-on's `__init__.py` must start
  with the reload boilerplate used in `ba_exploded_view/__init__.py` (reload each submodule
  when `bpy` is already in the module globals).
- Do not use **Install from Disk** on a development machine: it replaces the junction with a
  copy of the zip, and edits in the repository silently stop reaching Blender. If that
  happens, move the installed folder away and recreate the junction.
- The VS Code extension "Blender Development" (Jacques Lucke) works well on top of this
  setup and can reload on save.
