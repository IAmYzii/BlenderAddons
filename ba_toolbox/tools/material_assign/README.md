# BA Material Assign

Tool of the **BA Toolbox** Blender extension: pick one material from the current file and, with one click, make it
the only material on every selected object.

## Usage

Sidebar (`N`) in the 3D Viewport, tab **Toolbox**, panel **Material Assign**.

1. Choose a material in the picker. It lists every material in the file. The eyedropper button
   next to it takes the active object's active material instead.
2. Select the objects to change.
3. Check the preview list under the button: every selected object with its material slots.
   A green check marks a slot that already holds the chosen material and stays, a red X marks
   a material that will be removed. Objects without materials show the material that will be
   added. The header totals how many slots are kept and removed.
4. Click **Assign to Selected**. The button shows how many selected objects will be affected.

What happens on each selected object:

- Every material slot is removed and a single slot with the chosen material is added.
- All faces (or curve splines) are pointed at that slot, so the whole object uses it.
- Object-level slot links are reset to data links, so the material sits on the mesh data.

Notes:

- Works on meshes, curves, surfaces, text and metaballs. Lights, cameras, empties and other
  types in the selection are skipped. Linked library objects are skipped because their data
  is read-only.
- Objects sharing one mesh data block are all affected, since the slots live on the data.
- The replaced materials are not deleted from the file. Blender drops materials with zero
  users when the file is saved and reopened, or use File > Clean Up > Purge Unused Data.
- Object mode only. Undo restores the previous materials.

## Install

This tool ships as part of **BA Toolbox**; see the repository README for installation and
the development setup. It can be switched on or off in the toolbox's add-on preferences.

## Test

```
blender -b --factory-startup --python tests/test_material_assign.py   # run from the repository root
```
