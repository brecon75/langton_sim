import pygame
import random
import numpy as np

##constants (game settings)
GRID_SIZE = 30 ##small squares in edge
SQUARE_SIZE = 25  ##pixel dimension small square ka
WIDTH, HEIGHT = GRID_SIZE * SQUARE_SIZE, GRID_SIZE * SQUARE_SIZE 
WHITE = (255, 255, 255) 
BLACK = (0, 0, 0)
RED = (255, 0, 0)
PHER_RED = (255, 100, 100) ##light red
BLUE = (0, 0, 255)
PHER_BLUE = (100, 100, 255) ##light blue
PHEROMONE_DECAY_TIME = 5
FPS = 1 ##ek point ke bad kitne frames ho fark nhi padta,
# 0-5 is good for observation, 10-20 is fine for short term obs, 60 is good for long simulations

DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)] ##up, right, down, left

##ant object: x,y, dir(int), color, phertype
class ant_obj:
    def __init__(self, x, y, dir, color, pher_type):
        self.x = x ##coords are integers from 0 to GRID_SIZE-1
        self.y = y ##screen pixel dimensions are x*8, y*8, 8=SQUARE_SIZE
        self.dir = dir
        self.color = color
        self.pher_type = pher_type
    #phers is a dictionary with key as (x,y) and value as (pher_type, decay_time)
    def move(self, grid, phers):
        current_color = grid[self.y][self.x]
        if (self.x, self.y) in phers: #pheromone hai udhar
            pher_type, decay_time = phers[(self.x, self.y)]
            if pher_type == self.pher_type: ##self-pheromone recognition
                if random.random() < 0.8:
                    self.dir = self.dir
                else:
                    self.follow_standard_rule(current_color)
            else: ##cross-pher recognition, probability reversed
                if random.random() < 0.2:
                    self.dir = self.dir
                else:
                    self.follow_standard_rule(current_color)
        else:
            self.follow_standard_rule(current_color)
        grid[self.y][self.x] = 1 - grid[self.y][self.x] ##color switch
        phers[(self.x, self.y)] = (self.pher_type, PHEROMONE_DECAY_TIME) ##pheromone release
        dx, dy = DIRECTIONS[self.dir]
        self.x = (self.x + dx) % GRID_SIZE
        self.y = (self.y + dy) % GRID_SIZE

    def follow_standard_rule(self, current_color):
        if current_color == 0:
            self.dir = (self.dir + 1) % 4
        else:
            self.dir = (self.dir - 1) % 4

def draw_grid(screen, grid, ants, phers):
    for y in range(GRID_SIZE): ##init grid (all white, small squares banara)
        for x in range(GRID_SIZE):
            color = WHITE if grid[y][x] == 0 else BLACK
            pygame.draw.rect(screen, color, (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    for x in range(0, WIDTH, SQUARE_SIZE): ##grid lines
        pygame.draw.line(screen, (200, 200, 200), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, SQUARE_SIZE):
        pygame.draw.line(screen, (200, 200, 200), (0, y), (WIDTH, y))
    for (x, y), (pher_type, decay_time) in phers.items(): ##draw colored pher squares
        pher_color = PHER_RED if pher_type == "A" else PHER_BLUE
        pygame.draw.rect(screen, pher_color, (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    for ant in ants: ##maut aagyi 
        ## directional triangles plotted, ant ko represent krne k liye.
        x_pos = ant.x * SQUARE_SIZE + SQUARE_SIZE // 2
        y_pos = ant.y * SQUARE_SIZE + SQUARE_SIZE // 2
        if ant.dir == 0:
            points = [(x_pos, y_pos - SQUARE_SIZE // 2), (x_pos - SQUARE_SIZE // 2, y_pos + SQUARE_SIZE // 2), (x_pos + SQUARE_SIZE // 2, y_pos + SQUARE_SIZE // 2)]
        elif ant.dir == 1:
            points = [(x_pos + SQUARE_SIZE // 2, y_pos), (x_pos - SQUARE_SIZE // 2, y_pos - SQUARE_SIZE // 2), (x_pos - SQUARE_SIZE // 2, y_pos + SQUARE_SIZE // 2)]
        elif ant.dir == 2:
            points = [(x_pos, y_pos + SQUARE_SIZE // 2), (x_pos - SQUARE_SIZE // 2, y_pos - SQUARE_SIZE // 2), (x_pos + SQUARE_SIZE // 2, y_pos - SQUARE_SIZE // 2)]
        elif ant.dir == 3:
            points = [(x_pos - SQUARE_SIZE // 2, y_pos), (x_pos + SQUARE_SIZE // 2, y_pos - SQUARE_SIZE // 2), (x_pos + SQUARE_SIZE // 2, y_pos + SQUARE_SIZE // 2)]
        pygame.draw.polygon(screen, ant.color, points)

##decay func
def update_phers(phers):
    to_remove = []
    for key, (pher_type, decay_time) in phers.items():
        decay_time -= 1
        if decay_time <= 0:
            to_remove.append(key)
        else:
            phers[key] = (pher_type, decay_time)
    for key in to_remove:
        del phers[key] ##learnt abt del today


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ant sim")
    clock = pygame.time.Clock()
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    #ants initialised at random positions
    ants = [
        ant_obj(random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1), 0, RED, "A"),
        ant_obj(random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1), 2, BLUE, "B")
    ]
    #ants not adjacent
    while abs(ants[0].x - ants[1].x) <= 1 and abs(ants[0].y - ants[1].y) <= 1:
        ants[1].x = random.randint(0, GRID_SIZE - 1)
        ants[1].y = random.randint(0, GRID_SIZE - 1)
    phers = {}
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        for ant in ants:
            ant.move(grid, phers)
        update_phers(phers)
        screen.fill(WHITE)
        draw_grid(screen, grid, ants, phers)
        pygame.display.flip()  ##pata nhi ky krta hai docs smjh ni aaya lmao ded
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    main()

## sab chaotic hora, no highway formation after long time, but behaviour
## and game logic looks to be correct, ants are behaving as per the given rules (or my interpretation of the rules)
