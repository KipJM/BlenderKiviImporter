# KIVI motion file reqs:
# FIRST LINE: "%KIVI MOTION RECORDING"
FIRST_LINE_REQ = "%KIVI MOTION RECORDING"
# settings starts with '!', in format "!key=value"
INFO_CHAR = '!'
INFO_SEP_CHAR = '='
# current settings include:
# [version(str), script(str), scene(str), shot(int), shotat(datetime[str]), framerate(float)]
SHOT_KEY_INT = "shot"
FRAMERATE_KEY_FLOAT = "framerate"
# "<<<" indicates recording start
START_SYMBOL = "<<<"
# "@X>" where X is the frame number, starts at 0
FRAME_CHAR = '@'
# motion data is as follows:
POSE_CHAR = '>'
# @X>[A, B, C, D];[A, B, C, D];[A, B, C, D];[0, 0, 0, 1]
# events such as SYNC flash is indicated by '#'
EVENT_CHAR = '#'
# so an event would look like this:
# @X#FLASH


class Pose:
    content: str

    def __init__(self, _content):
        self.content = _content


class Event:
    event_type: str

    def __init__(self, _event_type):
        self.event_type = _event_type


# This is a demo parser for a KIVI .mrec motion recording file
filename = "script1_scene3-exit_shot5.mrec"

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
                print(
                    f"Not a KIVI MOTION RECORDING FILE! {FIRST_LINE_REQ} is expected, but the file starts with {line}")
                exit()
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
                    print(f"ERROR! UNEXPECTED SYMBOL IN INFO SECTION: {line}")
                    exit()

            else:
                if line[0] == FRAME_CHAR:
                    if POSE_CHAR in line:
                        # Pose

                        # Get index
                        frame_index = int(line[1:line.index(POSE_CHAR)])
                        if frame_index != len(file_frames):
                            print(f"ERROR! FRAME DATA NOT CONTINUOUS ON {line}")
                            exit()

                        # Parse content
                        pose = Pose(line[line.index(POSE_CHAR) + 1:])
                        print(pose)
                        file_frames.append(pose)

                    elif EVENT_CHAR in line:
                        # Event

                        # Get index
                        frame_index = int(line[1:line.index(EVENT_CHAR)])
                        if frame_index != len(file_frames):
                            print(f"ERROR! FRAME DATA NOT CONTINUOUS ON {line}")
                            exit()

                        # Parse event
                        event = Event(line[line.index(EVENT_CHAR) + 1:])
                        print(event)
                        file_frames.append(event)

                    else:
                        print(f"ERROR! UNEXPECTED CONTENT SYMBOL IN FRAME {line}")
                else:
                    print(f"ERROR! UNEXPECTED SYMBOL IN CONTENT SECTION {line}")

file_frames