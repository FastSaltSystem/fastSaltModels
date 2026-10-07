"""Sample PMS SimpView v4 body-reference tracks and bake them in Blender."""

from bisect import bisect_right
import math

import bpy
from mathutils import Quaternion, Vector


class Motion:
    def __init__(self, document, *, choice=None):
        if document.get("format") != "SimpView" or document.get("version") != 4:
            raise ValueError("Expected a PMS SimpView version 4 document")
        if document.get("dimension") != "spatial":
            raise ValueError("Only spatial motion is currently supported")
        choices = document["choices"]
        if choice is None:
            if len(choices) != 1:
                raise ValueError("Select a result choice explicitly when multiple choices exist")
            selected = choices[0]
        else:
            matches = [item for item in choices if item["label"] == choice]
            if len(matches) != 1:
                raise ValueError(f"Expected one result choice named {choice!r}")
            selected = matches[0]
        self.times = [float(t) for t in selected["times"]]
        if (not self.times or any(not math.isfinite(t) for t in self.times)
                or any(b <= a for a, b in zip(self.times, self.times[1:]))):
            raise ValueError("Motion times must be finite and strictly increasing")
        scene = selected["scene"]
        tracks = {track["id"]: track for track in scene["tracks"]}
        self.tracks = {}
        for target in scene["follow_targets"]:
            name, identifier = target["name"], target["track"]
            if identifier != f"body_frame:{name}":
                raise ValueError(f"{name}: expected an actual body-reference track")
            if name in self.tracks:
                raise ValueError(f"Duplicate body track {name}")
            track = tracks[identifier]
            for field, width in [("position", 3), ("quaternion", 4), ("scale", 3)]:
                rows = track[field]
                if len(rows) not in (1, len(self.times)):
                    raise ValueError(f"{name}.{field}: sample count differs from time vector")
                for row in rows:
                    if len(row) != width or not all(math.isfinite(x) for x in row):
                        raise ValueError(f"{name}.{field}: invalid sample")
            if any(abs(c - 1) > 1e-6 for row in track["scale"] for c in row):
                raise ValueError(f"{name}: body-reference tracks must have unit scale")
            if any(sum(c*c for c in row) < 1e-12 for row in track["quaternion"]):
                raise ValueError(f"{name}: zero quaternion")
            self.tracks[name] = track

    @staticmethod
    def _row(rows, index):
        return rows[0 if len(rows) == 1 else index]

    def pose(self, name, time):
        if not math.isfinite(time) or time < self.times[0] - 1e-9 or time > self.times[-1] + 1e-9:
            raise ValueError("Requested time is outside the saved result")
        time = min(max(time, self.times[0]), self.times[-1])
        first = max(0, min(bisect_right(self.times, time) - 1, len(self.times) - 1))
        second = min(first + 1, len(self.times) - 1)
        fraction = 0 if first == second else (time - self.times[first]) / (self.times[second] - self.times[first])
        track = self.tracks[name]
        positions = [Vector(self._row(track["position"], i)) for i in (first, second)]
        rotations = []
        for index in (first, second):
            x, y, z, w = self._row(track["quaternion"], index)
            rotations.append(Quaternion((w, x, y, z)).normalized())
        if rotations[0].dot(rotations[1]) < 0:
            rotations[1].negate()
        return positions[0].lerp(positions[1], fraction), rotations[0].slerp(rotations[1], fraction)


def bake_motion(imported, motion, *, fps=30):
    """Animate body frames; markers and any attached meshes inherit their motion.

    Bake every output movie frame. Between them Blender uses linear component
    curves; use the sampler again for a different output frame rate. Ground is
    unchanged. A parent may supply a presentation-only panel transform.
    """
    if not isinstance(fps, int) or fps <= 0:
        raise ValueError("fps must be a positive integer")
    bodies = {name for name, obj in imported.frames.items() if obj.get("pms_type") == "rigid_body"}
    if bodies != set(motion.tracks):
        raise ValueError(f"Body names do not match motion: {bodies.symmetric_difference(motion.tracks)}")
    duration_frames = (motion.times[-1] - motion.times[0]) * fps
    if abs(duration_frames - round(duration_frames)) > 1e-6:
        raise ValueError("Saved duration must cover an integer number of output frames")
    count = round(duration_frames) + 1
    for name in bodies:
        obj = imported.frames[name]
        if obj.animation_data:
            raise ValueError(f"{name}: refusing to overwrite existing animation")
        obj.rotation_mode = "QUATERNION"
        previous = None
        for frame in range(1, count + 1):
            location, rotation = motion.pose(name, motion.times[0] + (frame - 1) / fps)
            if previous is not None and rotation.dot(previous) < 0:
                rotation.negate()
            previous = rotation.copy()
            obj.location, obj.rotation_quaternion = location, rotation
            obj.keyframe_insert(data_path="location", frame=frame, group="PMS reference motion")
            obj.keyframe_insert(data_path="rotation_quaternion", frame=frame, group="PMS reference motion")
        action = obj.animation_data.action
        # Blender 4.4+ layered actions.
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        for key in curve.keyframe_points:
                            key.interpolation = "LINEAR"
    scene = bpy.context.scene
    scene.render.fps = fps
    scene.render.fps_base = 1
    scene.frame_start = 1
    scene.frame_end = count
    scene.frame_set(1)
    return count
