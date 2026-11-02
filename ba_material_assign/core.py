"""Material replacement logic. No UI here."""
import bpy

# Object types whose data carries material slots we can rewrite.
SUPPORTED_TYPES = {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META'}


def supported_targets(objects):
    """Filter to objects we can rewrite: supported type, with editable (non-library) data."""
    out = []
    for o in objects:
        if o.type not in SUPPORTED_TYPES or o.data is None:
            continue
        if o.library is not None or o.data.library is not None:
            continue  # linked library data is read-only
        if o.override_library is not None:
            continue
        out.append(o)
    return out


def assign_single_material(objects, material):
    """Remove every material slot on each object and leave exactly one slot holding `material`.

    Object-level slot links are reset to data links, and every face is pointed at slot 0.
    Shared data blocks are processed once. Returns the number of objects touched.
    """
    done_data = set()
    count = 0
    for o in objects:
        data = o.data
        if data.name not in done_data:
            data.materials.clear()
            data.materials.append(material)
            if o.type == 'MESH' and len(data.polygons):
                data.polygons.foreach_set("material_index", [0] * len(data.polygons))
                data.update()
            elif o.type in {'CURVE', 'SURFACE', 'FONT'}:
                for spline in data.splines:
                    spline.material_index = 0
            done_data.add(data.name)
        # Slots are per object too (link type and object-level material); force the data link.
        for slot in o.material_slots:
            slot.link = 'DATA'
        count += 1
    return count
