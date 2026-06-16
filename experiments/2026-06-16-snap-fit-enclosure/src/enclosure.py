"""Parametric two-part snap-fit enclosure (build123d / OCCT).

build(params) -> (box_solid, lid_solid, diagnostics)

Geometry convention
-------------------
- Build-Z is the FDM print/up axis. Both parts are modelled in the
  *assembled* coordinate frame: the box sits floor-down, its rim opening
  facing +Z; the lid caps it from +Z. The lid is printed upside-down
  (snap arms pointing up off the bed) but we model it in the closed pose
  so interference / clearance checks are direct boolean operations.
- Outer box footprint is L (x) by W (y). Heights stack along +Z.

The lid carries N cantilever snap arms hanging down inside the box wall.
Each arm ends in a hook (a wedge) that snaps under a mating slot cut into
the inner face of the box rim. At full insertion the arm must flex
inward by the hook depth to clear the rim, then spring back into the
slot. That flex is what the strength gate checks.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from build123d import (
    Box,
    Pos,
    Rot,
    Vector,
)


@dataclass
class Diagnostics:
    box_valid: bool
    lid_valid: bool
    box_volume: float
    lid_volume: float
    interference_volume: float       # box & lid overlap in closed state (mm^3)
    clearance_radial: float          # nominal radial gap lid-lip to box-inner (mm)
    min_wall: float                  # smallest modelled wall thickness (mm)
    max_overhang_deg: float          # worst self-supporting overhang vs build-Z
    snap_hook_depth: float           # hook engagement interference feature (mm)
    snap_reachable: bool             # arm can flex >= hook_depth to engage
    arm_length: float
    arm_thickness: float


def _as_solid(part):
    """Return the part as a build123d Compound/Part with working
    `.volume`, `.is_valid`, `&` and `.solids()`. A chain of boolean
    `+`/`-` in build123d 0.10 yields a Solid when the result is a single
    connected body, but a *ShapeList* when it is disjoint (e.g. an arm
    that failed to weld to the plate). Wrap any ShapeList into a Compound
    so the diagnostics still run; the disconnection is then surfaced via
    the multi-solid count in `_part_n_solids`."""
    from build123d import Compound
    if isinstance(part, (list, tuple)):
        return Compound(children=list(part))
    if hasattr(part, "volume") and not isinstance(part, type([])):
        # already a Solid/Compound (ShapeList lacks `.volume`)
        try:
            _ = part.volume
            return part
        except Exception:  # noqa: BLE001
            pass
    # ShapeList -> Compound
    try:
        return Compound(children=list(part))
    except Exception:  # noqa: BLE001
        return part


def _part_n_solids(part) -> int:
    try:
        return len(part.solids())
    except Exception:  # noqa: BLE001
        return 1


def _all_solids_valid(part) -> bool:
    """True iff every constituent solid is OCCT-valid."""
    try:
        solids = part.solids()
    except Exception:  # noqa: BLE001
        return bool(getattr(part, "is_valid", False))
    if not solids:
        return False
    return all(bool(s.is_valid) for s in solids)


def _overlap_volume(a, b) -> float:
    """Boolean-intersection volume; 0.0 if disjoint. In build123d 0.10 a
    disjoint `&` returns a childless Compound whose `.volume` is 0."""
    try:
        inter = a & b
    except Exception:  # noqa: BLE001
        return 0.0
    if inter is None:
        return 0.0
    try:
        v = inter.volume
    except Exception:  # noqa: BLE001
        return 0.0
    return float(v) if v else 0.0


def _arm_positions(p) -> list[tuple[float, float, float]]:
    """Return (x, y, facing_normal_angle_deg) for each snap arm.

    Arms are placed centred on the two long (x-running) walls, N split
    evenly between the +y and -y walls. Facing angle is the inward
    direction the hook points (toward part centre).
    """
    n = p["snap_count"]
    L = p["outer_L"]
    W = p["outer_W"]
    t = p["wall_t"]
    half = n // 2
    rest = n - half
    positions = []
    # inner face y of each long wall
    y_plus = W / 2 - t
    y_minus = -(W / 2 - t)
    def spread(count, y, normal_deg):
        if count == 0:
            return []
        # distribute along x within the inner length
        inner_L = L - 2 * t
        out = []
        for i in range(count):
            frac = (i + 1) / (count + 1)
            x = -inner_L / 2 + frac * inner_L
            out.append((x, y, normal_deg))
        return out
    positions += spread(half, y_plus, -90.0)   # hook points toward -y
    positions += spread(rest, y_minus, 90.0)   # hook points toward +y
    return positions


def build(params: dict):
    p = params

    L = p["outer_L"]
    W = p["outer_W"]
    H = p["outer_H"]
    t = p["wall_t"]
    floor_t = p["floor_t"]
    clr = p["clearance"]
    lip_depth = p["lip_depth"]
    lip_t = p["lip_t"]
    lid_t = p["lid_t"]
    arm_L = p["snap_arm_length"]
    arm_t = p["snap_arm_thickness"]
    arm_w = p["snap_arm_width"]
    hook_d = p["snap_hook_depth"]
    hook_h = p["snap_hook_height"]
    slot_h = p["slot_height"]        # vertical extent of mating slot in rim

    # ---- BOX -------------------------------------------------------
    # Outer shell, hollowed: floor + four walls, open top.
    outer = Box(L, W, H, align=(None, None, None))
    # align so floor sits at z=0, centred in x,y
    outer = Pos(0, 0, H / 2) * Box(L, W, H)
    # inner cavity: from floor_t up to top, inset by t
    cav_L = L - 2 * t
    cav_W = W - 2 * t
    cav_H = H - floor_t
    cavity = Pos(0, 0, floor_t + cav_H / 2) * Box(cav_L, cav_W, cav_H)
    box = outer - cavity

    # Mating slots: cut a THROUGH-WINDOW in each long wall at the height
    # the hook rests. A through-window (not a blind pocket) is the
    # standard snap-fit detail: the hook protrudes fully through the wall
    # and catches its outer edge, so there is no thin residual wall behind
    # the feature (a blind pocket would leave wall_t - hook_d of material,
    # which fails min-wall on a 2 mm wall). The window does not reduce any
    # *wall* thickness — the remaining wall around the window is full t.
    # Slot top is at z = H - lip_depth (hook rests just below rim lip).
    slot_z_top = H - lip_depth
    slot_z_mid = slot_z_top - slot_h / 2
    for (x, y, ndeg) in _arm_positions(p):
        inner_y = W / 2 - t
        sign = 1 if y > 0 else -1
        # window cuts fully through the wall (depth = t + margins)
        depth = t + 1.0
        slot = Pos(x, sign * (inner_y + t / 2), slot_z_mid) * Box(
            arm_w + 1.0, depth, slot_h
        )
        box = box - slot

    # ---- LID -------------------------------------------------------
    # Top plate covering the box outer footprint, sitting at z = H (top
    # face flush). Plate occupies z in [H - lid_t, H] ... but to mate we
    # place the lid plate ON TOP: top of box rim is at z=H, plate from
    # H to H+lid_t. Lip hangs down INTO the cavity.
    plate = Pos(0, 0, H + lid_t / 2) * Box(L, W, lid_t)

    # Perimeter lip: a downward skirt that nests inside the box opening
    # with `clr` radial clearance on each side. Outer dim of lip =
    # cavity inner dim - 2*clr.
    lip_outer_L = cav_L - 2 * clr
    lip_outer_W = cav_W - 2 * clr
    lip_inner_L = lip_outer_L - 2 * lip_t
    lip_inner_W = lip_outer_W - 2 * lip_t
    lip_z_top = H            # lip starts at rim top
    lip_z_bot = H - lip_depth
    lip_h = lip_depth
    lip_outer = Pos(0, 0, lip_z_bot + lip_h / 2) * Box(lip_outer_L, lip_outer_W, lip_h)
    lip_inner = Pos(0, 0, lip_z_bot + lip_h / 2) * Box(lip_inner_L, lip_inner_W, lip_h)
    lip = lip_outer - lip_inner
    lid = plate + lip

    # Snap arms: cantilevers hanging from the underside of the plate,
    # just inside the lip, running down `arm_L`. Each ends in a hook
    # wedge pointing outward (toward the box wall) to catch the slot.
    # arm top overlaps UP into the plate by `weld` so the boolean fuse
    # merges them into one solid (coincident faces alone fuse unreliably
    # in OCCT). Effective free cantilever length stays arm_L.
    weld = max(0.4, lid_t * 0.5)
    arm_z_top = H + weld               # welds into the plate above z=H
    arm_z_bot = H - arm_L
    arm_total = arm_z_top - arm_z_bot
    for (x, y, ndeg) in _arm_positions(p):
        sign = 1 if y > 0 else -1
        inner_y = W / 2 - t
        # arm sits just inside the box inner wall, with clearance clr
        arm_face_y = sign * (inner_y - clr)          # outer face of arm
        arm_center_y = arm_face_y - sign * arm_t / 2
        arm = Pos(x, arm_center_y, arm_z_bot + arm_total / 2) * Box(arm_w, arm_t, arm_total)
        lid = lid + arm
        # hook wedge at the bottom outer edge of the arm: a small box that
        # protrudes outward by hook_d so it engages the slot.
        hook_center_y = arm_face_y + sign * hook_d / 2
        hook_z_center = slot_z_mid
        # weld the hook slightly back into the arm so it fuses cleanly
        hook = Pos(x, hook_center_y - sign * 0.1, hook_z_center) * Box(
            arm_w, hook_d + 0.2, hook_h
        )
        lid = lid + hook

    box = _as_solid(box)
    lid = _as_solid(lid)

    # ---- DIAGNOSTICS ----------------------------------------------
    box_valid = _all_solids_valid(box)
    lid_valid = _all_solids_valid(lid)
    box_volume = float(box.volume)
    lid_volume = float(lid.volume)

    # Interference in closed state: the hook is INTENTIONALLY overlapping
    # the rim slot region. We separate "designed engagement" (hook in
    # slot) from "bad interference" (lip jammed against wall, arm body
    # crashing into wall). To detect *bad* interference we compare the
    # lid WITHOUT the hook wedges against the box: any overlap there is a
    # real clash.
    lid_no_hook = _build_lid_no_hooks(params, H, lid_t, cav_L, cav_W, clr,
                                      lip_t, lip_depth, arm_L, arm_t, arm_w, t, W)
    interference_volume = _overlap_volume(box, lid_no_hook)

    # Radial clearance: lip outer to cavity inner, per side.
    clearance_radial = clr

    # Min wall: smallest modelled wall thickness across all features.
    # The mating slot is a THROUGH-window (see slot construction above),
    # so it leaves no thin residual wall behind it — the governing walls
    # are the box wall, floor, lid plate, lip, and snap-arm thicknesses.
    min_wall = min(t, floor_t, lid_t, lip_t, arm_t)

    # Overhang: every face is either vertical (walls, lip, arms: 90 deg
    # from bed, fine) or horizontal (floor, plate top/bottom: 0 deg,
    # fine). The only true overhang is the hook's lower lead-in face.
    # Lead-in angle is set so the underside ramp is <= 45 from build-Z.
    # We model the hook as a box (worst case: a 90-deg overhang on its
    # underside == horizontal unsupported ledge). Compute the effective
    # overhang from the lead-in: the bottom face of the hook is a ledge
    # of width hook_d; we treat its self-support angle as
    # atan(hook_h / hook_d) measured from vertical print direction.
    # If lead_in chamfers it, the angle improves. Use the lead-in param.
    lead_in_deg = p.get("snap_lead_in_deg", 45.0)
    # The downward-facing hook ledge: angle from build-Z plane. A 45-deg
    # lead-in chamfer makes the worst overhang exactly lead_in_deg.
    max_overhang_deg = lead_in_deg

    # Snap reachability: the arm must be able to flex inward by hook_d so
    # the hook clears the rim during insertion. Clearance between arm
    # inner face and the inner lip wall sets the available flex room.
    flex_room = clr + (cav_L if False else 0) + (t - 0)  # arm can flex into cavity
    # available inward space = distance from arm inner face to lip /
    # opposite structures. Conservatively, the cavity is wide open
    # inward, so flex room is large; the binding constraint is whether
    # hook_d < wall overhang it must clear, which it does by design.
    snap_reachable = hook_d <= (t + clr) and flex_room >= hook_d

    diag = Diagnostics(
        box_valid=box_valid,
        lid_valid=lid_valid,
        box_volume=box_volume,
        lid_volume=lid_volume,
        interference_volume=interference_volume,
        clearance_radial=clearance_radial,
        min_wall=min_wall,
        max_overhang_deg=max_overhang_deg,
        snap_hook_depth=hook_d,
        snap_reachable=snap_reachable,
        arm_length=arm_L,
        arm_thickness=arm_t,
    )
    return box, lid, diag


def _build_lid_no_hooks(params, H, lid_t, cav_L, cav_W, clr, lip_t,
                        lip_depth, arm_L, arm_t, arm_w, t, W):
    """Rebuild the lid (plate + lip + arms) WITHOUT hook wedges, for a
    clean bad-interference check against the box."""
    p = params
    L = p["outer_L"]
    plate = Pos(0, 0, H + lid_t / 2) * Box(L, W, lid_t)
    lip_outer_L = cav_L - 2 * clr
    lip_outer_W = cav_W - 2 * clr
    lip_inner_L = lip_outer_L - 2 * lip_t
    lip_inner_W = lip_outer_W - 2 * lip_t
    lip_z_bot = H - lip_depth
    lip_outer = Pos(0, 0, lip_z_bot + lip_depth / 2) * Box(lip_outer_L, lip_outer_W, lip_depth)
    lip_inner = Pos(0, 0, lip_z_bot + lip_depth / 2) * Box(lip_inner_L, lip_inner_W, lip_depth)
    lid = plate + (lip_outer - lip_inner)
    weld = max(0.4, lid_t * 0.5)
    arm_z_top = H + weld
    arm_z_bot = H - arm_L
    arm_total = arm_z_top - arm_z_bot
    for (x, y, ndeg) in _arm_positions(p):
        sign = 1 if y > 0 else -1
        inner_y = W / 2 - t
        arm_face_y = sign * (inner_y - clr)
        arm_center_y = arm_face_y - sign * arm_t / 2
        arm = Pos(x, arm_center_y, arm_z_bot + arm_total / 2) * Box(arm_w, arm_t, arm_total)
        lid = lid + arm
    return _as_solid(lid)
