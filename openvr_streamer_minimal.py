import dataclasses
from typing import Any

import openvr
import re
import math
from mathutils import Matrix, Euler, Vector

# loc_offset: Vector = Vector((0, 0, 0.147))
# rot_offset: Vector = Vector((-90, 0, 180))
# scale: Vector = Vector((1, 1, 1))

streaming = False


@dataclasses.dataclass
class Tracker:
    friendly_name: str
    name: str
    type: str
    index: int
    connected: bool


trackers: dict[str, Tracker] = {}

tracker_target: str = ""


def handle_tracking(poses, tracker) -> list:
    mat = poses[tracker.index].mDeviceToAbsoluteTracking
    return [list(mat[0]), list(mat[1]), list(mat[2]), [0,0,0,1]]


# on frame update, update tracking as well as controller inputs
def puppet() -> list | None:
    # settings = scene.OVRSettings
    if not streaming:
        return

    get_trackers()
    poses = []
    poses, _ = openvr.VRCompositor().waitGetPoses(poses, None)
    global trackers

    if tracker_target in trackers:
        tracker = trackers[tracker_target]
        if tracker.connected:
            return handle_tracking(poses, tracker)
        # TODO: Controller inputs


# updates scene tracker list
def get_trackers():
    global trackers
    # settings = context.scene.OVRSettings
    vr_sys = openvr.VRSystem()
    types = {
        str(openvr.TrackedDeviceClass_HMD): "HMD",
        str(openvr.TrackedDeviceClass_Controller): "Controller",
        str(openvr.TrackedDeviceClass_GenericTracker): "GenericTracker"
    }
    for i in range(openvr.k_unMaxTrackedDeviceCount):
        if str(vr_sys.getTrackedDeviceClass(i)) in types:
            # add any new trackers
            tracker_type = types[str(vr_sys.getTrackedDeviceClass(i))]
            name = tracker_type + '_%03d' % i
            if name not in trackers:
                t = Tracker(friendly_name=name, type=tracker_type, index=i,
                            connected=bool(vr_sys.isTrackedDeviceConnected(i)), name=name)
                trackers[name] = t
                # print(f"added {t}")
            else:
                t = trackers[name]
            t.name = name
            t.type = tracker_type
            t.index = i
            t.connected = bool(vr_sys.isTrackedDeviceConnected(i))


# toggles streaming, by initializing and shutting down openvr session
def disableStreaming():
    global streaming, trackers
    if streaming:
        openvr.shutdown()
        streaming = False
        trackers.clear()


def enableStreaming():
    global streaming, trackers
    if not streaming:
        openvr.init(openvr.VRApplication_Scene)
        get_trackers()
        streaming = True
