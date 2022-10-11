import pygame
import neat
import os
import random

pygame.font.init()

GEN = 0

# fitness change
MOVE_BONUS = 0.1
DEATH_PENALTY = -1000
JUMP_PENALTY = -1

WIN_WIDTH = 600
WIN_HEIGHT = 400
VEL = 10
score = 0
font = pygame.font.SysFont('comicsans', 30)



dino_imgs = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "dino1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "dino2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "dino1 crouch.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "dino2 crouch.png")))]

cactus_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "cactus.png")))
bg_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg2.png")))


class Dino:
    vel = VEL
    imgs = dino_imgs

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_jumping = False
        self.is_crouching = False
        self.jump_frame = 10
        self.img_count = 0
        self.img = self.imgs[0]

    def jump(self):
        self.is_crouching = False
        self.is_jumping = True

    def crouch(self):
        if self.is_crouching:
            self.is_crouching = False
        else:
            self.is_crouching = True

    def move(self):

        if self.is_jumping:
            if self.jump_frame >= -10:
                self.y -= (self.jump_frame * abs(self.jump_frame)) * 0.4
                self.jump_frame -= 1
            else:
                self.jump_frame = 10
                self.is_jumping = False

    def draw(self, win):
        self.img_count += 1

        # dino crouch
        if self.is_crouching:
            if self.img_count < self.vel:
                self.img = self.imgs[2]
            elif self.img_count < 2 * self.vel:
                self.img = self.imgs[3]
            elif self.img_count < 1 + 3 * self.vel:
                self.img = self.imgs[2]
                self.img_count = 0
        else:
            # dino run
            if self.img_count < self.vel:
                self.img = self.imgs[0]
            elif self.img_count < 2 * self.vel:
                self.img = self.imgs[1]
            elif self.img_count < 1 + 3 * self.vel:
                self.img = self.imgs[0]
                self.img_count = 0

        win.blit(self.img, (self.x, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Cactus:
    vel = VEL
    img = cactus_img
    height = img.get_height()

    def __init__(self):
        self.x = WIN_WIDTH
        self.y = 270

    def move(self):
        self.x -= self.vel

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

    def collision(self, dino):
        dino_mask = dino.get_mask()
        mask = pygame.mask.from_surface(self.img)

        offset = (self.x - dino.x, self.y - round(dino.y))
        overlap = dino_mask.overlap(mask, offset)

        if overlap:
            return True
        return False


class Base:
    img = bg_img
    vel = VEL
    width = img.get_width()

    def __init__(self):
        self.x1 = 0
        self.x2 = self.width
        self.y = 0

    def move(self):
        self.x1 -= self.vel
        self.x2 -= self.vel

        # moving image with a infinite loop of 2 images
        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width

        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def draw(self, win):
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))


def draw_window(win, bg, dinos, cactus, score, gen, vel, alive):
    bg.draw(win)
    for d in dinos:
        d.draw(win)

    for c in cactus:
        c.draw(win)

    text = font.render("Score: " + str(round(score)), 1, (100, 100, 100))
    win.blit(text, (10, 10))

    text = font.render("Gen: " + str(gen), 1, (100, 100, 100))
    win.blit(text, (10, 40))

    text = font.render("Alive: " + str(alive), 1, (100, 100, 100))
    win.blit(text, (10, 70))

    text = font.render("Speed: " + str(vel), 1, (100, 100, 100))
    win.blit(text, (10, 110))

    pygame.display.update()


def human_main():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    bg = Base()

    score = 0
    cactus_allowed_spawn = True
    spawn_count = 0

    dinos = [Dino(30, 250)]

    cactus = [Cactus()]

    clock = pygame.time.Clock()
    run = True

    while run:
        score += 0.1
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    dinos[0].jump()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    dinos[0].crouch()

        # cactus spawn
        # big cactus spawn rate 3%
        cactus_proba = random.randrange(0, 1000, 1)
        if cactus_proba > 970 and cactus_allowed_spawn:
            cactus.append(Cactus())
            cactus_allowed_spawn = False

        if not cactus_allowed_spawn:
            spawn_count += 1
            if spawn_count == 25:
                cactus_allowed_spawn = True
                spawn_count = 0

        # delete cactus
        for c in cactus:
            if c.x + c.img.get_width() < 0:
                cactus.remove(c)

        draw_window(win, bg, dinos, cactus, score, "You are the human", 1)
        bg.move()
        dinos[0].move()
        for c in cactus:
            c.move()
            for d in dinos:
                if c.collision(d):
                    dinos.remove(d)

        if len(dinos) == 0:
            run = False
            break


def ia_main(genomes, config):
    global GEN
    GEN += 1

    global VEL
    alive = len(genomes)

    genes = []
    networks = []
    dinos = []

    for _, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        networks.append(net)
        genome.fitness = 0
        genes.append(genome)
        dinos.append(Dino(30, 250))

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    bg = Base()

    score = 0
    cactus_allowed_spawn = True
    spawn_count = 0

    cactus = [Cactus()]

    clock = pygame.time.Clock()
    run = True

    while run:
        score += 0.1
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                   VEL += 10
                if event.key == pygame.K_z:
                   VEL -= 10

        # find which catcus the dino is facing
        index = 0

        for i, dino in enumerate(dinos):
            dino.move()
            genes[i].fitness += MOVE_BONUS
            if len(cactus):
                output = networks[i].activate((dino.x, abs(dino.x - cactus[0].x), abs(dino.y - cactus[0].y)))
                choice = output.index(max(output))

                if choice == 0:
                    dino.jump()
                    genes[i].fitness += JUMP_PENALTY
                if choice == 1:
                    dino.crouch()
                    genes[i].fitness -= 0.1

            if dino.is_crouching:
                genes[i].fitness -= 0.3


        # cactus spawn
        # big cactus spawn rate 3%
        cactus_proba = random.randrange(0, 1000, 1)
        if cactus_proba > 970 and cactus_allowed_spawn:
            cactus.append(Cactus())
            cactus_allowed_spawn = False

        if not cactus_allowed_spawn:
            spawn_count += 1
            if spawn_count == 25:
                cactus_allowed_spawn = True
                spawn_count = 0

        # delete cactus
        for c in cactus:
            if c.x + c.img.get_width() < 0:
                cactus.remove(c)

        draw_window(win, bg, dinos, cactus, score, GEN, VEL, alive)
        bg.move()

        # move cactus
        for i, c in enumerate(cactus):
            c.move()

            # check collision with dinos
            for d in dinos:

                # kill the dino
                if c.collision(d):
                    dinos.remove(d)
                    genes[i].fitness += DEATH_PENALTY
                    alive = alive - 1

        if len(dinos) == 0:
            run = False
            break


def run(config_path):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(ia_main, 50)



if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feed-forward.txt")
    run(config_path)


#human_main()
