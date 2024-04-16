import math

import bpy
import bpy_extras
import kivi_parser
from mathutils import Matrix, Euler, Vector

# CHANGE THIS TO YOUR CAMERA OFFSET. FOR SOME REASON I DIDN'T INCLUDE THIS IN THE KIVI RECORDING FILES
# USUALLY GUESSING A ROUGH VALUE WORKS WELL ENOUGH (I THINK)
loc_offset: Vector = Vector((0, 0, 0.147))
rot_offset: Vector = Vector((-90, 0, 180))
scale: Vector = Vector((1, 1, 1))


def set_scene_settings(file_info):
    target_framerate = file_info[kivi_parser.FRAMERATE_KEY_FLOAT]
    blender_fps = math.ceil(target_framerate)
    blender_base = blender_fps / target_framerate

    # apply framerate settings
    bpy.context.scene.render.fps = blender_fps
    bpy.context.scene.render.fps_base = blender_base


def add_pose(target, mat):
    # matrix
    m_location_offset = Matrix.Translation(loc_offset)
    m_rotation_offset = Euler((math.radians(rot_offset[0]), math.radians(rot_offset[1]),
                               math.radians(rot_offset[2]))).to_matrix().to_4x4()
    m_scale_offset = (Matrix.Scale(
        scale[0], 4, (1, 0, 0))
                      @ Matrix.Scale(scale[1], 4, (0, 1, 0))
                      @ Matrix.Scale(scale[2], 4, (0, 0, 1))
                      )

    mat_world = (bpy_extras.io_utils.axis_conversion('Z', 'Y', 'Y', 'Z').to_4x4()
                 @ mat @ m_location_offset @ m_rotation_offset @ m_scale_offset)

    old_rot = target.rotation_quaternion.copy() if target.rotation_mode == 'QUATERNION' \
        else target.rotation_euler.copy()

    mat_rot = mat_world
    matrix_world = mat_world

    if target.bl_rna.name == 'Pose Bone':
        mat_rot = target.id_data.convert_space(pose_bone=target, matrix=mat_world, from_space='WORLD', to_space='LOCAL')
        target.matrix = mat_world
    else:
        mat_rot = mat_world
        target.matrix_world = mat_world

    if target.rotation_mode == 'QUATERNION':
        rot = mat_rot.to_quaternion()
        rot.make_compatible(old_rot)
        target.rotation_quaternion = rot
    else:
        rot = mat_rot.to_euler(target.rotation_euler.order, old_rot)
        target.rotation_euler = rot

    target.keyframe_insert('location')
    if target.rotation_mode == 'QUATERNION':
        target.keyframe_insert('rotation_quaternion')
    else:
        target.keyframe_insert('rotation_euler')
    target.keyframe_insert('scale')


def import_file(filename, target):
    file_info, file_content = kivi_parser.parse(filename)
    print(file_info)
    set_scene_settings(file_info)
    target.animation_data_clear()

    for frame_index, content in enumerate(file_content):
        # In Blender, anim start at 1
        bpy.context.scene.frame_set(frame_index + 1)
        if isinstance(content, kivi_parser.Pose):
            # Pose
            add_pose(target, content.matrix)
        elif isinstance(content, kivi_parser.Event):
            # Event
            bpy.context.scene.timeline_markers.new(content.event_type, frame=frame_index + 1)