# BlenderAddons

**BA Toolbox**: one Blender 4.2+ extension that bundles several small production tools.
Install once, enable once, and every tool shows up as a panel in the **Toolbox** sidebar tab
of the 3D Viewport. Individual tools can be switched off in the add-on preferences.

| Tool | Folder | Description |
|---|---|---|
| Exploded View | [`ba_toolbox/tools/exploded_view/`](ba_toolbox/tools/exploded_view/) | Houdini-style exploded view for selected or all objects, animated, with reset |
| Material Assign | [`ba_toolbox/tools/material_assign/`](ba_toolbox/tools/material_assign/) | Replace every material on the selected objects with one chosen material |

Each tool folder has its own README with usage details.

## Install (recommended: online repository with automatic updates)

Every push to `main` publishes a Blender extension repository to GitHub Pages. Add it once
and Blender keeps the toolbox up to date:

1. Blender > Edit > Preferences > Get Extensions > the dropdown at the top right
   (Repositories) > **+** > **Add Remote Repository**.
2. URL:

   ```
   https://iamyzii.github.io/BlenderAddons/index.json
   ```

   Leave "Check for Updates on Startup" on. Confirm.
3. Search for **BA Toolbox** in Get Extensions and click **Install**. It is enabled
   automatically.

When a new version lands on `main`, Get Extensions shows an **Update** button (or updates on
startup if you let it). Its add-on preferences list every tool with an on/off toggle; a tool
that fails to load shows its error there instead of breaking the rest.

### Install from a zip instead

Build the zip from the repository root, then Blender > Preferences > Get Extensions >
Install from Disk:

```
blender --command extension build --source-dir ba_toolbox --output-dir dist
```

### Releasing a new version

1. Bump `version` in `ba_toolbox/blender_manifest.toml` on the tool branch (semantic
   versioning: patch for fixes, minor for new tools or features).
2. Merge into `main` and push. The **Publish extension repository** workflow
   (`.github/workflows/publish.yml`) builds the zip with Blender's own tooling, validates it,
   regenerates `index.json`, and deploys to GitHub Pages.
3. Pull requests and pushes to other branches run the build and validation only, and attach
   the zip as a workflow artifact for inspection.

One-time repository setting for this to work: GitHub > Settings > Pages > Build and
deployment > Source = **GitHub Actions**.

## Repository layout

```
ba_toolbox/                    the extension (one manifest, one version)
  blender_manifest.toml
  __init__.py                  reload support, register/unregister
  registry.py                  loads tools, registers them one by one, isolates failures
  preferences.py               per-tool toggles in the add-on preferences
  tools/
    __init__.py                TOOLS list: the tools to load, in order
    exploded_view/             one folder per tool: __init__, core, properties, operators, ui, README
    material_assign/
tests/                         one headless test per tool + test_toolbox.py for the bundle
```

## Repository conventions

### Branching

- `main` holds only tested, working tools. Nothing is developed directly on `main`.
- Every tool has its own active branch, named after the tool, for example `exploded-view` or
  `material-assign`. All work on that tool happens on its branch and touches only its folder
  under `ba_toolbox/tools/` plus its test.
- Merge a tool branch into `main` only when the tool is tested and working. Use a merge commit
  (`git merge --no-ff <branch>`) so the branch history stays visible. Bump `version` in
  `ba_toolbox/blender_manifest.toml` as part of the merge; that is what makes an update visible
  to installed copies.
- After merging, keep the tool branch alive and continue development there.

### Tool layout

- A tool is a package under `ba_toolbox/tools/<tool_name>/` with its own `README.md` that
  documents that tool only: what it does and how to use it.
- The tool's `__init__.py` defines `label`, `description`, `register()` and `unregister()`,
  and starts with the reload boilerplate (reload each submodule when `bpy` is already in the
  module globals). Add the folder name to `TOOLS` in `ba_toolbox/tools/__init__.py`.
- Every tool puts its 3D Viewport sidebar panel in the shared **Toolbox** tab
  (`bl_category = "Toolbox"`), with the tool name as the panel label.
- Prefix identifiers to avoid clashes between tools: scene property `ba_<tool>`, operators
  `object.ba_<abbr>_<action>`, classes `BA<ABBR>_OT_...` / `BA<ABBR>_PT_...`.
- Each tool has a headless test in `tests/test_<tool_name>.py`. Run all tests from the
  repository root:

```
blender -b --factory-startup --python tests/test_exploded_view.py
```
```
blender -b --factory-startup --python tests/test_material_assign.py
```
```
blender -b --factory-startup --python tests/test_toolbox.py
```

### Development install and live reload

Link `ba_toolbox` into Blender's user extensions repository (a directory junction on Windows)
and enable it in Preferences > Add-ons. Blender then reads the code straight from this
repository. PowerShell, from the repository root:

```
New-Item -ItemType Junction -Path "$env:APPDATA\Blender Foundation\Blender\5.2\extensions\user_default\ba_toolbox" -Target "$PWD\ba_toolbox"
```

- After editing, run **Reload Scripts** in Blender (F3, type "Reload Scripts") instead of
  restarting. The toolbox reloads its own modules and every loaded tool package.
- Do not use **Install from Disk** on a development machine: it replaces the junction with a
  copy of the zip, and edits in the repository silently stop reaching Blender. If that
  happens, move the installed folder away and recreate the junction.
- The VS Code extension "Blender Development" (Jacques Lucke) works well on top of this
  setup and can reload on save.
