import neat
import os
import pygame, sys
import math
import random
import time

pygame.init()
pygame.font.init()

myfont = pygame.font.SysFont('Square', 100)
pygame.display.set_caption("Pong AI")

screen = pygame.display.set_mode((720,480))
clock = pygame.time.Clock()
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def distance(pos1, pos2):
    return math.sqrt((pos1.x-pos2.x)**2 + (pos1.y-pos2.y)**2)


class Counter:
    wins_p1 = 0
    wins_p2 = 0
    def __init__(self, font):
        super().__init__()
        self.fontObj = font
        self.scoreSurface = font.render("0   0", False, WHITE)
    def update(self):
        self.scoreSurface = self.fontObj.render(f"{self.wins_p2}   {self.wins_p1}", False, WHITE)



class Player:
    col = 0
    dirv = 0

    def __init__(self, speed = 5, left=True, color=WHITE):
        if left:
            self.pos = pygame.math.Vector2((20, 480/2))
        else:
            self.pos = pygame.math.Vector2((700 , 480/2))
 
        self.speed = speed
        self.surface = pygame.Surface((10, 50))
        self.rect = self.surface.get_rect(center = (round(self.pos.x), round(self.pos.y)))
        self.surface.fill(color)

    def move(self, d):
        self.dirv = d
        self.pos.y += d * self.speed
        self.rect.center = round(self.pos.x), round(self.pos.y)



class Pong:
    def __init__(self, pos, dirv, speed=5, color=WHITE):
            self.pos = pygame.math.Vector2(pos)
            self.dirv = pygame.math.Vector2(dirv).normalize()
            self.speed = speed
            self.surface = pygame.Surface((10, 10))
            self.rect = self.surface.get_rect(center = (round(self.pos.x), round(self.pos.y)))
            self.surface.fill(color)

    def setDir(self, dirv):
        self.dirv = pygame.math.Vector2(dirv).normalize()

    def setPos(self, pos):
        self.pos = pygame.math.Vector2(pos)

    def reflect(self, NV):
        self.dirv = self.dirv.reflect(pygame.math.Vector2(NV))
    def move(self):
        self.pos += self.dirv * self.speed
        self.rect.center = round(self.pos.x), round(self.pos.y)




def player_col_det(p, window):
    if p.rect.top <= window.top:
        p.col = 1

    elif p.rect.bottom >= window.bottom:
        p.col = -1 
    else:
        p.col = 0

def pong_col_det(pon, window, pl1, pl2, counter):
    if pon.rect.top <= window.top:
        print("1")
        pon.reflect((0, 1))
    if pon.rect.bottom >= window.bottom:
        print("2")
        pon.reflect((0, -1))
    if pon.rect.right >= window.right:
        print("3")
        
        counter.wins_p2 += 1
        counter.update()
        pon.setPos((720/2, 480/2))
        pon.setDir((random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)))

    if pon.rect.left <= window.left:
        print("4")
        counter.wins_p1 += 1
        counter.update()
        pon.setPos((720/2, 480/2))
        pon.setDir((random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)))

    if pon.rect.colliderect(pl2.rect):
        print("5")
        pon.reflect((1,0))
        pon.setDir((pon.dirv.x + 0.1 *  random.random(), pon.dirv.y + 0.1 * random.random()))
        return True

    if pon.rect.colliderect(pl1.rect):
        print("6")
        pon.reflect((-1,0))
        pon.setDir((pon.dirv.x + 0.1 * random.random(), pon.dirv.y + 0.1 *  random.random()))
        return True
        




p1 = Player(left=False)
p2 = Player(left=True)

counter = Counter(myfont)
pong = Pong((720/2, 480/2), (random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)))


while True:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            sys.exit()


        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                
                if not p1.col == 1:
                    p1.move(-1)
                    
                

            if event.key == pygame.K_DOWN:
                
                if not p1.col == -1:
                    p1.move(1)
                    

                
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                p1.dirv = 0
            if event.key == pygame.K_DOWN:
                p1.dirv = 0

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                
                if not p2.col == 1:
                    p2.move(-1)
                    
                

            if event.key == pygame.K_s:
                
                if not p2.col == -1:
                    p2.move(1)
                    

                
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                p2.dirv = 0
            if event.key == pygame.K_s:
                p2.dirv = 0





    screen.fill(BLACK)
    window = pygame.draw.rect(screen, WHITE, (0, 0, 720, 480), 15)
    #pygame.draw.lines(screen, WHITE, True, [(0, 0),(0,480), (720,480),(720, 0)], 10)

    for dash in range(30):
        if dash % 2 == 0:
            pygame.draw.line(screen, WHITE, (720/2 - 3, dash * (480/30)), (720/2 - 3, dash * (480/30) + (480/30)), 10)

    player_col_det(p1, window)
    player_col_det(p2, window)
    
    if p1.col == 0:
            p1.move(p1.dirv)

    if p2.col == 0:
            p2.move(p2.dirv)


    pong_col_det(pong, window, p1, p2, counter)



    pong.move()
    

    screen.blit(counter.scoreSurface, (720/2 - counter.scoreSurface.get_width() / 2, 40))
    screen.blit(pong.surface, (pong.rect.left, pong.rect.top))
    screen.blit(p2.surface, (p2.rect.left, p2.rect.top))
    screen.blit(p1.surface, (p1.rect.left, p1.rect.top))

    pygame.display.flip()

    

























