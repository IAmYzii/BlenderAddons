"""Explosion math and per-object state. No UI here."""
import bpy
from mathutils import Vector, Matrix

PROP_ORIG_LOC = "ba_exv_orig_location"      # original obj.location (parent space)
PROP_ORIG_CENTER = "ba_exv_orig_center"     # original world-space bbox center

SKIP_TYPES = {'CAMERA', 'LIGHT', 'SPEAKER', 'LIGHT_PROBE'}


def is_exploded(obj):
    return PROP_ORIG_LOC in obj


def world_bbox_center(obj):
    mw = obj.matrix_world
    corners = [mw @ Vector(c) for c in obj.bound_box]
    return sum(corners, Vector()) / 8.0


def _parent_space_matrix(obj):
    """Matrix mapping obj.location (parent space) to world space."""
    if obj.parent:
        return obj.parent.matrix_world @ obj.matrix_parent_inverse
    return Matrix.Identity(4)


def collect_targets(context):
    """Selected objects, or all visible geometry objects if nothing is selected."""
    sel = [o for o in context.selected_objects if o.type not in SKIP_TYPES]
    if sel:
        objs = sel
    else:
        objs = [o for o in context.visible_objects if o.type not in SKIP_TYPES]
    return _drop_nested(objs)


def exploded_objects(context):
    return _drop_nested([o for o in context.scene.objects if is_exploded(o)])


def _drop_nested(objs):
    """Skip objects whose ancestor is also in the set, so children do not move twice."""
    objset = set(objs)
    out = []
    for o in objs:
        p = o.parent
        nested = False
        while p:
            if p in objset:
                nested = True
                break
            p = p.parent
        if not nested:
            out.append(o)
    return out


def store_original(obj):
    if not is_exploded(obj):
        obj[PROP_ORIG_LOC] = tuple(obj.location)
        obj[PROP_ORIG_CENTER] = tuple(world_bbox_center(obj))


def original_center(obj):
    if is_exploded(obj):
        return Vector(obj[PROP_ORIG_CENTER])
    return world_bbox_center(obj)


def compute_center(context, objs, settings):
    if settings.center == 'CURSOR':
        return context.scene.cursor.location.copy()
    if settings.center == 'ACTIVE' and context.view_layer.objects.active:
        return original_center(context.view_layer.objects.active)
    if not objs:
        return Vector()
    # Bounding box of the original bbox centers.
    pts = [original_center(o) for o in objs]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return (lo + hi) * 0.5


def apply_explosion(context, objs, settings):
    """Explode objs (storing originals first). Offsets are always computed from the originals."""
    for o in objs:
        store_original(o)
    center = compute_center(context, objs, settings)
    amount = settings.distance + settings.extra
    for o in objs:
        direction = original_center(o) - center
        if settings.mode == 'DISTANCE':
            if direction.length_squared < 1e-12:
                offset = Vector()
            else:
                offset = direction.normalized() * amount
        else:
            offset = direction * amount
        # Convert world-space offset into the object's parent space.
        to_world = _parent_space_matrix(o).to_3x3()
        local_offset = to_world.inverted_safe() @ offset
        o.location = Vector(o[PROP_ORIG_LOC]) + local_offset
    return len(objs)


def reset_objects(objs):
    n = 0
    for o in objs:
        if is_exploded(o):
            o.location = Vector(o[PROP_ORIG_LOC])
            del o[PROP_ORIG_LOC]
            if PROP_ORIG_CENTER in o:
                del o[PROP_ORIG_CENTER]
            n += 1
    return n


def reapply_all(context):
    objs = exploded_objects(context)
    if objs:
        apply_explosion(context, objs, context.scene.ba_exploded_view)
