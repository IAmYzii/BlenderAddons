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
- Tests for an add-on go in `tests/` and run headless, for example
  `blender -b --factory-startup --python tests/test_headless.py`.

### Development install

Link the add-on folder into Blender's user extensions repository and enable it in
Preferences > Add-ons:

```
%APPDATA%\Blender Foundation\Blender\<version>\extensions\user_default\<addon_folder>
```
