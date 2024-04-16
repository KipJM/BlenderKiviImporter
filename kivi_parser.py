# KIVI motion file reqs:
# FIRST LINE: "%KIVI MOTION RECORDING"
FIRST_LINE_REQ = "%KIVI MOTION RECORDING"
# settings starts with '!', in format "!key=value"
INFO_CHAR = '!'
INFO_SEP_CHAR = '='
# current settings include:
# [version(str), script(str), scene(str), shot(int), shotat(datetime[str]), framerate(float)]
VERSION_KEY = "version"
SCRIPT_KEY = "script"
SCENE_KEY = "scene"
SHOT_KEY_INT = "shot"
FRAMERATE_KEY_FLOAT = "framerate"
# "<<<" indicates recording start
START_SYMBOL = "<<<"
# "@X>" where X is the frame number, starts at 0
FRAME_CHAR = '@'
# motion data is as follows:
POSE_CHAR = '>'
# @X>[A, B, C, D];[A, B, C, D];[A, B, C, D];[0, 0, 0, 1]
LIST_SEP_CHAR = ';'
LIST_START_CHAR = '['
LIST_END_CHAR = ']'
LIST_ITEM_SEP_CHAR = ", "
# events such as SYNC flash is indicated by '#'
EVENT_CHAR = '#'

# so an event would look like this:
# @X#FLASH

print("hi")
from mathutils import Matrix, Euler, Vector


class Pose:
    matrix: Matrix

    def __init__(self, raw_contents: str):
        # Parse

        # Separate each matrix item
        items = raw_contents.split(LIST_SEP_CHAR)
        constructed_matrix_list = []
        for item in items:
            # print(f"ITEM {item}")
            # Reconstruct list
            list_raw = item[item.index(LIST_START_CHAR) + 1:item.index(LIST_END_CHAR)]
            list_items = [float(i) for i in list_raw.split(LIST_ITEM_SEP_CHAR)]
            constructed_matrix_list.append(list_items)

        matrix = Matrix(constructed_matrix_list)
        # print(f"LIST {constructed_matrix_list} -> MATRIX {matrix}")
        self.matrix = matrix


class Event:
    event_type: str

    def __init__(self, _event_type):
        self.event_type = _event_type


def check_validity(filename):
    try:
        get_file_info(filename)
        return True
    except Exception as e:
        return False


# Only get the file info
def get_file_info(filename):
    with open(filename) as file:
        # This reads the entire file into memory. This isn't a big issue for smaller recordings,
        # plus it's easy to upgrade in the future
        lines = file.read().splitlines()

        file_checked = False
        content_started = False

        file_info = {}
        file_frames = []

        for line in lines:
            if not file_checked:
                if line == FIRST_LINE_REQ:
                    file_checked = True
                else:
                    raise AssertionError(
                        f"Not a KIVI MOTION RECORDING FILE! {FIRST_LINE_REQ} is expected, but the file starts with {line}")
            else:
                # info parse
                if line[0] == INFO_CHAR:
                    info_key = line[1:line.index(INFO_SEP_CHAR)]
                    info_value = line[line.index(INFO_SEP_CHAR) + 1:]

                    # # SPECIAL KEYS
                    # if info_key == SHOT_KEY_INT:
                    #     info_value = int(info_value)
                    # if info_key == FRAMERATE_KEY_FLOAT:
                    #     info_value = float(info_value)

                    file_info[info_key] = info_value

                elif line == START_SYMBOL:
                    print(file_info)
                    print(">>>")

                    # Return info
                    return file_info[VERSION_KEY], file_info[SCRIPT_KEY], file_info[SCENE_KEY], file_info[SHOT_KEY_INT], \
                    file_info[FRAMERATE_KEY_FLOAT]

                else:
                    raise AssertionError(f"ERROR! UNEXPECTED SYMBOL IN INFO SECTION: {line}")


def parse(filename):
    with open(filename) as file:
        # This reads the entire file into memory. This isn't a big issue for smaller recordings,
        # plus it's easy to upgrade in the future
        lines = file.read().splitlines()

        file_checked = False
        content_started = False

        file_info = {}
        file_frames = []

        for line in lines:
            if not file_checked:
                if line == FIRST_LINE_REQ:
                    file_checked = True
                else:
                    raise AssertionError(
                        f"Not a KIVI MOTION RECORDING FILE! {FIRST_LINE_REQ} is expected, but the file starts with {line}")
            else:
                if not content_started:
                    # info parse
                    if line[0] == INFO_CHAR:
                        info_key = line[1:line.index(INFO_SEP_CHAR)]
                        info_value = line[line.index(INFO_SEP_CHAR) + 1:]

                        # SPECIAL KEYS
                        if info_key == SHOT_KEY_INT:
                            info_value = int(info_value)
                        if info_key == FRAMERATE_KEY_FLOAT:
                            info_value = float(info_value)

                        file_info[info_key] = info_value

                    elif line == START_SYMBOL:
                        print(file_info)
                        print(">>>")
                        content_started = True

                    else:
                        raise AssertionError(f"ERROR! UNEXPECTED SYMBOL IN INFO SECTION: {line}")

                else:
                    if line[0] == FRAME_CHAR:
                        if POSE_CHAR in line:
                            # Pose

                            # Get index
                            frame_index = int(line[1:line.index(POSE_CHAR)])
                            if frame_index != len(file_frames):
                                raise AssertionError(f"ERROR! FRAME DATA NOT CONTINUOUS ON {line}")

                            # Parse content
                            pose = Pose(line[line.index(POSE_CHAR) + 1:])
                            # print(pose)
                            file_frames.append(pose)

                        elif EVENT_CHAR in line:
                            # Event

                            # Get index
                            frame_index = int(line[1:line.index(EVENT_CHAR)])
                            if frame_index != len(file_frames):
                                raise AssertionError(f"ERROR! FRAME DATA NOT CONTINUOUS ON {line}")

                            # Parse event
                            event = Event(line[line.index(EVENT_CHAR) + 1:])
                            # print(event)
                            file_frames.append(event)

                        else:
                            raise AssertionError(f"ERROR! UNEXPECTED CONTENT SYMBOL IN FRAME {line}")
                    else:
                        raise AssertionError(f"ERROR! UNEXPECTED SYMBOL IN CONTENT SECTION {line}")

    return file_info, file_frames
