import neat
import os
import pygame, sys
import math
import random
import time

pygame.init()
pygame.font.init()

myfont = pygame.font.SysFont('Square', 30)
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
    def __init__(self, pos, dirv, speed=10, color=WHITE):
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
        
        pon.reflect((0, 1))
    if pon.rect.bottom >= window.bottom:
        
        pon.reflect((0, -1))
    if pon.rect.right >= window.right:
        
        
        counter.wins_p2 += 1
        counter.update()
        pon.setPos((720/2, 480/2))
        pon.setDir((random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)))

    if pon.rect.left <= window.left:
        
        counter.wins_p1 += 1
        counter.update()
        pon.setPos((720/2, 480/2))
        pon.setDir((random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)))

    if pon.rect.colliderect(pl2.rect):
        
        pon.reflect((1,0))
        pon.setDir((pon.dirv.x + 0.1 *  random.random(), pon.dirv.y + 0.1 * random.random()))
        return True

    if pon.rect.colliderect(pl1.rect):
        
        pon.reflect((-1,0))
        pon.setDir((pon.dirv.x + 0.1 * random.random(), pon.dirv.y + 0.1 *  random.random()))
        return True
        





def draw_window(win, players, pongs):
    for player in players:
        screen.blit(player[0].surface, (player[0].rect.left, player[0].rect.top))
        screen.blit(player[1].surface, (player[1].rect.left, player[1].rect.top))

    for pong in pongs:
        screen.blit(pong.surface, (pong.rect.left, pong.rect.top))

    for dash in range(30):
            if dash % 2 == 0:
                pygame.draw.line(screen, WHITE, (720/2 - 3, dash * (480/30)), (720/2 - 3, dash * (480/30) + (480/30)), 10)
    window = pygame.draw.rect(screen, WHITE, (0, 0, 720, 480), 15)

p1 = Player(left=False)

gen = 0

def eval_genomes(genomes, config):
    global gen

    nets = []
    players = []
    genes = []
    counters = []
    pongs = []

    for genome_id, genome in genomes:
        color = (random.uniform(20,255), random.uniform(20,255), random.uniform(20,255))
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        counters.append(Counter(myfont))    
        players.append((Player(color=color), Player(color=color, left=False)))
        genes.append(genome)
        pongs.append(Pong((720/2, 480/2), (random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)), color=color))

    gen += 1

    while len(players) > 0:
        
        
        clock.tick(FPS)
        screen.fill(BLACK)
        
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()

        for x, player in enumerate(players):
            window = pygame.draw.rect(screen, WHITE, (0, 0, 720, 480), 15)
            

            col_with_pong = pong_col_det(pongs[x], window, player[0], player[1], counters[x])
            player_col_det(player[0], window)
            player_col_det(player[1], window)

            pongs[x].move()
            if col_with_pong:
                genes[x].fitness += 3

            genes[x].fitness += 0.005
            output = nets[x].activate((player[0].pos.y, player[1].pos.y, pongs[x].pos.y, pongs[x].pos.x))

            if output[0] > 0.2 and not player[0].col == 1:
                player[0].move(-1)
            if output[0] < 0.2 and output[0] > -0.2:
                player[0].move(0)
            if output[0] < -0.8 and not player[0].col == -1:
                player[0].move(1)

            if output[1] > 0.8 and not player[1].col == 1:
                player[1].move(-1)
            if output[1] < 0.2 and output[1] > -0.2:
                player[1].move(0)
            if output[1] < -0.2 and not player[1].col == -1:
                player[1].move(1)

        for x, pong in enumerate(pongs):
            if counters[x].wins_p1 > 0 or counters[x].wins_p2 > 0:
                genes.pop(x)
                nets.pop(x)
                pongs.pop(x)
                players.pop(x)

        count = myfont.render(f"Pop Count: {len(players)}, Gen: {gen}", False, WHITE)

        draw_window(window, players, pongs)
        
        screen.blit(count, (30,30))
        #screen.blit(counter.scoreSurface, (720/2 - counter.scoreSurface.get_width() / 2, 40))
        pygame.display.flip()



def run(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    winner = p.run(eval_genomes, 50)

    print(f'\nBest genome:\n{winner}')

    










if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)