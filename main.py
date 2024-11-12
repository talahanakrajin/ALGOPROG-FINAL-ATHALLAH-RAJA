import pygame
import time
import random

WIDTH, HEIGHT = 1000, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jump Jump CS")

BG = pygame.transform.scale(pygame.image.load("backgroundsprite.png"), (WIDTH, HEIGHT))

def draw(): #this part is to define the background image
    WIN.blit(BG, (0,0))
    pygame.display.update()

def main(): #This is for the main display of the game to play
    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        draw()    
    pygame.quit()

if __name__ == "__main__": #this part is for the game to run if we click the specific file
    main()