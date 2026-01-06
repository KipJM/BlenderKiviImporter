import dataclasses

import openvr
import re
import math
from mathutils import Matrix, Euler, Vector

loc_offset: Vector = Vector((0, 0, 0.147))
rot_offset: Vector = Vector((-90, 0, 180))
scale: Vector = Vector((1, 1, 1))

streaming = False


@dataclasses.dataclass
class Tracker:
    friendly_name: str
    name: str
    type: str
    index: int
    connected: bool
    is_target_tracker: bool


trackers: dict[str, Tracker] = {}


def handle_tracking(poses, tracker):
    if not tracker.is_target_tracker:
        return

    # target = bpy.data.objects[tracker.target]

    mat = poses[tracker.index].mDeviceToAbsoluteTracking
    # TODO: EXPORT

    # mat = Matrix([list(mat[0]), list(mat[1]), list(mat[2]), [0, 0, 0, 1]])

    # matrix
    m_location_offset = Matrix.Translation(loc_offset)
    m_rotation_offset = Euler((math.radians(rot_offset[0]), math.radians(rot_offset[1]),
                               math.radians(rot_offset[2]))).to_matrix().to_4x4()
    m_scale_offset = (Matrix.Scale(
        scale[0], 4, (1, 0, 0))
                      @ Matrix.Scale(scale[1], 4, (0, 1, 0))
                      @ Matrix.Scale(scale[2], 4, (0, 0, 1))
                      )

    print(mat)

    # mat_world = bpy_extras.io_uti ls.axis_conversion('Z', 'Y', 'Y', 'Z').to_4x4() @ mat @ m_location_offset @ m_rotation_offset @ m_scale_offset
    # old_rot = target.rotation_quaternion.copy() if target.rotation_mode == 'QUATERNION' else target.rotation_euler.copy()

    # mat_rot = mat_world
    # matrix_world = mat_world
    #
    # if target.rotation_mode == 'QUATERNION':
    #     rot = mat_rot.to_quaternion()
    #     rot.make_compatible(old_rot)
    #     target.rotation_quaternion = rot
    # else:
    #     rot = mat_rot.to_euler(target.rotation_euler.order, old_rot)
    #     target.rotation_euler = rot

    # if bpy.context.scene.tool_settings.use_keyframe_insert_auto:
    #     target.keyframe_insert('location')
    #     if target.rotation_mode == 'QUATERNION':
    #         target.keyframe_insert('rotation_quaternion')
    #     else:
    #         target.keyframe_insert('rotation_euler')
    #     target.keyframe_insert('scale')


# handle controller inputs for a given tracker (assumes its a valid controller)
# def handle_controller(tracker):
#     def set_property(property, val, range_old, range_new):
#         try:
#             # item = prop = bpy.data.objects[target]
#             item = prop = bpy.context.scene
#         except:
#             return
#         # prop_path = property.split('.')
#         prop_path = re.split('\.(?![^\[]*\])', property)
#         for p in prop_path:
#             parent_item = item
#             item = prop
#             p_split = re.split('\[|\]', p)
#             prop = getattr(item, p_split[0], None)
#             if prop == None: return
#
#             if len(p_split) > 1:  # there's an index on the property to handle
#                 if re.findall('\'|\"', p_split[1]):  # case its a named index
#                     prop = prop[re.sub('\'|\"', '', p_split[1])]
#
#                 elif p_split[1].isnumeric:  # case its a integer index
#                     prop = prop[int(p_split[1])]
#
#                 else:  # otherwise treat as invalid
#                     return
#
#         # abandon when target property is not a float
#         if type(prop) is not float: return
#
#         remap = (((val - range_old[0]) * (range_new[1] - range_new[0])) / (range_old[1] - range_old[0])) + range_new[0]
#         setattr(item, prop_path[-1], remap)
#
#         if bpy.context.scene.tool_settings.use_keyframe_insert_auto:
#             if type(item) is Vector:
#                 parent_item.keyframe_insert(prop_path[-2])
#             else:
#                 item.keyframe_insert(prop_path[-1])
#
#     # get controller state
#     result, p_controller_state = openvr.VRSystem().getControllerState(tracker.index)
#     # handle trigger
#     set_property(tracker.trigger_property, p_controller_state.rAxis[1].x, [0, 1],
#                  [tracker.trigger_min, tracker.trigger_max])
#     # handle trackpad
#     set_property(tracker.trackpad_x_property, p_controller_state.rAxis[0].x, [-1, 1],
#                  [tracker.trackpad_x_min, tracker.trackpad_x_max])
#     set_property(tracker.trackpad_y_property, p_controller_state.rAxis[0].y, [-1, 1],
#                  [tracker.trackpad_y_min, tracker.trackpad_y_max])
#     # handle grip
#     set_property(tracker.grip_property, p_controller_state.ulButtonPressed >> 2 & 1, [0, 1],
#                  [tracker.grip_min, tracker.grip_max])
#     # handle menu button
#     set_property(tracker.menu_property, p_controller_state.ulButtonPressed >> 1 & 1, [0, 1],
#                  [tracker.menu_min, tracker.menu_max])


# on frame update, update tracking as well as controller inputs
def puppet():
    # settings = scene.OVRSettings
    if not streaming:
        return

    get_trackers()
    poses = []
    poses, _ = openvr.VRCompositor().waitGetPoses(poses, None)
    global trackers
    for tracker_key in trackers:
        tracker = trackers[tracker_key]

        if not tracker.connected:
            continue
        handle_tracking(poses, tracker)
        # if tracker.type == 'Controller':
            # TODO: Controller inputs
            # handle_controller(tracker)
            # print("Controllers not yet supported")
    return


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
                            connected=bool(vr_sys.isTrackedDeviceConnected(i)), name=name, is_target_tracker=False)
                if name == "Controller_002":
                    t.is_target_tracker = True
                trackers[name] = t
                print(f"added {t}")
            else:
                t = trackers[name]
            t.name = name
            t.type = tracker_type
            t.index = i
            t.connected = bool(vr_sys.isTrackedDeviceConnected(i))


# toggles streaming, by initializing and shutting down openvr session
def toggleStreaming():
    global streaming, trackers
    if streaming:
        openvr.shutdown()
        streaming = False
        trackers.clear()
    else:
        openvr.init(openvr.VRApplication_Scene)
        get_trackers()
        streaming = True
    return {'FINISHED'}


toggleStreaming()
while True:
    puppet()
    # print(trackers)

# user interface panel
# class OVRStreamPanel():
#     def draw(self, context):
#         layout = self.layout
#
#         settings = context.scene.OVRSettings
#
#         label = 'Stop Streaming' if settings.streaming else 'Start Streaming'
#         layout.operator('id.toggle_streaming', text=label)
#
#         if settings.streaming:
#             if not settings.trackers: return
#             layout.template_list("TrackerList", "", settings, "trackers", settings, "active_tracker",
#                                  rows=len(settings.trackers))
#             t = settings.trackers[settings.active_tracker]
#             if not t.connected:
#                 layout.label(text='Not Connected')
#                 return
#             layout.prop_search(t, 'target', context.scene, 'objects')
#             if t.target:
#                 item = bpy.data.objects[t.target]
#                 if item.type == 'ARMATURE':
#                     row = layout.row()
#                     row.prop(t, 'use_subtarget')
#                     if t.use_subtarget:
#                         row.prop_search(t, 'subtarget', item.pose, 'bones', text='')
#                         if not t.subtarget: return
#                         item = item.pose.bones[t.subtarget]
#
#                 layout.label(text='Offset:')
#                 row = layout.row(align=True)
#                 col = row.column(align=True)
#                 col.prop(item.OVRBind, 'location')
#                 col = row.column()
#                 col.prop(item.OVRBind, 'rotation')
#                 col = row.column()
#                 col.prop(item.OVRBind, 'scale')
#             if t.type == 'Controller':
#                 def draw_input(label, prop, min, max):
#                     if label: layout.label(text=label + ' Scene Property:')
#                     layout.prop(t, prop, text='')
#                     row = layout.row(align=True)
#                     row.prop(t, min, text='Min')
#                     row.prop(t, max, text='Max')
#
#                 draw_input('Trigger', 'trigger_property', 'trigger_min', 'trigger_max')
#                 draw_input('Trackpad X', 'trackpad_x_property', 'trackpad_x_min', 'trackpad_x_max')
#                 draw_input('Trackpad Y', 'trackpad_y_property', 'trackpad_y_min', 'trackpad_y_max')
#                 draw_input('Grip Button', 'grip_property', 'grip_min', 'grip_max')
#                 draw_input('Menu Button', 'menu_property', 'menu_min', 'menu_max')


# listview for trackers
#
# class TrackerList():
#     def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
#         trackers = data
#         t = item
#         if self.layout_type in {'DEFAULT', 'COMPACT'}:
#             layout.prop(t, 'friendly_name', text="", emboss=False, icon_value=icon)
#         elif self.layout_type in {'GRID'}:
#             layout.label(text="", translate=False, icon_value=icon)
#
#         # class containing relevant data about a given tracker


# class OVRTrackerItem(bpy.types.PropertyGroup):
#     name: bpy.props.StringProperty(name='Tracker Name')
#     friendly_name: bpy.props.StringProperty(name='Friendly Name')
#     index: bpy.props.IntProperty(name='Index')
#     type: bpy.props.StringProperty(name='Tracker Type')
#     connected: bpy.props.BoolProperty(name='Connected', default=False)
#
#     target: bpy.props.StringProperty(name='Target')
#     use_subtarget: bpy.props.BoolProperty(name="Use Bone", default=True)
#     subtarget: bpy.props.StringProperty(name='Subtarget')
#
#     # trigger_target: bpy.props.StringProperty(name='Trigger Target')
#     trigger_property: bpy.props.StringProperty(name='Trigger Property')
#     trigger_min: bpy.props.FloatProperty(name='Trigger Range Minimum', default=0)
#     trigger_max: bpy.props.FloatProperty(name='Trigger Range Maximum', default=1)
#
#     # trackpad_x_target: bpy.props.StringProperty(name='Target X',default='')
#     trackpad_x_property: bpy.props.StringProperty(default='')
#     trackpad_x_min: bpy.props.FloatProperty(default=-1)
#     trackpad_x_max: bpy.props.FloatProperty(default=1)
#     # trackpad_y_target: bpy.props.StringProperty(name='Target Y',default='')
#     trackpad_y_property: bpy.props.StringProperty(default='')
#     trackpad_y_min: bpy.props.FloatProperty(default=-1)
#     trackpad_y_max: bpy.props.FloatProperty(default=1)
#
#     grip_property: bpy.props.StringProperty(default='')
#     grip_min: bpy.props.FloatProperty(default=0)
#     grip_max: bpy.props.FloatProperty(default=1)
#
#     menu_property: bpy.props.StringProperty(default='')
#     menu_min: bpy.props.FloatProperty(default=0)
#     menu_max: bpy.props.FloatProperty(default=1)
#
#
# # class that serves as container for all of this addon's data
# class OVRSettings(bpy.types.PropertyGroup):
#     streaming: bpy.props.BoolProperty(name='Streaming', default=False)
#     trackers: bpy.props.CollectionProperty(type=OVRTrackerItem)
#     active_tracker: bpy.props.IntProperty(name='Active Tracker')
#
#
# # class that stores the offset data for any object bound to a tracker
# class OVRBind(bpy.types.PropertyGroup):
#     location: bpy.props.FloatVectorProperty(name="Loc")
#     rotation: bpy.props.FloatVectorProperty(name="Rot")
#     scale: bpy.props.FloatVectorProperty(name="Scale", default=(1, 1, 1))

# # bpy.app.handlers.frame_change_post.clear()
# def register():
#     bpy.utils.register_class(OVRTrackerItem)
#     bpy.utils.register_class(OVRSettings)
#     bpy.utils.register_class(OVRBind)
#
#     bpy.types.Scene.OVRSettings = bpy.props.PointerProperty(type=OVRSettings)
#     bpy.types.Object.OVRBind = bpy.props.PointerProperty(type=OVRBind)
#     bpy.types.PoseBone.OVRBind = bpy.props.PointerProperty(type=OVRBind)
#
#     bpy.utils.register_class(TrackerList)
#     bpy.utils.register_class(ToggleStreaming)
#     bpy.utils.register_class(OVRStreamPanel)
#
#     # bpy.app.handlers.frame_change_post.clear()
#     bpy.app.handlers.frame_change_post.append(puppet)
