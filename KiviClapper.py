import datetime
import pygame
import winsound

thread = None
kill_thread = False
flash_now = False

info_text = "KIVI Clapperboard"


def updateScreen(bg, text_color):
    screen.fill(bg)
    text_surface = font.render(info_text, True, text_color)
    screen.blit(text_surface, (10, 10))
    updateTime()
    pygame.display.flip()


dot = 0


def updateTime():
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
    text_rect = text_surface.get_rect(center=(w / 2, h / 2))
    screen.blit(text_surface, text_rect)

    blip_text = blip_font.render(add, True, (255, 255, 255), (0, 0, 0))
    screen.blit(blip_text, text_surface.get_rect(center=(w / 2 + 480, h / 2)))


def flash():
    updateScreen((255, 255, 255), (0, 0, 0))
    # Clap
    winsound.Beep(1000, 50)
    # time.sleep(0.05)
    updateScreen((0, 0, 0), (255, 255, 255))


# pygame setup
pygame.init()
screen = pygame.display.set_mode((800, 500), pygame.RESIZABLE, 32)
pygame.display.set_caption("Clapperboard")
clock = pygame.time.Clock()
pygame.font.init()
font = pygame.font.SysFont('MicrogrammaDOT-BolExt', 20)
font_clock = pygame.font.SysFont('MicrogrammaDOT-BolExt', 40)
blip_font = pygame.font.SysFont("Segoe UI Emoji", 40)

flashed = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and not flashed:
        flash()
        flashed = True
    if flashed and not keys[pygame.K_SPACE]:
        info_text = input()
        flashed = False

    updateScreen((0, 0, 0), (255, 255, 255))

    clock.tick(29.97)
