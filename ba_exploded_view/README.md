# BA Exploded View

Blender 4.2+ extension that gives you a Houdini-style exploded view with one click.

## Usage

Sidebar (`N`) in the 3D Viewport, tab **Toolbox**, panel **Exploded View**.

- **Explode**: moves the selected objects away from the center. With nothing selected it
  explodes every visible object (cameras, lights, speakers and light probes are skipped).
- **Reset**: restores the selected exploded objects, or all of them when nothing is selected.
- **Distance**: explosion distance. Updates live while objects are exploded.
- **Mode**: *Distance* moves every object the same length; *Scale* moves objects
  proportionally to how far they are from the center (Houdini's default).
- **Center**: combined bounds of the exploded objects, the active object, or the 3D cursor.
- **Animation**: Explode and Reset ease into place over this many seconds (default 0.3,
  0 = instant). Slider changes apply instantly.

Original positions are stored on each object, so clicking Explode again or changing the
sliders never compounds, and Reset still works after saving and reopening the file.
A child whose parent is also being exploded is left alone so it does not move twice.

## Install

Blender > Edit > Preferences > Get Extensions > Install from Disk, choose a zip of the
`ba_exploded_view` folder. Or build the zip:

```
blender --command extension build --source-dir ba_exploded_view --output-dir dist   # run from the repository root
```

For development, link the folder into Blender's user extensions repo
(`%APPDATA%\Blender Foundation\Blender\4.5\extensions\user_default\ba_exploded_view`)
and enable **BA Exploded View** in Preferences > Add-ons. After editing, use
**Reload Scripts** (F3) in Blender; `__init__.py` reloads its submodules so the change is
live without a restart. See the repository README for details.

## Test

```
blender -b --factory-startup --python tests/test_headless.py   # run from the repository root
```
