import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Super Chomsky")

WIDTH, HEIGHT = 1000, 800 #screen ratio (in pixel)
FPS = 60 
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))

#flip the image when the character is facing to the opposite direction
def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

#splitting sprite sheet for character animation
def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites
    return all_sprites


# find the exact terrain or block from the terrain folder
def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32) #SRCALPA is a function to make a png file transparent
    rect = pygame.Rect(96, 0, size, size) #the 96 and 0 are the value of x and y, on a sprite sheet if we want to access a specific sprite we use x and y to define the location
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

#load the font sprite sheet
def load_font_sprites():
    path = join("assets", "Menu", "Text", "Text-white.png")
    sprite_sheet = pygame.image.load(path).convert_alpha()
    font_sprites = {}
    char_width = 8
    char_height = 10

    for i in range(26):
        char = chr(ord('A') + i)
        x = (i % 10) * char_width
        y = (i // 10) * char_height
        surface = pygame.Surface((char_width, char_height), pygame.SRCALPHA, 32)
        rect = pygame.Rect(x, y, char_width, char_height)
        surface.blit(sprite_sheet, (0, 0), rect)
        font_sprites[char] = pygame.transform.scale2x(surface)
        print(f"Loaded character '{char}' at position {x}, {y}")

    #add space character
    space_surface = pygame.Surface((char_width, char_height), pygame.SRCALPHA, 32)
    font_sprites[' '] = pygame.transform.scale2x(space_surface)
    return font_sprites

#render the text
def render_text(text, font_sprites):
    surfaces = []
    for char in text:
        if char in font_sprites:
            surfaces.append(font_sprites[char])
       

    width = sum(surface.get_width() for surface in surfaces)
    height = max(surface.get_height() for surface in surfaces)
    text_surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)

    x_offset = 0
    for surface in surfaces:
        text_surface.blit(surface, (x_offset, 0))
        x_offset += surface.get_width()

    return text_surface

# generate playera
class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    APPEARING = load_sprite_sheets("MainCharacters", "Appearing", 96, 96, True)
    SPRITES = load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, True)
    ANIMATION_DELAY = 3

    #create the object for the player class
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.is_appearing = True
        self.jump_count = 0

    #make the character jump
    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    #move the character for x or y direction
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    #move player to the left
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    #move player to the right
    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    #called once every frame and make sure the character move to the right direction and update the animation
    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        self.fall_count += 1
        self.update_sprite()

    #make the player land and stop falling
    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    #make a player collide with an object above it
    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    #animate the character
    def update_sprite(self):
        if self.is_appearing:
            sprite_sheet = "Appearing"
            sprite_sheet_name = sprite_sheet + "_" + self.direction
            sprites = self.APPEARING[sprite_sheet_name]
            sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
            self.sprite = sprites[sprite_index]

            old_center = self.rect.center
            self.rect = self.sprite.get_rect(center=old_center)

            if self.animation_count // self.ANIMATION_DELAY >= len(sprites):
                self.is_appearing = False
                self.animation_count = 0
                self.update_sprite()
        
        else: 
            sprite_sheet = "idle"
            if self.y_vel < 0:
                if self.jump_count == 1:
                    sprite_sheet = "jump"
                elif self.jump_count == 2:
                    sprite_sheet = "double_jump"
            elif self.y_vel > self.GRAVITY * 2:
                sprite_sheet = "fall"
            elif self.x_vel != 0:
                sprite_sheet = "run"

            sprite_sheet_name = sprite_sheet + "_" + self.direction
            sprites = self.SPRITES[sprite_sheet_name]
            sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
            self.sprite = sprites[sprite_index]

            old_center = self.rect.center
            self.rect = self.sprite.get_rect(center=old_center)


        self.animation_count += 1
        self.update()

    # make a mask for collision
    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    #draw the character to the window
    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

# make the object
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name
    
    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

# modify and generate the object using the function on the super class called Object
class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

# make a fire trap
class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    # turn on the fire
    def on(self):
        self.animation_name = "on"
    
    # turn off the fire
    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

# get the background for the game
def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []
    for i in range(WIDTH // width + 1): #i divide it integerly so that i can know how many tiles do i need to make the bg image the +1 is to make sure i don't have any gaps
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


# generate the background
def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)
    
    player.draw(window, offset_x)
    pygame.display.update()

# create collision between player and object (vertically)
def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

        collided_objects.append(obj)
    
    return collided_objects

# create collision between player and object (Horizontally)
def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
    
    player.move(-dx, 0)
    player.update()
    return collided_object

# make the character move when some key is pressed
def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0 #assign to zero to stay still when the keys aren't pressed
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL)

    handle_vertical_collision(player, objects, player.y_vel)

# make the buttons for main menu
class Button:
    def __init__(self, x, y, width, height, text, font_sprites, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_sprites = font_sprites
        self.callback = callback
        self.color = (255, 165, 0)
        self.hover_color = (139, 69, 19)
        self.current_color = self.color

    #draw the button
    def draw(self, window):
        pygame.draw.rect(window, self.current_color, self.rect)
        text_surface = render_text(self.text, self.font_sprites)
        text_rect = text_surface.get_rect(center=self.rect.center)
        window.blit(text_surface, text_rect)

    #check if the button is clicked
    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.callback()

    #check if the button is hovered
    def check_hover(self, pos):
        if self.rect.collidepoint(pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.color

#start a new game
def new_game():
    main_game(window)

#load the game
def load_game():
    print("Load Game button clicked")

#quit the game
def quit_game():
    pygame.quit()
    quit()

#make the main menu
def main_menu(window):
    font_sprites = load_font_sprites()
    buttons = [
        Button(WIDTH // 2 - 100, HEIGHT // 2 - 150, 200, 50, "NEW GAME", font_sprites, new_game),
        Button(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50, "LOAD GAME", font_sprites, load_game),
        Button(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50, "QUIT GAME", font_sprites, quit_game)
    ]

    title_image = pygame.image.load(join("assets", "Menu", "Title", "title.png")).convert_alpha()
    title_rect = title_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 250))

    run = True
    while run:
        window.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    button.check_click(event.pos)

        for button in buttons:
            button.check_hover(pygame.mouse.get_pos())
            button.draw(window)
        
        window.blit(title_image, title_rect)
        pygame.display.update()

    pygame.quit()
    quit()

# make the window for the game
def main_game(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")
    
    block_size = 96

    player = Player(100, 100, 50, 50)
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()

    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size), 
               Block(block_size * 3, HEIGHT - block_size * 4, block_size), fire]


    offset_x = 0
    scroll_area_width = 200

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2 :
                    player.jump()

        player.loop(FPS)
        fire.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_vel > 0) or (
            player.rect.left - offset_x <= scroll_area_width and player.x_vel < 0)):
            offset_x += player.x_vel       
    
    pygame.quit()
    quit()
    

if __name__ == "__main__":
    main_menu(window)
