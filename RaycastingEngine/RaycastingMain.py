
import pygame, sys, math, time, re, string, os
TEXTURE_SIZE = 256
HALF_TEXTURE_SIZE = TEXTURE_SIZE // 2
MAP = (
    '########'
    '# #    #'
    '# #  ###'
    '#      #'
    '#      #'
    '#  ##  #'
    '#   #  #'
    '########'
)

class game:
    def __init__(self):
        pygame.init()
        pygame.mouse.set_visible(False)
        self.rel = 0
        self.FPS = 0
        self.clock = pygame.time.Clock()
        self.SCREEN_HEIGHT = 1020
        self.SCREEN_WIDTH = 1920
        self.WIDTH = self.SCREEN_WIDTH
        self.HEIGHT = self.SCREEN_HEIGHT
        self.res = self.SCREEN_WIDTH, self.SCREEN_HEIGHT
        self.MAP_SIZE = 8
        self.TILE_SIZE = int((self.SCREEN_WIDTH / 2) / self.MAP_SIZE)
        self.MAX_DEPTH = 1000
        self.FOV = math.pi // 3
        self.HALF_FOV = self.FOV / 2
        self.CASTED_RAYS = 120
        self.STEP_ANGLE = self.FOV / self.CASTED_RAYS 
        self.SCALE = self.SCREEN_WIDTH // self.CASTED_RAYS
        self.HALF_WIDTH = self.SCREEN_WIDTH // 2
        self.HALF_HEIGHT = self.SCREEN_HEIGHT // 2
        self.MOUSE_SENSITIVITY = 0.0001
        self.MOUSE_MAX_REL = 40
        self.MOUSE_BORDER_LEFT = 1600
        self.MOUSE_BORDER_RIGHT = self.SCREEN_WIDTH - self.MOUSE_BORDER_LEFT
        self.player_x = (self.SCREEN_WIDTH / 2) / 2
        self.player_y = (self.SCREEN_WIDTH / 2) / 2
        self.player_angle = math.pi
        self.screen = pygame.display.set_mode(self.res)
        self.delta_time = 1
        self.forward = True
        self.PLAYER_MAX_HEALTH = 250
        self.player_health = self.PLAYER_MAX_HEALTH
        self.new_game()
        
    def new_game(self):
        self.object_renderer = ObjectRenderer(self)
        self.run()

    # game loop
    def run(self):
        self.forward = True
        while True:
            self.handle_events()
            self.update()
            self.draw()
            
            
            
    # Handling user input
    def handle_events(self):
        # Quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
        self.keys = pygame.key.get_pressed()
        # Forward
        if self.keys[pygame.K_w]:
            self.forward = True
            self.player_x += -math.sin(self.player_angle) * 2
            self.player_y += math.cos(self.player_angle) * 2 
        # Backwards
        if self.keys[pygame.K_s]:
            self.forward = False
            self.player_x -= -math.sin(self.player_angle) * 2 
            self.player_y -= math.cos(self.player_angle) * 2 
        # Left look direction
        if self.keys[pygame.K_a]:
            self.player_angle -= 0.1
        # Right look direction
        if self.keys[pygame.K_d]:
            self.player_angle += 0.1
        


        # convert target X, Y coordinate to map col, row
        self.col = int(self.player_x / self.TILE_SIZE)
        self.row = int(self.player_y / self.TILE_SIZE)
        # calculate map square index
        self.square = self.row * self.MAP_SIZE + self.col

        # player hits the wall (collision detection)
        if MAP[self.square] == '#':
            if self.forward == True:
                self.player_x -= -math.sin(self.player_angle) * 2
                self.player_y -= math.cos(self.player_angle) * 2
            else:
                self.player_x += -math.sin(self.player_angle) * 2
                self.player_y += math.cos(self.player_angle) * 2
        # Mouse looking direction
        mx, my = pygame.mouse.get_pos()
        if mx < self.MOUSE_BORDER_LEFT or mx > self.MOUSE_BORDER_RIGHT:
            pygame.mouse.set_pos([self.HALF_WIDTH, self.HALF_HEIGHT])
        self.rel = pygame.mouse.get_rel()[0]
        self.rel = max(-self.MOUSE_MAX_REL, min(self.MOUSE_MAX_REL, self.rel))
        self.player_angle += self.rel * self.MOUSE_SENSITIVITY * self.delta_time
           
                    
       
    def draw(self):
        self.object_renderer.draw()

    def update(self):
        pygame.display.set_caption(f'Raycasting Game Engine By Rylan / Frames: {self.clock.get_fps() :.1f}')
        self.object_renderer.cast_rays()
        pygame.display.flip()
        self.delta_time = self.clock.tick(self.FPS)

class ObjectRenderer():
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.sky_image = self.get_texture('Assets/sky.png', (self.game.WIDTH, self.game.HALF_HEIGHT))
        self.grass_image = self.get_texture('Assets/grass.png', (self.game.WIDTH, self.game.HALF_HEIGHT))
        self.sky_offset = 0
        self.grass_offset = 0
        self.FLOOR_COLOUR = 100, 200, 100
        self.health = self.game.player_health
        

        

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(texture, res)
    # draw 2D map
    def draw_map(self):
        for row in range(8):
            # loop over map columns
            for col in range(8):
                square = row * self.game.MAP_SIZE + col
                # draw map in the game window
                pygame.draw.rect(
                    self.screen,
                    (200, 200, 200) if MAP[square] == '#' else (100, 100, 100),
                    (col * self.game.TILE_SIZE, row * self.game.TILE_SIZE, self.game.TILE_SIZE - 2, self.game.TILE_SIZE - 2)
                )
        # draw player on 2D board
        pygame.draw.circle(self.screen, (255, 0, 0), (int(self.game.player_x), int(self.game.player_y)), 8)
        # draw player direction
        pygame.draw.line(self.screen, (0, 255, 0), (self.game.player_x, self.game.player_y),
                                        (self.game.player_x - math.sin(self.game.player_angle) * 50,
                                            self.game.player_y + math.cos(self.game.player_angle) * 50), 3)
        # draw player FOV
        pygame.draw.line(self.screen, (0, 255, 0), (self.game.player_x, self.game.player_y),
                                        (self.game.player_x - math.sin(self.game.player_angle - self.game.HALF_FOV) * 50,
                                            self.game.player_y + math.cos(self.game.player_angle - self.game.HALF_FOV) * 50), 3)
        pygame.draw.line(self.screen, (0, 255, 0), (self.game.player_x, self.game.player_y),
                                        (self.game.player_x - math.sin(self.game.player_angle + self.game.HALF_FOV) * 50,
                                            self.game.player_y + math.cos(self.game.player_angle + self.game.HALF_FOV) * 50), 3)

    def draw(self):
        self.draw_background()
        self.draw_map()
        

    def draw_background(self):
        self.WIDTH = self.game.WIDTH 
        self.HEIGHT = self.game.HEIGHT
        self.HALF_HEIGHT = self.game.HALF_HEIGHT
        self.sky_offset = (self.sky_offset + 4.5 * self.game.rel) % self.WIDTH
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + self.WIDTH, 0))
        
        
        # Floor #
        pygame.draw.rect(self.screen, self.FLOOR_COLOUR, (0, self.HALF_HEIGHT, self.WIDTH, self.HEIGHT))
         # update 2D background
        pygame.draw.rect( self.screen, (0, 0, 0), (0, 0, self.HEIGHT, self.HEIGHT))
        
        
    

      
    # raycasting algorithm
    def cast_rays(self):
        start_angle = self.game.player_angle - self.game.HALF_FOV
        # loop over casted rays
        for ray in range(self.game.CASTED_RAYS):
            # cast ray step by step
            for depth in range(self.game.MAX_DEPTH):
                # get ray target coordinates
                target_x = self.game.player_x - math.sin(start_angle) * depth
                target_y = self.game.player_y + math.cos(start_angle) * depth
                
                # covert target X, Y coordinate to map col, row
                col = int(target_x / self.game.TILE_SIZE)
                row = int(target_y / self.game.TILE_SIZE)
                
                # calculate map square index
                square = row * self.game.MAP_SIZE + col

                # ray hits the condition
                if MAP[square] == '#':
                    # highlight wall that has been hit by a casted ray
                    pygame.draw.rect(self.screen, (0, 255, 0), (col * self.game.TILE_SIZE,
                                                        row * self.game.TILE_SIZE,
                                                        self.game.TILE_SIZE - 2,
                                                        self.game.TILE_SIZE - 2))

                    # draw casted ray
                    pygame.draw.line(self.screen, (255, 255, 0), (self.game.player_x, self.game.player_y), (target_x, target_y))
                    
                    # wall shading
                    color = 255/ (1 + depth * depth * 0.0001)
            
                    # fix fish eye effect
                    depth *= math.cos(self.game.player_angle - start_angle)
                                    
                    # calculate wall height
                    self.wall_height = 21000 / (depth + 0.0001)
                    
                    # fix stuck at the wall
                    if self.wall_height > self.game.SCREEN_HEIGHT:
                        self.wall_height = self.game.SCREEN_HEIGHT 
                    # Border Rects
                    left_border = pygame.Rect(0, 0, 20, self.game.SCREEN_HEIGHT)
                    right_border = pygame.Rect(1900, 0, 20, self.game.SCREEN_HEIGHT)
                    # draw 3D projection (rectangle by rectangle...)
                    pygame.draw.rect(self.screen, (color, color, color), (self.game.SCREEN_HEIGHT + ray * self.game.SCALE - 1000,(self.game.SCREEN_HEIGHT / 2) - self.wall_height / 2, self.game.SCALE, self.wall_height))
                    pygame.draw.rect(self.screen, (0, 0 ,0), left_border)
                    pygame.draw.rect(self.screen, (0, 0 ,0), right_border)
                    break

            # increment angle by a single step
            start_angle += self.game.STEP_ANGLE



if __name__ == '__main__':
    game = game()
    game.run()    











