import neat
import os
import pygame, sys
import math
import random
import time


#### Basic pygame setup ###

pygame.init()
pygame.font.init()

myfont = pygame.font.SysFont('Square', 30)
pygame.display.set_caption("Pong AI")

screen = pygame.display.set_mode((720,480))
clock = pygame.time.Clock()
FPS = 30

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def distance(pos1, pos2): 
    return math.sqrt((pos1.x-pos2.x)**2 + (pos1.y-pos2.y)**2)


# keeps track of score and displays if implemented in the gameloop
class Counter:
    wins_p1 = 0
    wins_p2 = 0
    def __init__(self, font):
        super().__init__()
        self.fontObj = font
        self.scoreSurface = font.render("0   0", False, WHITE)
    def update(self):
        self.scoreSurface = self.fontObj.render(f"{self.wins_p2}   {self.wins_p1}", False, WHITE)


# Player object, mostly for rendering
class Player:
    col = 0 # collisions flag: 1 = up, 0 = none -1 = down
    dirv = 0 # direction vector

    def __init__(self, speed = 5, left=True, color=WHITE):
        if left:
            self.pos = pygame.math.Vector2((10, 480/2))
        else:
            self.pos = pygame.math.Vector2((710 , 480/2))
 
        self.speed = speed
        self.surface = pygame.Surface((5, 80))
        self.rect = self.surface.get_rect(center = (round(self.pos.x), round(self.pos.y)))
        self.surface.fill(color)

    def move(self, d):
        self.dirv = d
        self.pos.y += d * self.speed
        self.rect.center = round(self.pos.x), round(self.pos.y)




# Pong Object, mostly for rendering
class Pong:
    def __init__(self, pos, dirv, speed=7, color=WHITE):
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



# checks if a player collides with the window and sets a flag
def player_col_det(p, window): 
    if p.rect.top <= window.top:
        p.col = 1

    elif p.rect.bottom >= window.bottom:
        p.col = -1 
    else:
        p.col = 0


# checks if the pong hits an obstacle and reflects off of it, return True if collision with player
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
        



# projects all players and pongs to the pygame screen 
def draw_window(win, players, pongs):
    for player in players:
        screen.blit(player[0].surface, (player[0].rect.left, player[0].rect.top))
        screen.blit(player[1].surface, (player[1].rect.left, player[1].rect.top))

    for pong in pongs:
        screen.blit(pong.surface, (pong.rect.left, pong.rect.top))

    for dash in range(30):
            if dash % 2 == 0:
                pygame.draw.line(screen, WHITE, (int(720/2 - 3), int(dash * (480/30))), (int(720/2 - 3), int(dash * (480/30) + (480/30))), 10)
    window = pygame.draw.rect(screen, WHITE, (0, 0, 720, 480), 15)



gen = 0 # keeps track of current generation for rendering


# evaluate the fitness of each genome in the current generation
def eval_genomes(genomes, config):
    global gen

    nets = []
    players = [] # a player object consists of a tuple of a player pair (one left, one right)
    genes = []
    counters = []
    pongs = []

    for genome_id, genome in genomes:
        color = (random.uniform(50,255), random.uniform(50,255), random.uniform(50,255))
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        counters.append(Counter(myfont))    
        players.append((Player(color=color), Player(color=color, left=False)))
        genes.append(genome)
        pongs.append(Pong((720/2, 480/2), (random.choice([-1,1]), random.uniform(-0.5, 0.5)), color=color))

    gen += 1

    while len(players) > 0:  # pygame mainloop, as long as player pairs are alive
        
        clock.tick(FPS)
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()

        window = pygame.draw.rect(screen, WHITE, (0, 0, 720, 480), 15)


        ## evaluate each player pairs fitness and their genes ouputs for the next move 

        for x, player in enumerate(players):
            col_with_pong = pong_col_det(pongs[x], window, player[0], player[1], counters[x])
            player_col_det(player[0], window)
            player_col_det(player[1], window)

            pongs[x].move()

            if col_with_pong:
                genes[x].fitness += 10  #  one of the players in the pair hits the pong, their fitness increases


            # depending on the output of net net, the players act accordingly

            output = nets[x].activate((player[0].pos.y, pongs[x].pos.y)) # Feed forward with y pos of players and y pos of the ball
            output2 = nets[x].activate((player[1].pos.y, pongs[x].pos.y))

            # left player

            if output[0] > 0.66 and not player[0].col == 1:
                player[0].move(-1) # move up
            if output[0] < 0.66 and output[0] > 0.33:
                player[0].move(0) # don't move
            if output[0] < 0.33 and not player[0].col == -1:
                player[0].move(1) # move down

            # right player

            if output2[0] > 0.66 and not player[1].col == 1:
                player[1].move(-1)
            if output2[0] < 0.66 and output2[0] > 0.33:
                player[1].move(0)
            if output2[0] < 0.33 and not player[1].col == -1:
                player[1].move(1)

        

        for x, player in enumerate(players):
            
            # remove the player pair from the alive population when their pong gets behind one of their lines

            if counters[x].wins_p1 == 1 or counters[x].wins_p2 == 1:
                players.remove(player)
                counters.remove(counters[x])
                pongs.remove(pongs[x])
                genes.remove(genes[x])
                nets.remove(nets[x])
                

        count = myfont.render(f"Pop Count: {len(players)}, Gen: {gen}", False, WHITE)
        
        draw_window(window, players, pongs)
        screen.blit(count, (30,30))

        pygame.display.flip()



def run(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    winner = p.run(eval_genomes, 300)

    print(f'\nBest genome:\n{winner}')


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)