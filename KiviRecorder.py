import atexit
import datetime
import queue
import threading
import time

import pygame
import pygame_gui
import winsound
from pygame_gui.core.utility import create_resource_path
from pygame_gui.windows import UIFileDialog

import openvr_streamer_minimal

framerate = 29.97


# saving thread
def fileWriteThread():
    with open(save_directory + f"\\script{script}_scene{scene}_shot{shot}.mrec", "w") as rec_file:
        def writeNl(content):
            rec_file.write(content + "\n")

        # Init
        print("Starting file writing")
        print(f"Writing to file at {save_directory}" + f"\\script{script}_scene{scene}_shot{shot}.mrec")

        # Add init metadata
        writeNl("%KIVI MOTION RECORDING")
        writeNl(f"!version={'KiviRecorder 1.0 internal'}")
        writeNl(f"!script={script}")
        writeNl(f"!scene={scene}")
        writeNl(f"!shot={shot}")
        writeNl(f"!shotat={datetime.datetime.now().strftime('%m/%d  %H:%M:%S.%f')[:-5]}")
        writeNl(f"!framerate={framerate}")
        writeNl(f"<<<")

        while recording:
            # print("HI")
            # print(f"wq left: {write_queue.qsize()}")
            if not write_queue.empty():
                # print(f"WQ LEFT: {write_queue.qsize()}")
                data = write_queue.get()

                if data[1] is True:
                    # Flash write
                    writeNl(f"@{data[0]}#FLASH")
                else:
                    mat = data[1]

                    writeNl(f"@{data[0]}>{mat[0]};{mat[1]};{mat[2]};{mat[3]}")

        if not recording:
            print("Stopping write!")
            # for i in range(5):
            #     print("useless wait")
            #     time.sleep(0.5)
            # stopping
            # write everything to file before shutting down
            while write_queue.qsize() != 0:
                print(f"Stopping write. Writing everything to disk... WQ left: {write_queue.qsize()}")
                data = write_queue.get()

                if data[1] is True:
                    # Flash write
                    writeNl(f"@{data[0]}#FLASH")
                else:
                    mat = data[1]

                    writeNl(f"@{data[0]}>{mat[0]};{mat[1]};{mat[2]};{mat[3]}")

def bgScreen(bg, text_color):
    screen.fill(bg)
    text_surface = font.render(info_text, True, text_color)
    screen.blit(text_surface, (10, 10))


dot = 0


def clapperTime():
    global dot
    match dot:
        case 0:
            add = "◓"
            dot += 1
        case 1:
            add = "◑"
            dot += 1
        case 2:
            add = "◒"
            dot += 1
        case 3:
            add = "◐"
            dot = 0

    text_surface = font_clock.render(str(datetime.datetime.now().strftime("%m/%d  %H:%M:%S.%f")[:-5]), True,
                                     (255, 255, 255), (0, 0, 0))
    w, h = pygame.display.get_surface().get_size()
    text_rect = text_surface.get_rect(center=(w / 2, h / 2 - 20))
    screen.blit(text_surface, text_rect)

    blip_text = blip_font.render(add, True, (255, 255, 255), (0, 0, 0))
    screen.blit(blip_text, text_surface.get_rect(center=(w / 2 + 480, h / 2 - 20)))


def recText():
    text_surface = font.render("PRESS Q TO STOP RECORDING", True, (255, 255, 255), (0, 0, 0))
    w, h = pygame.display.get_surface().get_size()
    text_rect = text_surface.get_rect(center=(w / 2, h))
    screen.blit(text_surface, text_rect)


def stoppedText():
    text_surface = font.render("PRESS P TO START RECORDING", True, (255, 255, 255), (0, 0, 0))
    w, h = pygame.display.get_surface().get_size()
    text_rect = text_surface.get_rect(center=(w / 2, h - 25))
    screen.blit(text_surface, text_rect)

    text_surface = font.render("N: CHANGE SCENE | F: SAVE LOCATION | V: TRACKER SELECT", True, (255, 255, 255),
                               (0, 0, 0))
    w, h = pygame.display.get_surface().get_size()
    text_rect = text_surface.get_rect(center=(w / 2, h - 5))
    screen.blit(text_surface, text_rect)

    text_surface = font_big.render("RECORDING STOPPED", True, (255, 255, 255))
    w, h = pygame.display.get_surface().get_size()
    text_rect = text_surface.get_rect(center=(w / 2, h / 2 - 30))
    screen.blit(text_surface, text_rect)


def scene_data(flashing=False):
    color = (187, 255, 0) if not flashing else (0, 0, 0)
    # scene data
    text_surface = font_big.render(f"SCRIPT {script}", True, color)
    w, h = pygame.display.get_surface().get_size()
    text_rect = text_surface.get_rect(center=(w / 2, h / 2 + 70))
    screen.blit(text_surface, text_rect)

    text_surface = font_big.render(f"SCENE {scene}", True, color)
    w, h = pygame.display.get_surface().get_size()
    text_rect = text_surface.get_rect(center=(w / 2, h / 2 + 120))
    screen.blit(text_surface, text_rect)

    text_surface = font_big.render(f"SHOT {shot}", True, color)
    w, h = pygame.display.get_surface().get_size()
    text_rect = text_surface.get_rect(center=(w / 2, h / 2 + 170))
    screen.blit(text_surface, text_rect)


def flash():
    # write
    global write_queue, frame
    write_queue.put_nowait([frame, True])

    bgScreen((255, 255, 255), (0, 0, 0))
    clapperTime()
    scene_data(True)
    pygame.display.flip()
    # Clap
    winsound.Beep(1000, int(1000 / framerate))
    frame += 1  # Account for misalignment because of flash blocking thread
    # time.sleep(0.05)
    bgScreen((0, 0, 0), (255, 255, 255))
    clapperTime()
    scene_data()
    pygame.display.flip()


def write_openvr(mat):
    global write_queue, frame
    if mat is None:
        return
    write_queue.put_nowait([frame, mat])


def setupScene():
    text_surface = font_clock.render("SETUP SCENE IN CONSOLE", True, (255, 255, 255), (0, 0, 0))
    w, h = pygame.display.get_surface().get_size()
    text_rect = text_surface.get_rect(center=(w / 2, h / 2 - 30))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()
    a = input("do you want to change scenes? (Y/n)")
    if a != "Y":
        print("return to pygame")
        return

    a = input("ENTER SCRIPT NUMBER: ")
    global scene, shot, script
    script = a

    a = input("ENTER SCENE NUMBER: ")
    scene = a

    a = input("ENTER SHOT NUMBER [DEFAULT TO ONE]:")
    if not a.isnumeric():
        print("INVALID. DEFAULTING TO ONE")
        shot = 1
    else:
        shot = int(a)

    print(
        f"SETUP DONE. SCRIPT {script} SCENE {scene}. STARTING FROM SHOT {shot}. SHOOTING AT {framerate}fps. Happy shooting!")


def selectTracker():
    text_surface = font_clock.render("SELECT TRACKER IN CONSOLE", True, (255, 255, 255), (0, 0, 0))
    w, h = pygame.display.get_surface().get_size()
    text_rect = text_surface.get_rect(center=(w / 2, h / 2 - 30))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()

    print("SELECT A TRACKER")
    print("==Trackers List======")
    print("--[TRACKER ID] | Tracker Info--")
    for tracker in openvr_streamer_minimal.trackers:
        print(f"[{tracker}] | {openvr_streamer_minimal.trackers[tracker]}")

    print("=====================")
    selection = input("Select the target tracker ID: ")

    if selection not in openvr_streamer_minimal.trackers:
        print("INVALID SELECTION. ABORTING.")
        return

    print(f"YOU HAVE SELECTED TRACKER [{selection}]")
    openvr_streamer_minimal.tracker_target = selection


def startRecording():
    # Safety checks
    global recording, file_dialog
    if file_dialog is not None:
        file_dialog.kill()
        file_dialog = None

    if openvr_streamer_minimal.tracker_target == "" or None:
        print("ERROR! TARGET TRACKER NOT SET!")
        return

    if save_directory is None:
        print("ERROR! SAVE DIRECTORY NOT YET DEFINED!")
        return

    # Start rec
    recording = True

    # TODO: start steamvr rec
    # start filewrite thread
    global write_thread, write_queue
    print("clearing queue...")
    print(f"{write_queue.qsize()} ->")
    with write_queue.mutex:
        write_queue.queue.clear()
    print(write_queue.qsize())

    print("starting write thread...")
    write_thread = threading.Thread(target=fileWriteThread)
    write_thread.start()

    global frame
    frame = 0

    print("===RECORDING START===")


def stopRecording():
    # save file
    global recording, write_thread, write_queue

    recording = False

    if write_thread is not None:
        print("Finalizing write...")
        write_thread.join()
        print("write thread stopped.")


    # print(f"{write_queue.qsize()} <")
    # next shot
    global shot
    shot += 1

    print("==RECORDING STOPPED==")


# pygame setup
pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE, 32)
manager = pygame_gui.UIManager((80000, 60000))
pygame.display.set_caption("KIVI Recorder")
clock = pygame.time.Clock()
pygame.font.init()
font = pygame.font.SysFont('MicrogrammaDOT-BolExt', 20)
font_clock = pygame.font.SysFont('MicrogrammaDOT-BolExt', 40)
font_big = pygame.font.SysFont('MicrogrammaDOT-BolExt', 50)
blip_font = pygame.font.SysFont("Segoe UI Emoji", 40)

info_text = "KIVI Recorder"
recording = False

# Data structure: List[2]: [frame-index, val(True:bool for flash, string for pose)]
write_queue = queue.Queue(maxsize=0)
write_thread: threading.Thread
atexit.register(stopRecording)

flashed = False

# Rec info
script = "00"
scene = "00"
shot = 1
save_directory = None

file_dialog = None

# Enable OpenVR
openvr_streamer_minimal.enableStreaming()

frame = 0

while True:
    time_delta = clock.tick(framerate)
    tic = time.perf_counter()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            stopRecording()
            openvr_streamer_minimal.disableStreaming()
            quit()

        if (event.type == pygame_gui.UI_WINDOW_CLOSE
                and event.ui_element == file_dialog):
            file_dialog = None

        if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            try:
                save_directory = create_resource_path(event.text)
                print(save_directory)
            except pygame.error:
                print("OH NO ERROR IN PICKING SAVE DIRECTORY")

        manager.process_events(event)

    if not recording:
        bgScreen((255, 0, 95), (0, 0, 0))
        stoppedText()

        keys = pygame.key.get_just_released()
        if keys[pygame.K_p]:
            startRecording()
        if keys[pygame.K_n]:
            setupScene()
        if keys[pygame.K_f] and file_dialog is None:
            file_dialog = UIFileDialog(pygame.Rect(160, 50, 440, 500),
                                       manager,
                                       window_title='Pick a recordings save directory...',
                                       initial_file_path='./',
                                       allow_picking_directories=True,
                                       allow_existing_files_only=True,
                                       allowed_suffixes={""})
        if keys[pygame.K_v]:
            selectTracker()

    else:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not flashed:
            flash()
            flashed = True
        if flashed and not keys[pygame.K_SPACE]:
            # info_text = input()
            flashed = False
        if keys[pygame.K_q]:
            stopRecording()
            recording = False
            continue

        # Openvr
        write_openvr(openvr_streamer_minimal.puppet())
        frame += 1

        bgScreen((0, 0, 0), (255, 255, 255))
        clapperTime()
        recText()

    scene_data()

    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.flip()

    toc = time.perf_counter()
    print(f"{toc - tic:0.4f}s, {1/(toc - tic):0.4f}fps")