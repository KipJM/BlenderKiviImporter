# KIVI motion file reqs:
# FIRST LINE: "%KIVI MOTION RECORDING"
# settings starts with '!', in format "!key=value"
# current settings include:
# [version(str), script(str), scene(str), shot(int), shotat(datetime[str]), framerate(float)]
# "<<<" indicates recording start
# "@X>" where X is the frame number, starts at 0
# motion data is as follows:
# @X>[A, B, C, D];[A, B, C, D];[A, B, C, D];[0, 0, 0, 1]
# events such as SYNC flash is indicated by '#'
# so an event would look like this:
# @X#FLASH

# This is a demo parser for a KIVI .mrec motion recording file
filename = "script1_scene3-exit_shot5.mrec"

with open(filename) as file:
    # This reads the entire file into memory. This isn't a big issue for smaller recordings,
    # plus it's easy to upgrade in the future
    lines = file.read().splitlines()