import math
import random

import pygame
from os import path
import sys
from random import randrange, choice
from math import copysign

img_dir = path.join(path.dirname(__file__), 'data')

WIDTH = 1200
HEIGHT = 800
FPS = 60

player_legs = []
player_torso = []
alien_move = []
zombie_move = []
lizard_move = []
enemy_move = []


def img_load():
    for i in range(1, 64):
        player_legs.append(pygame.image.load(path.join(
            'data\move-legs',
            f"move-legs-00{str(i // 10) + str(i % 10)}.png"
        )).convert_alpha())
        player_torso.append(pygame.image.load(path.join(
            'data\move-torso',
            f"move-torso-00{str(i // 10) + str(i % 10)}.png"
        )).convert_alpha())
        alien_move.append(pygame.image.load(path.join(
            'data\move-alien',
            f"move-00{str(i // 10) + str(i % 10)}.png"
        )).convert_alpha())
        zombie_move.append(pygame.image.load(path.join(
            'data\move-zombie',
            f"move-00{str(i // 10) + str(i % 10)}.png"
        )).convert_alpha())
        lizard_move.append(pygame.image.load(path.join(
            'data\move-lizard',
            f"move-00{str(i // 10) + str(i % 10)}.png"
        )).convert_alpha())
    enemy_move.append(alien_move)
    enemy_move.append(zombie_move)
    enemy_move.append(lizard_move)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, difficulty, severeness):
        pygame.sprite.Sprite.__init__(self)
        self.difficulty = difficulty - 1
        self.cur_image_num = 0
        self.image = enemy_move[self.difficulty][self.cur_image_num]
        self.rect = self.image.get_rect()

        self.rand_spawn()

        self.speed = 1
        self.speedx = 0
        self.speedy = 0

        self.delay = 500
        self.damage = 10
        self.last_kick_time = self.delay

        self.playerx = 0
        self.playery = 0
        self.alfa = 0

        self.radius = 25

        self.hp = 10 * severeness

    def set_speed(self, x, y):
        self.speedx = 0
        self.speedy = 0
        xs = x - self.rect.centerx
        ys = y - self.rect.centery
        rast = (xs ** 2 + ys ** 2) ** 0.5
        if rast > 25:
            self.speedx += copysign(1, xs) * self.speed
            self.speedy += copysign(1, ys) * self.speed
        self.playerx = x
        self.playery = y
        self.cur_image_num += 1
        if self.cur_image_num >= 63:
            self.cur_image_num = 0

    def kick(self, player):
        if pygame.time.get_ticks() - self.last_kick_time > self.delay:
            self.last_kick_time = pygame.time.get_ticks()
            player.hp -= self.damage

    def rand_spawn(self):
        rand = random.randint(0, 3)
        if rand == 0:
            # UP
            self.rect.x = randrange(WIDTH - self.rect.width)
            self.rect.y = -50
        elif rand == 1:
            # DOWN
            self.rect.x = randrange(WIDTH - self.rect.width)
            self.rect.y = HEIGHT + 50
        elif rand == 2:
            # LEFT
            self.rect.x = WIDTH - 50
            self.rect.y = randrange(HEIGHT - self.rect.height)
        elif rand == 3:
            self.rect.x = -50
            self.rect.y = randrange(HEIGHT - self.rect.height)
        else:
            print('0_o')

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        self.alfa = math.degrees(math.atan2(self.playerx - self.rect.centerx, self.playery - self.rect.centery)) + 270
        self.image, self.rect = self.rotatePivoted(enemy_move[self.difficulty][self.cur_image_num], self.alfa, self.rect.center)

    def rotatePivoted(self, im, angle, pivot):
        # rotate the leg image around the pivot
        image = pygame.transform.rotate(im, angle)
        rect = image.get_rect()
        rect.center = pivot
        return image, rect


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        img_load()
        self.cur_image_num = 0
        self.image = player_torso[self.cur_image_num]
        self.image1 = player_legs[self.cur_image_num]
        self.rect = self.image.get_rect()
        self.rect.center = 600, 400
        self.hp = 100
        self.score = 0

        self.radius = 25

        self.speed = 2
        self.speedx = 0
        self.speedy = 0
        self.weapon = Weapon(*revolver)

        self.mousex = WIDTH / 2
        self.mousey = 0
        self.alfa = 0

    def shoot(self, mousex, mousey):
        return self.weapon.shoot(self.rect.centerx, self.rect.centery, mousex, mousey)

    def rotate(self, mousex, mousey):
        self.mousex, self.mousey = mousex, mousey

    def update(self):
        self.speedx = 0
        self.speedy = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_a] or keystate[pygame.K_d] or keystate[pygame.K_w] or keystate[pygame.K_s]:
            self.cur_image_num += 1
            if self.cur_image_num >= 63:
                self.cur_image_num = 0
        if keystate[pygame.K_a]:
            self.speedx = -self.speed
        if keystate[pygame.K_d]:
            self.speedx = self.speed
        if keystate[pygame.K_w]:
            self.speedy = -self.speed
        if keystate[pygame.K_s]:
            self.speedy = self.speed
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

        self.alfa = math.degrees(math.atan2(self.mousex - self.rect.centerx, self.mousey - self.rect.centery)) + 180
        self.image, self.rect = self.rotatePivoted(player_legs[self.cur_image_num], self.alfa, self.rect.center)
        self.image1, self.rect = self.rotatePivoted(player_torso[self.cur_image_num], self.alfa, self.rect.center)

    def rotatePivoted(self, im, angle, pivot):
        # rotate the leg image around the pivot
        image = pygame.transform.rotate(im, angle)
        rect = image.get_rect()
        rect.center = pivot
        return image, rect


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x0, y0, x1, y1):
        self.range = 40
        x1 += copysign(1, random.randint(-1, 0)) * random.randint(0, self.range)
        y1 += copysign(1, random.randint(-1, 0)) * random.randint(0, self.range)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((5, 5))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.centerx = x0
        self.rect.centery = y0
        self.speed = 10
        rast = ((x0 - x1) ** 2 + (y0 - y1) ** 2) ** 0.5
        c = self.speed / rast
        self.speedx = -c * (x0 - x1)
        self.speedy = -c * (y0 - y1)

        self.radius = 5

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.x < 0 or self.rect.x > WIDTH:
            self.kill()
        if self.rect.y < 0 or self.rect.y > HEIGHT:
            self.kill()


class ShotgunBullet:
    def __init__(self, x0, y0, x1, y1):
        self.list_of_bullet = []
        for i in range(20):
            self.list_of_bullet.append(Bullet(x0, y0, x1, y1))


# описание оружия
# название, задержка между выстрелами, задержка перезарядки, размер обоймы, урон, тип выстрела
revolver = ['revolver', 700, 1200, 12, 10, Bullet]
machine_gun = ['machine_gun', 117, 1200, 25, 5, Bullet]
shot_gun = ['shotgun', 857, 1900, 12, 10, ShotgunBullet]


class Weapon:
    def __init__(self, name, delay, reload, cage, damage, type_of_bullet):
        self.name = name
        self.delay = delay
        self.reload = reload
        self.cage = cage
        self.cur_cage = cage
        self.damage = damage
        self.type_of_bullet = type_of_bullet
        self.last_shoot = self.delay

    def shoot(self, x0, y0, mousex, mousey):
        if self.cur_cage > 0:
            if pygame.time.get_ticks() - self.last_shoot >= self.delay:
                self.last_shoot = pygame.time.get_ticks()
                self.cur_cage -= 1
                return self.type_of_bullet(x0, y0, mousex, mousey)
        else:
            if pygame.time.get_ticks() - self.last_shoot >= self.reload:
                self.cur_cage = self.cage


class WeaponBonus(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.weapon = choice([revolver, machine_gun, shot_gun])
        if self.weapon == revolver:
            self.image = pygame.image.load(path.join(img_dir, "pistol.png")).convert_alpha()
        elif self.weapon == machine_gun:
            self.image = pygame.image.load(path.join(img_dir, "assault-rifle.png")).convert_alpha()
        elif self.weapon == shot_gun:
            self.image = pygame.image.load(path.join(img_dir, "shotgun.png")).convert_alpha()

        self.image = pygame.transform.scale(self.image, (50, 38))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.birthday = pygame.time.get_ticks()
        self.last_blink_time = 0
        self.visible = True
        self.radius = 10

    def update(self):
        if pygame.time.get_ticks() - self.birthday >= 10000:
            self.kill()
        if pygame.time.get_ticks() - self.birthday >= 7000:
            if pygame.time.get_ticks() - self.last_blink_time >= 300:
                self.visible = not self.visible
                self.last_blink_time = pygame.time.get_ticks()
        if self.visible:
            self.image.set_alpha(128)
        else:
            self.image.set_alpha(0)


class HpBonus(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(img_dir, "powerup-medikit.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.birthday = pygame.time.get_ticks()
        self.last_blink_time = 0
        self.visible = True
        self.radius = 10

    def update(self):
        if pygame.time.get_ticks() - self.birthday >= 10000:
            self.kill()
        if pygame.time.get_ticks() - self.birthday >= 7000:
            if pygame.time.get_ticks() - self.last_blink_time >= 300:
                self.visible = not self.visible
                self.last_blink_time = pygame.time.get_ticks()
        if self.visible:
            self.image.set_alpha(128)
        else:
            self.image.set_alpha(0)


class PowerBlastBonus(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(img_dir, "powerup-fireblast.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.birthday = pygame.time.get_ticks()
        self.last_blink_time = 0
        self.visible = True
        self.radius = 10

    def update(self):
        if pygame.time.get_ticks() - self.birthday >= 10000:
            self.kill()
        if pygame.time.get_ticks() - self.birthday >= 7000:
            if pygame.time.get_ticks() - self.last_blink_time >= 300:
                self.visible = not self.visible
                self.last_blink_time = pygame.time.get_ticks()
        if self.visible:
            self.image.set_alpha(128)
        else:
            self.image.set_alpha(0)

    def shoot(self):
        self.list_of_bullet = []
        x = self.rect.centerx
        y = self.rect.centery

        self.list_of_bullet.append(Bullet(x, y, x, 0))
        self.list_of_bullet.append(Bullet(x, y, x, HEIGHT))
        self.list_of_bullet.append(Bullet(x, y, 0, y))
        self.list_of_bullet.append(Bullet(x, y, WIDTH, y))

        self.list_of_bullet.append(Bullet(x, y, x + y, 0))
        self.list_of_bullet.append(Bullet(x, y, x + (HEIGHT - y), HEIGHT))
        self.list_of_bullet.append(Bullet(x, y, x - (HEIGHT - y), HEIGHT))
        self.list_of_bullet.append(Bullet(x, y, x - y, 0))

        self.list_of_bullet.append(Bullet(x, y, x + (1/2)*y, 0))
        self.list_of_bullet.append(Bullet(x, y, x + (1/2)*(HEIGHT - y), HEIGHT))
        self.list_of_bullet.append(Bullet(x, y, x - (1/2)*(HEIGHT - y), HEIGHT))
        self.list_of_bullet.append(Bullet(x, y, x - (1/2)*y, 0))

        self.list_of_bullet.append(Bullet(x, y, x + (3 ** 0.5 / 2) * y, 0))
        self.list_of_bullet.append(Bullet(x, y, x + (3 ** 0.5 / 2) * (HEIGHT - y), HEIGHT))
        self.list_of_bullet.append(Bullet(x, y, x - (3 ** 0.5 / 2) * (HEIGHT - y), HEIGHT))
        self.list_of_bullet.append(Bullet(x, y, x - (3 ** 0.5 / 2) * y, 0))
        return self.list_of_bullet