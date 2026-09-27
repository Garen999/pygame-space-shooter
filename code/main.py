import pygame
import sys
from os.path import join

from random import randint, uniform #uniform is randint for floats

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups) #super calls from parent class (sprite) and sprite automatically added to group
        self.image = pygame.image.load(join('images','player.png')).convert_alpha() #convert() increases performance as it fits the pygame format
        self.rect = self.image.get_frect(center =(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)) #frect is a float rect
        self.direction = pygame.math.Vector2() #self states that the variable is given to all members of group
        self.speed = 300
        self.health = 9999

        # cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

        # mask
        self.mask = pygame.mask.from_surface(self.image) #reveals visible areas of a surface

    def laser_timer(self): #run continuosly
        if not self.can_shoot:
            current_time = pygame.time.get_ticks() #get_ticks gets time passed since initialising pygame in ms
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt): #function call during event loop that updates all sprites
        keys = pygame.key.get_pressed() #pressed attatches to every frame and justpressed attatches once
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a]) #boolean -> so when key is pressed holds a value of 1 and if not holds a value of 0
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction #normalize makes it so that speed when going horizontal and vertical is equal to just going either horizontal/vertical and a vector doesn't work in if statement if values are [0,0]
        self.rect.center += self.direction * self.speed * dt

        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0  
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
    
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot: #run once
            Laser(laser_surface, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
        
        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surface):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(center = (randint(0,WINDOW_WIDTH),randint(0,WINDOW_HEIGHT))) #done before program starts and so won't be attatched to every frame

class Laser(pygame.sprite.Sprite):
    def __init__(self, surface, pos, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(midbottom = pos)

    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0: #destroys laser if it leaves screen
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surface, pos, groups):
        super().__init__(groups)
        self.original_surface = surface
        self.image = surface
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5,0.5),1)
        self.speed = randint(400,500)
        self.rotation_speed = randint(40,80)
        self.rotation = 0

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
 
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surface, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center) #makes meteors have more natural movement

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0 
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)

    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

def collisions():
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask) #thrid parameter decides if sprite group is destroyed in collision and if destroyed can be accessed temporarily
    if collision_sprites:
        damage_sound.play()
        player.health -= 2500

    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()

def display_score(start_time):
    current_time = pygame.time.get_ticks()
    elapsed_time = current_time - start_time
    text_surface = font.render(str(elapsed_time), True, (240,240,240)) #second parameter is anti-aliasing (smoothing out edges)
    text_rect = text_surface.get_frect(midbottom = (WINDOW_WIDTH/2, WINDOW_HEIGHT - 50))
    display_surface.blit(text_surface, text_rect)
    pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,10).move(0,-8), 5, 10) #inflate grows/shrinks rectangle

def display_health(health):
    if health > 6666:
        text_surface = font.render(str(health), True, 'green')
    elif health > 3333:
        text_surface = font.render(str(health), True, 'yellow')
    elif health > 0:
        text_surface = font.render(str(health), True, 'red')

    text_rect = text_surface.get_frect(topright = (WINDOW_WIDTH - 50, 50))
    display_surface.blit(text_surface, text_rect)


# general setup
pygame.init() #initalises pygame
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) #brackets needed as one argument (tuple) is expected
pygame.display.set_caption("Spaceship Shooter")
clock = pygame.time.Clock() #controls framerate

# import
star_surface = pygame.image.load(join('images','star.png')).convert_alpha() #so that surface isn't imported 20 times and only rectangles are for efficiency
meteor_surface = pygame.image.load(join('images','meteor.png')).convert_alpha()
laser_surface = pygame.image.load(join('images','laser.png')).convert_alpha()
game_over_font = pygame.font.Font(join('fonts','PressStart2P-Regular.ttf'), 100)
title_font = pygame.font.Font(join('fonts','PressStart2P-Regular.ttf'), 50)
font = pygame.font.Font(join('fonts','Oxanium-Bold.ttf'), 40) #default font is none
explosion_frames = [pygame.image.load(join('images','explosion',f'{i}.png')).convert_alpha() for i in range(21)]

laser_sound = pygame.mixer.Sound(join('sound','laser.wav')) #Sound has capital S
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('sound','explosion.wav'))
damage_sound = pygame.mixer.Sound(join('sound','damage.ogg'))
game_music = pygame.mixer.Sound(join('sound','game_music.wav'))

# sprites
all_sprites = pygame.sprite.Group() #capital G needed for Group
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group() 
for i in range(20):
    Star(all_sprites, star_surface) #stars must be created before so that player is above stars
player = Player(all_sprites) #only attatch sprite to a variable if it will be reused

def start_screen():
    start_screen = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True
        
        display_surface.fill((0,0,0))
        prompt_surface = title_font.render("PRESS ENTER TO START", True, (240,240,240))
        prompt_rect = prompt_surface.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        display_surface.blit(prompt_surface, prompt_rect)

        pygame.display.update()

def difficulty_selecter():
    easy_surface = title_font.render("EASY", True, (240,240,240))
    easy_rect = easy_surface.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 100))
    medium_surface = title_font.render("MEDIUM", True, (240,240,240))
    medium_rect = medium_surface.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
    hard_surface = title_font.render("HARD", True, (240,240,240))
    hard_rect = hard_surface.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 100))
    choice_surface = font.render("Select Your Difficulty", True, (240,240,240))
    choice_Rect = choice_surface.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 200))
        
    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_rect.collidepoint(event.pos):
                    start_time = pygame.time.get_ticks()
                    return start_time, 'easy'
                if medium_rect.collidepoint(event.pos):
                    start_time = pygame.time.get_ticks()
                    return start_time, 'medium'
                if hard_rect.collidepoint(event.pos):
                    start_time = pygame.time.get_ticks()
                    return start_time, 'hard'
                
        display_surface.fill((0,0,0))

        display_surface.blit(easy_surface, easy_rect)
        display_surface.blit(medium_surface, medium_rect)
        display_surface.blit(hard_surface, hard_rect)
        display_surface.blit(choice_surface, choice_Rect)

        if easy_rect.collidepoint(mouse_pos):
            easy_surface = title_font.render("EASY", True, 'green')
        else:
            easy_surface = title_font.render("EASY", True, (240,240,240))
        if medium_rect.collidepoint(mouse_pos):
            medium_surface = title_font.render("MEDIUM", True, 'yellow')
        else:
            medium_surface = title_font.render("MEDIUM", True, (240,240,240))
        if hard_rect.collidepoint(mouse_pos):
            hard_surface = title_font.render("HARD", True, 'red')
        else:
            hard_surface = title_font.render("HARD", True, (240,240,240))

        pygame.display.update()

def main_game(start_time, difficulty):
    running = True

    game_music.play(loops = -1) #-1 is indefinite looping
    game_music.set_volume(0.1)

    if difficulty == "easy":
        spawn_rate = 400
    elif difficulty == "medium":
        spawn_rate = 200
    elif difficulty == "hard":
        spawn_rate = 100

    # custom events -> meteor event
    # interval timer
    meteor_event = pygame.event.custom_type()   
    pygame.time.set_timer(meteor_event, spawn_rate) #second parameter is duration of event in ms 
        
    while running:
        dt = clock.tick() / 1000 #empty -> max frame rate and dt = 1/frame rate
        # event loop
        for event in pygame.event.get(): #checks for different events
            if event.type == pygame.QUIT:
                running = False
            if event.type == meteor_event:
                x,y = randint(0, WINDOW_WIDTH), randint(-200,-100)
                Meteor(meteor_surface, (x,y), (all_sprites, meteor_sprites))

        # update
        all_sprites.update(dt)

        collisions()
        if player.health <= 0:
            final_score = (pygame.time.get_ticks() - start_time)
            return final_score

        # draw the game
        display_surface.fill('#3a2e3f')
        display_score(start_time)
        display_health(player.health)
        all_sprites.draw(display_surface)

        pygame.display.update() #takes all elements in while loop and draws on surface

def game_over(final_score):
    start_screen = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False

        game_music.stop()
        display_surface.fill((0,0,0))
        game_over_surface = game_over_font.render("GAME OVER", True, (240,240,240))
        game_over_rect = game_over_surface.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        score_surface = font.render(f"Score: {final_score}", True, (240,240,240))
        score_rect = score_surface.get_frect(topright = (WINDOW_WIDTH -50, 50))
        prompt_surface = font.render("Press Enter to Play Again or Press ESC to Quit", True, (240,240,240))
        prompt_rect = prompt_surface.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 80))

        display_surface.blit(game_over_surface, game_over_rect)
        display_surface.blit(score_surface, score_rect)
        display_surface.blit(prompt_surface, prompt_rect)

        pygame.display.update()

start_screen()
start_time, difficulty = difficulty_selecter()

while True:
    final_score = main_game(start_time, difficulty)
    play_again = game_over(final_score)

    if play_again:
        player.health = 9999
        start_time = pygame.time.get_ticks()
        difficulty = difficulty
        continue
    else:
        break

pygame.quit() #closes game properly by uninitialising everything (opposite to init)
