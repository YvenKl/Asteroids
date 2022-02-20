import pygame
from pygame.constants import (QUIT, K_KP_PLUS, K_KP_MINUS, K_ESCAPE, KEYDOWN, K_SPACE, K_LEFT, K_RIGHT)
import os
import math
from random import randint


class Settings(object):
    window_width = 1600
    window_height = 1000
    fps = 60
    title = "Animation"
    path = {}
    path_file = os.path.dirname(os.path.abspath(__file__))
    path_image = os.path.join(path_file, "images")
    path['file'] = os.path.dirname(os.path.abspath(__file__))
    path['image'] = os.path.join(path['file'], "images")
    directions = {'stop':(0, 0), 'down':(0,  1), 'up':(0, -1), 'left':(-1, 0), 'right':(1, 0)}
    rotate = 0
    min_asteroid_vel = 2
    max_asteroid_vel = 4
    asteroid_big_cooldown = 0
    nof_max_asteroid_big = 5
    #player_vel_x = 0
    #player_vel_y = 0
    #player_base_vel = 0


    @staticmethod
    def dim():
        return (Settings.window_width, Settings.window_height)

    @staticmethod
    def filepath(name):
        return os.path.join(Settings.path['file'], name)

    @staticmethod
    def imagepath(name):
        return os.path.join(Settings.path['image'], name)


class Timer(object):
    def __init__(self, duration, with_start = True):
        self.duration = duration
        if with_start:
            self.next = pygame.time.get_ticks()
        else:
            self.next = pygame.time.get_ticks() + self.duration

    def is_next_stop_reached(self):
        if pygame.time.get_ticks() > self.next:
            self.next = pygame.time.get_ticks() + self.duration
            return True
        return False

    def change_duration(self, delta=10):
        self.duration += delta
        if self.duration < 0:
            self.duration = 0


class Animation(object):
    def __init__(self, namelist, endless, animationtime, colorkey=None):
        self.images = []
        self.endless = endless
        self.timer = Timer(animationtime)
        for filename in namelist:
            if colorkey == None:
                bitmap = pygame.image.load(Settings.imagepath(filename)).convert_alpha()
            else:
                bitmap = pygame.image.load(Settings.imagepath(filename)).convert()
                bitmap.set_colorkey(colorkey)           # Transparenz herstellen §\label{srcAnimation0101}§
            self.images.append(bitmap)
        self.imageindex = -1

    def next(self):
        if self.timer.is_next_stop_reached():
            self.imageindex += 1
            if self.imageindex >= len(self.images):
                if self.endless:
                    self.imageindex = 0
                else:
                    self.imageindex = len(self.images) - 1
        return self.images[self.imageindex]

    def is_ended(self):
        if self.endless:
            return False
        elif self.imageindex >= len(self.images) - 1:
            return True
        else:
            return False

class Asteroid(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.image = pygame.image.load(os.path.join(Settings.path_image, "Asteroid_Brown.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.left = randint(50, Settings.window_width-50)
        self.rect.top = 0
        self.speed_h = randint(Settings.min_asteroid_vel, Settings.max_asteroid_vel)
        self.speed_v = randint(Settings.min_asteroid_vel, Settings.max_asteroid_vel)
        self.image = pygame.transform.scale(self.image, (int(self.image.get_rect().width * 2.5),int(self.image.get_rect().height * 2.5)))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        self.rect.move_ip((self.speed_h, self.speed_v))
        self.off_map()

    def off_map(self):
        if self.rect.top + self.speed_v > Settings.window_height:
            self.rect.move_ip((0, -Settings.window_height))
        if self.rect.bottom + self.speed_v < 0:
            self.rect.move_ip((0, Settings.window_height))
        if self.rect.right + self.speed_h < 0:
            self.rect.move_ip((Settings.window_width, 0))
        if self.rect.left + self.speed_h > Settings.window_width:
            self.rect.move_ip((-Settings.window_width, 0))


class Background(object):
    def __init__(self, filename="background.jpg") -> None:
        super().__init__()
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename)).convert()
        self.image = pygame.transform.scale(self.image, (Settings.window_width, Settings.window_height))

    def draw(self, screen):
        screen.blit(self.image, (0, 0))


class Playership(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.ogimage = pygame.image.load("images/player_ship.png")
        self.animation = Animation([f"player_ship.png" for i in range(1)], True, 100, (0,0,0)) # §\label{srcAnimation0102}§
        self.image = self.animation.next()
        self.rect = self.image.get_rect()
        self.rect.center = (Settings.window_width // 2, Settings.window_height // 2)
        self.x_vel = 0
        self.y_vel = 0
        self.pos = 0

    def update(self):
        self.off_map()
        self.movement()
        #self.image = self.animation.next()
        self.rotate()
        self.rect.move_ip((self.x_vel, self.y_vel))

    def off_map(self):
        if self.rect.top + self.y_vel > Settings.window_height:
            self.rect.move_ip((0, -Settings.window_height-self.rect.height))
        if self.rect.bottom + self.y_vel < 0:
            self.rect.move_ip((0, Settings.window_height+self.rect.height))
        if self.rect.right + self.x_vel < 0:
            self.rect.move_ip((Settings.window_width-self.rect.left, 0))
        if self.rect.left + self.x_vel > Settings.window_width:
            self.rect.move_ip((-Settings.window_width-self.rect.height, 0))

    def movement(self):
        keys = pygame.key.get_pressed()
        #if keys[pygame.K_LEFT] and self.rect.left - Settings.player_vel_x > 0:  # links movement
            #self.rect.left -= Settings.player_vel_x
        #if keys[pygame.K_RIGHT] and self.rect.left + Settings.player_vel_x + self.get_width() < Settings.window_width:  # rechts movement
            #self.rect.left += Settings.player_vel_x
        if keys[pygame.K_UP]: #and self.rect.top - Settings.player_vel_y > 0:  # nach oben movement
            self.x_vel = self.x_vel - math.sin(math.radians(Settings.rotate))
            self.y_vel = self.y_vel - math.cos(math.radians(Settings.rotate))
            if self.x_vel <= -10:
                self.x_vel = -10
            if self.x_vel >= 10:
                self.x_vel = 10
            if self.y_vel <= -10:
                self.y_vel = -10
            if self.y_vel >= 10:
                self.y_vel = 10
            # self.rect.top += Settings.player_vel_y
            # self.rect.left += Settings.player_vel_x
        #if keys[pygame.K_DOWN] and self.rect.top + Settings.player_vel_y + self.get_height() + 15 < Settings.window_height:  # nach unten movement
            #self.rect.top += Settings.player_vel_y

    def get_width(self):
        return self.rect.width

    def get_height(self):
        return self.rect.height

    def rotate(self):
        self.image = pygame.transform.rotate(self.ogimage, Settings.rotate)
        self.rect = self.image.get_rect(center=self.rect.center)


class Game(object):
    def __init__(self) -> None:
        super().__init__()
        os.environ['SDL_VIDEO_WINDOW_POS'] = "10, 50"
        pygame.init()
        self.screen = pygame.display.set_mode(Settings.dim())
        pygame.display.set_caption(Settings.title)
        self.clock = pygame.time.Clock()
        self.playership = pygame.sprite.GroupSingle(Playership())
        self.asteroid = pygame.sprite.Group(Asteroid())
        self.running = False

    def run(self) -> None:
        self.start()
        self.running = True
        while self.running:
            self.clock.tick(Settings.fps)
            self.watch_for_events()
            self.update()
            self.draw()
        pygame.quit()

    def spawning_of_asteroids(self):
        Settings.asteroid_big_cooldown += 1
        if Settings.asteroid_big_cooldown >= 180:
            Settings.asteroid_big_cooldown = 0
            if len(self.asteroid.sprites()) < Settings.nof_max_asteroid_big:
                self.asteroid.add(Asteroid())

    def groupcollide(self):
        if pygame.sprite.groupcollide(self.playership, self.asteroid, False, False, pygame.sprite.collide_rect):
            self.running = False

    def watch_for_events(self) -> None:
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                elif event.key == K_LEFT:
                    if Settings.rotate <= 359:
                        Settings.rotate += 22.5
                        #Settings.player_vel_x = Settings.player_vel_x - math.sin(math.radians(Settings.rotate))
                        #Settings.player_vel_y = Settings.player_vel_y - math.cos(math.radians(Settings.rotate))
                    else:
                        Settings.rotate = 22.5
                        #Settings.player_vel_x = Settings.player_vel_x - math.sin(math.radians(Settings.rotate))
                        #Settings.player_vel_y = Settings.player_vel_y - math.cos(math.radians(Settings.rotate))
                elif event.key == K_RIGHT:
                    if Settings.rotate >= 1:
                        Settings.rotate -= 22.5
                    else:
                        Settings.rotate = 337.5

    def update(self) -> None:
        self.spawning_of_asteroids()
        self.playership.update()
        self.asteroid.update()
        self.groupcollide()

    def draw(self) -> None:
        self.background.draw(self.screen)
        self.playership.draw(self.screen)
        self.asteroid.draw(self.screen)
        pygame.display.flip()

    def start(self):
        self.background = Background()


if __name__ == '__main__':
    anim = Game()
    anim.run()

