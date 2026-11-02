"""Explosion math and per-object state. No UI here."""
import time

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


def exploded_locations(context, objs, settings):
    """Store originals, then return {obj: exploded location} without moving anything."""
    for o in objs:
        store_original(o)
    center = compute_center(context, objs, settings)
    amount = settings.distance
    result = {}
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
        result[o] = Vector(o[PROP_ORIG_LOC]) + local_offset
    return result


def apply_explosion(context, objs, settings, animate=False):
    """Explode objs. Offsets are always computed from the originals, so it never compounds."""
    targets = exploded_locations(context, objs, settings)
    _move(targets, settings.duration if animate else 0.0)
    return len(targets)


def reset_objects(objs, duration=0.0):
    targets = {}
    for o in objs:
        if is_exploded(o):
            targets[o] = Vector(o[PROP_ORIG_LOC])
            del o[PROP_ORIG_LOC]
            if PROP_ORIG_CENTER in o:
                del o[PROP_ORIG_CENTER]
    _move(targets, duration)
    return len(targets)


def reapply_all(context):
    objs = exploded_objects(context)
    if objs:
        apply_explosion(context, objs, context.scene.ba_exploded_view)


# --- animation -------------------------------------------------------------
# The final location is written immediately (so undo captures the real end
# state); the tween is purely visual and runs on an app timer.

_anim = {"segments": [], "start": 0.0, "duration": 0.0}
_FPS_INTERVAL = 1.0 / 60.0


def _move(targets, duration):
    if duration <= 0.0 or not targets:
        for o, loc in targets.items():
            o.location = loc
        _anim["segments"] = []
        return
    segments = []
    for o, end in targets.items():
        start = o.location.copy()
        o.location = end  # final state now, so the operator's undo step is correct
        if (end - start).length_squared > 1e-12:
            segments.append((o, start, end))
    _anim["segments"] = segments
    _anim["start"] = time.perf_counter()
    _anim["duration"] = duration
    if segments and not bpy.app.timers.is_registered(_tick):
        bpy.app.timers.register(_tick, first_interval=0.0)


def _tick():
    segs = _anim["segments"]
    if not segs:
        return None
    t = (time.perf_counter() - _anim["start"]) / _anim["duration"]
    done = t >= 1.0
    t = 1.0 if done else t
    f = t * t * (3.0 - 2.0 * t)  # smoothstep ease in/out
    alive = []
    for o, start, end in segs:
        try:
            o.location = start.lerp(end, f)
            alive.append((o, start, end))
        except ReferenceError:
            pass  # object was deleted / undone mid-animation
    if done or not alive:
        _anim["segments"] = []
        return None
    _anim["segments"] = alive
    return _FPS_INTERVAL


def is_animating():
    return bool(_anim["segments"])
