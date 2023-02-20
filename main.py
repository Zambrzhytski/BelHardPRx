
import csv
import os
import random
import neat
import math
import sys


import pygame

from pygame.math import Vector2
from pygame.draw import rect

pygame.init()

width = 800
height = 600
screen = pygame.display.set_mode([800, 600])

done = False

start = True

clock = pygame.time.Clock()

generation = 0


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


color = lambda: tuple([random.randint(0, 255) for i in range(3)])
GRAVITY = Vector2(0, 0.96)




class Player(pygame.sprite.Sprite):

    win: bool
    died: bool

    def __init__(self, name, image, platforms, pos, *groups):

        super().__init__(*groups)
        self.onGround = False
        self.platforms = platforms
        self.died = False
        self.win = False

        self.name = name
        self.image = pygame.transform.smoothscale(image, (32, 32))
        self.rect = self.image.get_rect(center=pos)
        self.jump_amount = 12
        self.particles = []
        self.isjump = False
        self.vel = Vector2(0, 0)
        self.angle = 0
        self.jumps_count = 0

    def draw_particle_trail(self, x, y, color=(255, 255, 255)):

        self.particles.append(
            [[x - 5, y - 8], [random.randint(0, 25) / 10 - 1, random.choice([0, 0])],
             random.randint(5, 8)])

        for particle in self.particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= 0.5
            particle[1][0] -= 0.4
            rect(alpha_surf, color,
                 ([int(particle[0][0]), int(particle[0][1])], [int(particle[2]) for i in range(2)]))
            if particle[2] <= 0:
                self.particles.remove(particle)

    def collide(self, yvel, platforms):
        global coins

        for p in platforms:
            if pygame.sprite.collide_rect(self, p):

                if isinstance(p, Spike):
                    self.died = True

                if isinstance(p, Platform) or isinstance(p, HalfBlock):

                    if yvel > 0:
                        self.rect.bottom = p.rect.top
                        self.vel.y = 0

                        self.onGround = True

                        self.isjump = False
                    elif yvel < 0:
                        self.rect.top = p.rect.bottom
                    else:
                        self.vel.x = 0
                        self.rect.right = p.rect.left
                        self.died = True

    def jump(self):
        self.vel.y = -self.jump_amount

    def doJump(self):
        self.isjump = True
        self.jumps_count += 1

    def update(self):
        if self.isjump:
            if self.onGround:
                self.jump()

        if not self.onGround:
            self.vel += GRAVITY

            if self.vel.y > 100: self.vel.y = 100

        self.collide(0, self.platforms)

        self.rect.top += self.vel.y

        self.onGround = False


        self.collide(self.vel.y, self.platforms)






class Draw(pygame.sprite.Sprite):

    def __init__(self, image, pos, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=(pos[0], pos[1]))
        self.pos = pos


class Platform(Draw):

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class Spike(Draw):

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class HalfBlock(Draw):

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)



def calc_dist(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]

    return math.sqrt(dx ** 2 + dy ** 2)


spikes = []
spike_groups = []

def init_level(map):
    x = 0
    y = 0

    for row in map:
        for col in row:

            if col == "0":
                Platform(block, (x, y), elements)

            if col == "1":
                HalfBlock(half_block, (x, y), elements)

            if col == "2":
                s = Spike(spike, [x, y, 1], elements)

                if spike_groups:
                    last_spike = spikes[-1]
                    if x - last_spike.pos[0] == 32:
                        spike_groups[-1].pos[2] += 1
                        pass
                    else:
                        spike_groups.append(s)
                else:
                    spike_groups.append(s)

                spikes.append(s)

            x += 32
        y += 32
        x = 0

    spike_groups.sort(key=lambda x: x.pos[0])

def get_closest_spike(player_x):
    for s in spike_groups:
        if s.pos[0] > player_x:
            return s.pos

    return None


def blitRotate(surf, image, pos, originpos: tuple, angle: float):

    w, h = image.get_size()
    box = [Vector2(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
    box_rotate = [p.rotate(angle) for p in box]

    min_box = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
    max_box = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])
    pivot = Vector2(originpos[0], -originpos[1])
    pivot_rotate = pivot.rotate(angle)
    pivot_move = pivot_rotate - pivot

    origin = (pos[0] - originpos[0] + min_box[0] - pivot_move[0], pos[1] - originpos[1] - max_box[1] + pivot_move[1])

    rotated_image = pygame.transform.rotozoom(image, angle, 1)

    surf.blit(rotated_image, origin)


def block_map(level_num):

    lvl = []
    with open(level_num, newline='') as csvfile:
        trash = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in trash:
            lvl.append(row)
    return lvl


def reset():
    global avatars, p_c, tomato_in, spikes, spike_groups, TravelDist, elements, player_sprite, level

    if level == 1:
        pygame.mixer.music.load(os.path.join("music", "castle-town.mp3"))
    elements = pygame.sprite.Group()
    TravelDist = 150
    spikes = []
    spike_groups = []
    tomato_in = False

    avatars = ["Bloody", "Ghost", "Haze", "Ice", "Lime", "Orange", "Samurai", "Sub-Zero", "Sunny", "Vampire", "Tomato"]
    p_c = random.choice(avatars)
    avatars.remove(p_c)

    init_level(
        block_map(
            level_num=levels[level]))


def move_map():

    global TravelDist
    TravelDist += CameraX

    for sprite in elements:
        sprite.rect.x -= CameraX


def draw_stats(surf, money=0):

    global fill
    progress_colors = [pygame.Color("red"), pygame.Color("orange"), pygame.Color("yellow"), pygame.Color("lightgreen"),
                       pygame.Color("green")]

    tries = font.render(f" Attempt {str(attempts)}", True, WHITE)
    BAR_LENGTH = 600
    BAR_HEIGHT = 10

    fill += 0.5
    outline_rect = pygame.Rect(0, 0, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(0, 0, fill, BAR_HEIGHT)
    col = progress_colors[int(fill / 100)]
    rect(surf, col, fill_rect, 0, 4)
    rect(surf, WHITE, outline_rect, 3, 4)
    screen.blit(tries, (BAR_LENGTH, 0))


def resize(img, size=(32, 32)):

    resized = pygame.transform.smoothscale(img, size)
    return resized



font = pygame.font.SysFont("lucidaconsole", 20)
dname_font = pygame.font.SysFont("Roboto Condensed", 30)
heading_font = pygame.font.SysFont("Roboto Condensed", 70)

avatar = pygame.image.load(os.path.join("images", "avatar.png"))  # load the main character
pygame.display.set_icon(avatar)
alpha_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

elements = pygame.sprite.Group()

spike = pygame.image.load(os.path.join("images", "spike-up.png"))
spike = resize(spike)

block = pygame.image.load(os.path.join("images", "block.png"))
block = pygame.transform.smoothscale(block, (32, 32))

half_block = pygame.image.load(os.path.join("images", "half-block.png"))
half_block = pygame.transform.smoothscale(half_block, (32, 32))

fill = 0
num = 0
CameraX = 0
TravelDist = 150
attempts = 0
coins = 0
angle = 0
level = 0

particles = []
orbs = []
win_cubes = []

levels = ["GD1.csv"]
level_list = block_map(levels[level])
level_width = (len(level_list[0]) * 32)
level_height = len(level_list) * 32
init_level(level_list)

pygame.display.set_caption('Pydash: Geometry Dash in Python')

text = font.render('image', False, (255, 255, 0))

bg = pygame.image.load(os.path.join("images", "bg.png"))

avatars = ["Bloody", "Ghost", "Haze", "Ice", "Lime", "Orange", "Samurai", "Sub-Zero", "Sunny", "Vampire", "Tomato"]
p_c = random.choice(avatars)
avatars.remove(p_c)
tomato_in = False
players = []


def run_game(genomes, config):
    global tomato_in, CameraX, done, players, generation

    generation += 1
    players = []
    nets = []


    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        if not tomato_in:
            tomato_in = True
            rand_av = p_c
            avatar = pygame.image.load(os.path.join("images", f"avatars/{rand_av}.png"))
        else:
            rand_av = random.choice(avatars)
            avatar = pygame.image.load(os.path.join("images", f"avatars/{rand_av}.png"))
        players.append(Player(rand_av, avatar, elements, (150, 150)))

    while not done:
        screen.blit(bg, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if len(players) == 0:
            reset()
            break

        for i, player in enumerate(players):
            closest_spike = get_closest_spike(TravelDist)
            output = nets[i].activate((
                closest_spike[0] - TravelDist,
                abs(closest_spike[1] - player.rect.y),
                closest_spike[2] * 32,
            ))


            genomes[i][1].fitness = int((TravelDist - 150) / 100)

            if output[0] < 0.5 and player.isjump == False:
                player.doJump()
                genomes[i][1].fitness -= 5

        for j, player in enumerate(players):
            players[j].vel.x = 6


            player.update()
            CameraX = player.vel.x


            if player.isjump:
                players[j].angle -= 8.1712
                blitRotate(screen, player.image, player.rect.center, (16, 16), player.angle)
            else:
                screen.blit(player.image, player.rect)

            if player.died:
                genomes[j][1].fitness -= 50
                players.pop(j)

                genomes.pop(j)
                nets.pop(j)

        move_map()
        elements.draw(screen)

        for i, player in enumerate(players):
            if(player.died):
                continue

            dname_label = dname_font.render(player.name, True, (170, 238, 187))
            dname_label_rect = dname_label.get_rect()
            dname_label_rect.center = (player.rect.x + 20, player.rect.y - 20)
            screen.blit(dname_label, dname_label_rect)

        label = heading_font.render("Поколение: " + str(generation), True, (255, 255, 255))
        label_rect = label.get_rect()
        label_rect.center = (width / 2, 150)
        screen.blit(label, label_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    config_path = "./config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.run(run_game, 1000)

pygame.quit()
