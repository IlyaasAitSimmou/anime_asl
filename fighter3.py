import pygame
from random import randint

class Fighter():
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0 # 0:idle #1:run #2:jump #3:attack1 #4:attack2 #5:hit #6:death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80*2, 180*2))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.attack_sound = sound
        shield_fx = pygame.mixer.Sound(f'assets/audio/shield_fx/shield{randint(1, 5)}.wav')
        shield_fx.set_volume(6)
        self.shield_sound = shield_fx
        self.defending = False
        self.hit = False
        self.alive = True
        self.health = 100

    def load_images(self, sprite_sheet, animation_steps):
        # extract images from spritesheet
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(self.size*x, self.size*y, self.size, self.size)
                temp_img_list.append(pygame.transform.scale(temp_img, (self.size*self.image_scale, self.size*self.image_scale)))
            animation_list.append(temp_img_list)
        return animation_list

    # def move(self, screen_width, screen_height, target):
    #     gravity = 2
    #     speed = 10
    #     dx = 0
    #     dy = 0
    #     self.running = False
    #     self.attack_type = 0

    #     # get keypresses
    #     key = pygame.key.get_pressed()


    #     # can only perform other actions if not currently attacking
    #     if self.attacking == False and self.alive:
    #         # check player 1 controls
    #         if self.player == 1:
    #             # movement
    #             if key[pygame.K_a]:
    #                 dx = -speed
    #                 self.running = True
    #             if key[pygame.K_d]:
    #                 dx = speed
    #                 self.running = True
    #             # jumping
    #             if key[pygame.K_w] and self.jump == False:
    #                 self.vel_y = -30
    #                 self.jump = True
    #             # attack
    #             if key[pygame.K_r] or key[pygame.K_t]:
    #                 self.attack(target)
    #                 if key[pygame.K_r]:
    #                     self.attack_type = 1
    #                 if key[pygame.K_t]:
    #                     self.attack_type = 2
                
    #             # check player 2 controls
    #         if self.player == 2:
    #             # movement
    #             if key[pygame.K_LEFT]:
    #                 dx = -speed
    #                 self.running = True
    #             if key[pygame.K_RIGHT]:
    #                 dx = speed
    #                 self.running = True
    #             # jumping
    #             if key[pygame.K_UP] and self.jump == False:
    #                 self.vel_y = -30
    #                 self.jump = True
    #             # attack
    #             if key[pygame.K_j] or key[pygame.K_k]:
    #                 self.attack(target)
    #                 if key[pygame.K_j]:
    #                     self.attack_type = 1
    #                 if key[pygame.K_k]:
    #                     self.attack_type = 2

        
    #     # apply gravity
    #     self.vel_y += gravity
    #     dy += self.vel_y

    #     # ensure player stays on screen
    #     if self.rect.left + dx < 0:
    #         dx = 0 - self.rect.left
    #     if self.rect.right + dx > screen_width:
    #         dx = screen_width - self.rect.right
    #     if self.rect.bottom + dy > screen_height - 110:
    #         self.vel_y = 0
    #         self.jump = False
    #         dy = screen_height - 110 - self.rect.bottom

    #     # ensure players face each other
    #     if target.rect.centerx > self.rect.centerx:
    #         self.flip = False
    #     else:
    #         self.flip = True

    #     # apply attack cooldown
    #     if self.attack_cooldown > 0:
    #         self.attack_cooldown -= 1

        
    #     # update player position
    #     self.rect.x += dx
    #     self.rect.y += dy
    
    def move(self, screen_width, screen_height, target, action=None, attack=0):
        if action == 'defend':
            self.defending = True
        if action == 'attack':
            if attack == 1:
                self.attack_type = 1
            if attack == 2:
                self.attack_type = 2
            self.attack(target, self.attack_type)
    # handle animation updates
    def update(self):
        # check player action
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6)
        elif self.hit:
            self.update_action(5)
        elif self.attacking:
            if self.attack_type == 1:
                self.update_action(3)
            elif self.attack_type == 2:
                self.update_action(4)

        elif self.jump == True:
            self.update_action(2)
        elif self.running == True:
            self.update_action(1)
        else:
            self.update_action(0)


        animation_cooldown = 50

        # update image
        self.image = self.animation_list[self.action][self.frame_index]

        # check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.animation_list[self.action]):
            # end animation when player dies
            if self.alive == False:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                # check if attack was executed
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20
                # check if damage was taken
                if self.action == 5:
                    self.hit = False
                    # if player was in attack, attack stops
                    self.attacking = False
                    self.attack_cooldown = 20
        

    # define attack
    # def attack(self, target):
    #     if self.attack_cooldown == 0:
    #         self.attacking = True
    #         self.attack_sound.play()
    #         attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
    #         if attacking_rect.colliderect(target.rect):
    #             target.health -= 10
    #             target.hit = True

    def attack(self, target, attack_type):
        self.attacking = True
        self.attack_sound.play()
        if not target.defending:
            if attack_type == 1:
                target.health -= 20
            elif attack_type == 2:
                target.health -= 40
        else:
            self.shield_sound.play()
        target.hit = True
        target.defending = False
        print(self.player)
    
    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
    
    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - (self.offset[0]*self.image_scale), self.rect.y - (self.offset[1]*self.image_scale)))

class Button():
    def __init__(self, border_color, main_color, width, height, x, y, text, font_size, text_color, border_width, font):
        self.color = main_color
        self.main_body = pygame.Rect((x + border_width, y, width, height))
        self.border_color = border_color
        self.border = pygame.Rect((x, y - border_width, width + 2*border_width, height + 2*border_width))
        self.font = pygame.font.Font(font, font_size)
        self.text = self.font.render(text, True, text_color)
        self.text_pos = (x + (width/2), y + (height/2))

    def draw(self, surface):
        pygame.draw.rect(surface, self.border_color, self.border)
        pygame.draw.rect(surface, self.color, self.main_body)
        surface.blit(self.text, self.text_pos)

class Effect():
    def __init__(self, animation_list, animation_cooldown):
        self.animation_list = animation_list
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.animation_cooldown = animation_cooldown
        self.animate = False
    
    def reset(self):
        self.frame_index = 0
    
    def draw(self, surface, x, y):
        if self.frame_index < len(self.animation_list) - 1:
            if pygame.time.get_ticks() - self.update_time > self.animation_cooldown:
                self.frame_index += 1
                self.update_time = pygame.time.get_ticks()
            surface.blit(self.animation_list[self.frame_index], (x, y))
        else:
            self.animate = False