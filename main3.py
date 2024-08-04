import pygame
import random
from pygame import mixer
from fighter3 import Fighter, Button, Effect
import cv2
from inference.core.interfaces.camera.entities import VideoFrame
from inference import InferencePipeline
import supervision as sv
from datetime import datetime, timedelta
import requests
import asyncio
import aiohttp

def add_row_to_airtable( response_time, status, player, character):
    # Example usage
    personal_access_token = 'patpw8SmEpRnSk9Wc.3a46a423dce308b0f3419693a096038435e83e9a9a4dafb900cc74f4c8c25e98'
    base_id = 'app5eD0etpFEv7MEK'
    table_id = 'tblRCAJmwzEEqhQaw'
    # API URL
    url = f'https://api.airtable.com/v0/{base_id}/{table_id}'

    # Headers with authorization
    headers = {
        'Authorization': f'Bearer {personal_access_token}',
        'Content-Type': 'application/json'
    }

    # Data to be added (replace field names with actual field names in your table)
    data = {
        'fields': {
            # change response time to be a 2 digit decimal number rounded

            'response_time': str(round(float(response_time), 2)),
            'result': str(status),
            'player': str(player),
            'character': character.upper(),
        }
    }

    # Make the request to add the row
    response = requests.post(url, json=data, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        print('Row added successfully:', response.json())
    else:
        print('Failed to add row:', response.status_code, response.json())



response_time = 1.2
status = ''
player = ''
character = ''





# utilities.py


words = ['cat', 'dog', 'car', 'man', 'van', 'him', 'tan', 'can', 'oak', 'oak', 'oak']
# words = ['oak']
word = random.choice(words)

COLOR_ANNOTATOR = sv.ColorAnnotator()
LABEL_ANNOTATOR = sv.LabelAnnotator()

# Use a different name to avoid confusion with the function
start_time = None

recognized = []
def on_prediction(res: dict, frame: VideoFrame) -> None:
    global word
    global recognized
    global start_time, pipeline
    image = frame.image
    annotated_frame = image.copy()

    detections = res["predictions"]["predictions"]

    if len(detections.xyxy) > 0:

        annotated_frame = COLOR_ANNOTATOR.annotate(
            scene=annotated_frame, detections=detections
        )
        annotated_frame = LABEL_ANNOTATOR.annotate(
            scene=annotated_frame,
            detections=detections,
        )
        class_name = (detections.data)["class_name"][0]
        recognized.append(class_name)
        # Call the function

        # print(class_name)

    # Print the time difference correctly
    print(datetime.now() - start_time)

    if datetime.now() - start_time > timedelta(seconds=6):

    # Convert recognized into a set to remove duplicates and then into a list
        recognized_set = set(recognized)
        recognized_list = list(recognized_set)
        
        # Convert all items in recognized_list to lowercase
        recognized_list = [item.lower() for item in recognized_list]

        # Determine the number of items to process
        if len(recognized_list) > 2:
            recognized_list = recognized_list[:1]
            print("Processing first 3 items from recognized_list:", recognized_list)
        else:
            print("Processing all items from recognized_list:", recognized_list)

        # Loop through the filtered recognized_list and call add_row_to_airtable
        for item in recognized_list:
            add_row_to_airtable(
                str((datetime.now() - start_time).total_seconds()),  # response_time in seconds
                "correct" if item in word else "wrong",  # status
                turn,  # player
                item  # character
            )

        # Display and finalize
        cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
        cv2.moveWindow('frame', 0, 0)
        cv2.imshow('frame', annotated_frame)
        cv2.resizeWindow('frame', 500, 300)
        pipeline.terminate()
        pipeline.join()
        cv2.destroyAllWindows()
        print("closed")
        return recognized_list

    start_point = (570, 0)
    end_point = (1513, 120)

    cv2.rectangle(annotated_frame, start_point, end_point, (0, 0, 255), cv2.FILLED)

    text = word
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 5
    font_color = (255, 255, 255)
    line_type = 4

    center_x = (start_point[0] + end_point[0]) // 2
    center_y = (start_point[1] + end_point[1]) // 2

    # Get the text size
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, line_type)

    # Calculate the bottom-left corner of the text to center it
    text_x = center_x - text_width // 2
    text_y = center_y + text_height // 2

    # Add the text
    cv2.putText(annotated_frame, text, (text_x, text_y), font, font_scale, font_color, line_type)
    cv2.resizeWindow("frame", 320, 180)
    cv2.moveWindow("frame", 0, 0)
    cv2.imshow("frame", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        return


def start_pipeline():
    global start_time, pipeline
    start_time = datetime.now()
    pipeline = InferencePipeline.init_with_workflow(
        video_reference=0,
        workspace_name="nathan-yan",
        workflow_id="custom-workflow-9",
        max_fps=60,
        api_key="Zw9s4qJmfSsVpb4IerO9",
        on_prediction=on_prediction,
    )

    pipeline.start()





# Pygame

mixer.init()
pygame.init()

# create game window

screen_width, screen_height = 1000, 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('ASL Arcana')

# set framerate
clock = pygame.time.Clock()
FPS = 60

# define colors
red = (255, 0, 0)
yellow = (255, 255, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
black = (0, 0, 0)

# define game variables

intro_count = 5
last_count_update = pygame.time.get_ticks()
score = [0, 0]
round_over = False
round_over_cooldown = 2000
plyr1_action = ''
plyr2_action = ''
plyr1_potions = 5
plyr2_potions = 5
plyr_1_turns = 0
plyr_2_turns = 0
attack = 0
turn = 1
double_animate = 0
last_time = 0
last_clicked1 = pygame.time.get_ticks()
last_clicked2 = pygame.time.get_ticks()
count = 0

# define fighter variables

warrior_size = 162
warrior_scale = 4
warrior_offset = [72, 56]
warrior_data = [warrior_size, warrior_scale, warrior_offset]

wizard_size = 250
wizard_scale = 3
wizard_offset = [112, 107]
wizard_data = [wizard_size, wizard_scale, wizard_offset]


pygame.mixer.music.load('assets/audio/musicop.mp3')
pygame.mixer.music.set_volume(0.15)
pygame.mixer.music.play(-1, 0.0, 5000)

sword_fx = pygame.mixer.Sound('assets/audio/sword.wav')
sword_fx.set_volume(0.25)
magic_fx = pygame.mixer.Sound('assets/audio/magic.wav')
magic_fx.set_volume(1.1)
# load background image

bg_image = pygame.image.load('assets/images/background/setting2.webp').convert_alpha()

# load spritesheets

warrior_sheet = pygame.image.load('assets/images/warrior/sprites/warrior.png').convert_alpha()
wizard_sheet = pygame.image.load('assets/images/wizard/sprites/wizard.png').convert_alpha()


# Load Damage spritesheets
explosion_sheet = pygame.image.load('assets/images/damage/explosion.png').convert_alpha()
explosion_info = {'length': 16, 'size_in_px': 72}

explosion_list = []
for x in range(16):
    temp_img = explosion_sheet.subsurface(72*x, 0, 72, 72)
    explosion_list.append(pygame.transform.scale(temp_img, (100, 100)))


damage_sheet = pygame.image.load('assets/images/damage/damage.png').convert_alpha()
damage_info = {'length': 7, 'size_in_px': 140}
damage_list = []
for x in range(7):
    temp_img = damage_sheet.subsurface(140*x, 0, 140, 50)
    damage_list.append(pygame.transform.scale(temp_img, (200, 200)))


blood_sheet = pygame.image.load('assets/images/damage/blood.png').convert_alpha()
blood_info = {'length': 6, 'size_in_px': 32}
blood_list = []
for x in range(6):
    temp_img = blood_sheet.subsurface(32*x, 0, 32, 32)
    blood_list.append(pygame.transform.scale(temp_img, (150, 150)))

# Effects defined

explosion = Effect(explosion_list, 50)
explosion_x = 0
explosion_y = 0

damage = Effect(damage_list, 50)
damage_x = 0
damage_y = 0

blood = Effect(blood_list, 50)
blood_x = 0
blood_y = 0

# Shield

shield_image = pygame.image.load('assets/images/shield/shield.png').convert_alpha()
shield_info = {'rotation': 90, 'scale': 0.6}
shield_list = []
for x in range(55):
    temp_img = pygame.transform.rotate(shield_image, 90 + 5*x)
    temp_img = pygame.transform.scale_by(temp_img, 0.0074*x)
    shield_list.append(temp_img)

shield = Effect(shield_list, 50)
shield_x = 0
shield_y = 0

# load victory image

victory_image = pygame.image.load('assets/images/icons/victory.png').convert_alpha()

# define number of steps in each animation
warrior_animation_steps = [10, 8, 1, 7, 7, 3, 7]
wizard_animation_steps = [8, 8, 1, 8, 8, 3, 7]


# define font
count_font = pygame.font.Font("assets/fonts/turok.ttf", 80)
score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)
turn_font = pygame.font.Font("assets/fonts/turok.ttf", 50)


action_defend_btn = Button((255, 90, 0), red, screen_width/3 - 80, 90, 20, 490, 'defend', 30, yellow, 10, "assets/fonts/turok.ttf")
plyr1_action_heal_btn = Button((255, 90, 0), red, screen_width/3 - 20, 90, screen_width/3, 490, f'heal ({plyr1_potions} left)', 30, white, 10, "assets/fonts/turok.ttf")
plyr2_action_heal_btn = Button((255, 90, 0), blue, screen_width/3 - 20, 90, screen_width/3, 490, f'heal ({plyr2_potions} left)', 30, yellow, 10, "assets/fonts/turok.ttf")
action_attack_btn = Button((255, 90, 0), black, screen_width/3 - 80, 90, 2*screen_width/3 + 40, 490, 'attack', 30, white, 10, "assets/fonts/turok.ttf")

attack1_btn = Button((30, 90, 255), blue, screen_width/2 - 20, 90, 0, 490, 'attack 1', 20, yellow, 10, "assets/fonts/turok.ttf")
attack2_btn = Button((30, 90, 255), blue, screen_width/2 - 20, 90, screen_width/2, 490, 'attack 2', 20, yellow, 10, "assets/fonts/turok.ttf")

# define function to draw text

def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


# draw background function

def draw_bg():
    scaled_bg = pygame.transform.scale(bg_image, (screen_width, screen_height))
    screen.blit(scaled_bg, (0, 0))

# function for drawing fighter health bars
def draw_health_bar(health, x, y):
    ratio = health/100
    pygame.draw.rect(screen, white, (x - 2, y - 2, 404, 34))
    pygame.draw.rect(screen, red, (x, y, 400, 30))
    pygame.draw.rect(screen, (0, 255, 0), (x, y, 400*ratio, 30))

def double_animation(animation_1, animation_2, x_1, y_1, x_2, y_2, last_time=pygame.time.get_ticks()):
    if pygame.time.get_ticks() - last_time >= len(animation_1.animation_list)*animation_1.animation_cooldown:
        animation_2.draw(screen, x_2, y_2)
    else:
        animation_1.draw(screen, x_1, y_1)
    if animation_2.frame_index >= len(animation_2.animation_list) - 1:
        return 'ended'
    else:
        return None

def remove_duplicates(lst):
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def count_word_in_recognized(recognized, word):
    word = word.lower()
    recognized_str = ''.join(recognized).lower()
    
    def get_count(recognized_str, word):
        index = 0
        for char in recognized_str:
            if char == word[index]:
                index += 1
            if index == len(word):
                return 3  # Full word found
        if index == 2:
            return 2  # Two letters found in order
        elif index == 1:
            return 1  # One letter found in order
        else:
            return 0  # No letters found in order

    return get_count(recognized_str, word)


# Create two instances of Fighter

Fighter1 = Fighter(1, 200, 310, False, warrior_data, warrior_sheet, warrior_animation_steps, sword_fx)
Fighter2 = Fighter(2, 700, 310, True, wizard_data, wizard_sheet, wizard_animation_steps, magic_fx)

# game loop
run = True
while run:
    
    clock.tick(FPS)
    # draw background

    draw_bg()

    # show player stats

    draw_health_bar(Fighter1.health, 20, 20)
    draw_health_bar(Fighter2.health, 580, 20)
    draw_text('P1: ' + str(score[0]), score_font, red, 20, 60)
    draw_text('P2: ' + str(score[1]), score_font, red, 580, 60)
    Fighter1.draw(screen)
    Fighter2.draw(screen)


    # update count
    if intro_count <= 0:
        # move fighters
        if turn == 1:
            if plyr1_action == '':
                draw_text("Player 1's Turn. Pick a move!", turn_font, blue, 220, 90)
                action_attack_btn.draw(screen)
                action_defend_btn.draw(screen)
                plyr1_action_heal_btn.draw(screen)
                if action_attack_btn.main_body.collidepoint(pygame.mouse.get_pos()):
                    action_attack_btn.hover(screen)
                if action_defend_btn.main_body.collidepoint(pygame.mouse.get_pos()):
                    action_defend_btn.hover(screen)
                if plyr1_action_heal_btn.main_body.collidepoint(pygame.mouse.get_pos()):
                    plyr2_action_heal_btn.hover(screen)
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONUP:
                        if action_attack_btn.main_body.collidepoint(event.pos):
                            plyr1_action = 'attack'
                        if action_defend_btn.main_body.collidepoint(event.pos):
                            plyr1_action = 'defend'
                        if plyr1_action_heal_btn.main_body.collidepoint(event.pos):
                            if plyr1_potions > 0:
                                Fighter1.health += 10
                                plyr1_potions -= 1
                                turn = 2
                                plyr1_action = ''
                # if action_defend_btn.clicked:
                #     plyr1_action = 'defend'
                # if plyr1_action_heal_btn.clicked:
                #     plyr1_action = 'heal'
                # if action_attack_btn.clicked:
                    
            elif plyr1_action == 'defend':
                shield.reset()
                shield.animate = True
                shield_x = Fighter1.rect.x
                shield_y = Fighter1.rect.y
                Fighter1.move(screen_width, screen_height, Fighter2, 'defend', 1)
                turn = 2
                plyr1_action = ''
            elif plyr1_action == 'attack':
                # if pygame.time.get_ticks() - last_clicked1 > 8000 or (last_clicked2 == last_clicked1 == last_count_update):
                last_clicked1 = pygame.time.get_ticks()
                word = random.choice(words)
                start_pipeline()


                print(recognized, "recognized")
                recognized = remove_duplicates(recognized)
                print(recognized)
                # recognized_set = set(recognized)
                # convert recognized_set into list
                # recognized_list = list(recognized_set)
                # recognized = recognized_list


                


                count = count_word_in_recognized(recognized, word)
                print(recognized)
                print(count)  # Output will be 3 as 'abc' is found in order

                # count = sum(1 for char in ''.join(recognized).lower() if char in word)




                # if not count:
                #     count = 0
                # print(count)

                # print("RECOGNIZED CHARS: " , recognized)

                # attack1_btn.draw(screen)
                # attack2_btn.draw(screen)
                # if 3 > count >= 1:
                if count == 1:
                    print("thing_1_plyr_1", recognized, 'count: ' + str(count))
                # if count == 0:
                    print('len: ' + str(len(recognized)), recognized)
                    Fighter1.move(screen_width, screen_height, Fighter2, 'attack', 1)
                    blood.reset()
                    blood.animate = True
                    blood_x = Fighter2.rect.x
                    blood_y = Fighter2.rect.y

                    turn = 2
                    plyr1_action = ''
                    recognized = []
                if count == 2:
                    print("thing", recognized, count, sum(1 for char in ''.join(recognized).lower() if char in word))
                # if count == 0:
                    print('len: ' + str(len(recognized)), recognized)
                    Fighter1.move(screen_width, screen_height, Fighter2, 'attack', 2)
                    double_animate = 1
                    blood.reset()
                    damage.reset()
                    blood_x = Fighter2.rect.x
                    blood_y = Fighter2.rect.y
                    damage_x = Fighter2.rect.x
                    damage_y = Fighter2.rect.y
                    last_time = pygame.time.get_ticks()
                    
                    turn = 2
                    plyr1_action = ''
                    recognized = []
                # if ''.join(recognized).lower() == word:
                if count == 3:
                    print("thing", recognized, count, sum(1 for char in ''.join(recognized).lower() if char in word))
                    Fighter1.move(screen_width, screen_height, Fighter2, 'attack', 3)
                    double_animate = 2
                    blood.reset()
                    explosion.reset()
                    blood_x = Fighter2.rect.x
                    blood_y = Fighter2.rect.y
                    explosion_x = Fighter2.rect.x
                    explosion_y = Fighter2.rect.y
                    last_time = pygame.time.get_ticks()
                    
                    turn = 2
                    plyr1_action = ''
                    recognized = []
                else:
                    turn = 2
                    plyr1_action = ''
                    recognized = []
                    
        elif turn == 2:
            if plyr2_action == '':
                draw_text("Player 2's Turn. Pick a move!", turn_font, blue, 220, 90)
                action_attack_btn.draw(screen)
                action_defend_btn.draw(screen)
                plyr2_action_heal_btn.draw(screen)
                if action_attack_btn.main_body.collidepoint(pygame.mouse.get_pos()):
                    action_attack_btn.hover(screen)
                if action_defend_btn.main_body.collidepoint(pygame.mouse.get_pos()):
                    action_defend_btn.hover(screen)
                if plyr2_action_heal_btn.main_body.collidepoint(pygame.mouse.get_pos()):
                    plyr2_action_heal_btn.hover(screen)
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONUP:
                        if action_attack_btn.main_body.collidepoint(event.pos):
                            plyr2_action = 'attack'
                        if action_defend_btn.main_body.collidepoint(event.pos):
                            plyr2_action = 'defend'
                        if plyr2_action_heal_btn.main_body.collidepoint(event.pos):
                            if plyr2_potions > 0:
                                Fighter2.health += 10
                                plyr2_potions -= 1
                                turn = 1
                                plyr2_action = ''
                                plyr2_action_heal_btn = Button((255, 90, 0), red, screen_width/3 - 20, 90, screen_width/3, 490, f'heal ({plyr2_potions} left)', 20, yellow, 10, "assets/fonts/turok.ttf")

                # if action_defend_btn.clicked:
                    
                # if plyr2_action_heal_btn.clicked:
                    
                # if action_attack_btn.clicked:
                    
            elif plyr2_action == 'defend':
                shield.reset()
                shield.animate = True
                shield_x = Fighter2.rect.x
                shield_y = Fighter2.rect.y
                Fighter2.move(screen_width, screen_height, Fighter1, 'defend', 1)
                turn = 1
                plyr2_action = ''
            elif plyr2_action == 'attack':
                # if pygame.time.get_ticks() - last_clicked2 > 8000 or (last_clicked2 == last_clicked1 == last_count_update):
                last_clicked2 = pygame.time.get_ticks()
                word = random.choice(words)
                start_pipeline()

                
                recognized = remove_duplicates(recognized)
                print(recognized, " : recognized")
                # recognized_set = set(recognized)
                # convert recognized_set into list
                # recognized_list = list(recognized_set)
                # recognized = recognized_list


                count = count_word_in_recognized(recognized, word)
                
                  # Output will be 3 as 'abc' is found in order

                # count = sum(1 for char in ''.join(recognized).lower() if char in word)
                
                # attack1_btn.draw(screen)
                # attack2_btn.draw(screen)
                # if 3 > count >= 1:
                    
                if count == 1:
                    print("thing_1_plyr_2", recognized, 'count: ' + str(count))
                    Fighter2.move(screen_width, screen_height, Fighter1, 'attack', 1)
                    # print('len: ' + str(len(recognized)).lower(), recognized)
                    blood.reset()
                    blood.animate = True
                    blood_x = Fighter1.rect.x
                    blood_y = Fighter1.rect.y

                    turn = 1
                    plyr2_action = ''
                    recognized = []
                if count == 2:
                    print("thing", recognized, 'count: ' + str(count), 'sum:' + str(sum(1 for char in ''.join(recognized).lower() if char in word)))
                    Fighter2.move(screen_width, screen_height, Fighter1, 'attack', 2)
                    # print('len: ' + str(len(recognized)).lower(), recognized)
                    double_animate = 1
                    blood.reset()
                    damage.reset()
                    blood_x = Fighter1.rect.x
                    blood_y = Fighter1.rect.y
                    damage_x = Fighter1.rect.x
                    damage_y = Fighter1.rect.y
                    last_time = pygame.time.get_ticks()

                    turn = 1
                    plyr2_action = ''
                    recognized = []
                # if ''.join(recognized).lower() == word:
                if count == 3:
                    print("thing", recognized, count, sum(1 for char in ''.join(recognized).lower() if char in word))
                    Fighter2.move(screen_width, screen_height, Fighter1, 'attack', 3)
                    double_animate = 2
                    blood.reset()
                    explosion.reset()
                    blood_x = Fighter1.rect.x
                    blood_y = Fighter1.rect.y
                    explosion_x = Fighter1.rect.x
                    explosion_y = Fighter1.rect.y
                    last_time = pygame.time.get_ticks()

                    turn = 1
                    plyr2_action = ''
                    recognized = []
                else:
                    turn = 1
                    plyr1_action = ''
                    recognized = []
                # if attack1_btn.clicked:
                #     print('trueee')
                #     Fighter2.move(screen_width, screen_height, Fighter1, 'attack', 1)
                #     turn = 1
                # if attack2_btn.clicked:
                #     Fighter2.move(screen_width, screen_height, Fighter1, 'attack', 2)
                #     turn = 1
                


        Fighter1.move(screen_width, screen_height, Fighter2, 'None', 1)
        Fighter2.move(screen_width, screen_height, Fighter1, 'None', 2)
    else:
        # display count timer
        draw_text(str(intro_count), count_font, red, screen_width/2, screen_height/3)
        # update count timer
        if (pygame.time.get_ticks() - last_count_update) >= 1000:
            intro_count -= 1
            last_count_update = pygame.time.get_ticks()

    # update fighters
    Fighter1.update()
    Fighter2.update()

    # draw fighters

    # Fighter1.draw(screen)
    # Fighter2.draw(screen)

    if explosion.animate:
        explosion.draw(screen, explosion_x, explosion_y)
    if damage.animate:
        damage.draw(screen, damage_x, damage_y)
    if blood.animate:
        blood.draw(screen, blood_x, blood_y)
    if double_animate == 1:
        doub_anim_proc = double_animation(damage, blood, damage_x, damage_y, blood_x, blood_y, last_time)
        if doub_anim_proc == 'ended':
            double_animate = 0
    if double_animate == 2:
        doub_anim_proc = double_animation(explosion, blood, explosion_x, explosion_y, blood_x, blood_y, last_time)
        if doub_anim_proc == 'ended':
            double_animate = 0
    if shield.animate:
        shield.draw(screen, shield_x, shield_y)



    # check for player defeat
    if round_over == False:
        if Fighter1.alive == False:
            score[1] += 1
            round_over = True
            round_over_time = pygame.time.get_ticks()
        elif Fighter2.alive == False:
            score[0] += 1
            round_over = True
            round_over_time = pygame.time.get_ticks()
    else:
        screen.blit(victory_image, (360, 150))
        if pygame.time.get_ticks() - round_over_time > round_over_cooldown:
            round_over = False
            intro_count = 5
            Fighter1 = Fighter(1 ,200, 310, False, warrior_data, warrior_sheet, warrior_animation_steps, sword_fx)
            Fighter2 = Fighter(2, 700, 310, True, wizard_data, wizard_sheet, wizard_animation_steps, magic_fx)

    # event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    #  update display
    pygame.display.update()

# exit pygame

pygame.quit()