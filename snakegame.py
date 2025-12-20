import pygame #library for games dispaly input and use keys
import sys # for fonts and entry or exit in sys
import random # generates random alphabets or numbers
import json # json is like local databse 
import os # is used to do taks in operating system like we are using it to check assests path

pygame.init() #initializing pygame
pygame.mixer.init() #initializing that we are going to use sound,music,audio etc

# Window setup
info = pygame.display.Info()
width, height = info.current_w, info.current_h
screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
pygame.display.set_caption(" Snake Game ")

# Colors
black = (0, 0, 0)
dark_silver = (80, 80, 80)  # Used for connecting lines and tail
red = (255, 0, 0)
yellow = (255, 255, 0)
white = (255, 255, 255)

# Loading background image
background = pygame.image.load("C:/Users/Hp/h.c/pythonproject/background.png")
background = pygame.transform.scale(background, (width, height))

#sound assests
red_food_sound = pygame.mixer.Sound("C:/Users/Hp/h.c/pythonproject/redfoodsound.mp3")
yellow_food_sound = pygame.mixer.Sound("C:/Users/Hp/h.c/pythonproject/yellowfoodsound.wav")
game_over_sound = pygame.mixer.Sound("C:/Users/Hp/h.c/pythonproject/gameover.wav")
game_pause_sound = pygame.mixer.Sound("C:/Users/Hp/h.c/pythonproject/gamepausesound.wav")
pygame.mixer.music.load("C:/Users/Hp/h.c/pythonproject/backgroundsound.mp3")

# Game settings
clock = pygame.time.Clock()
snake_block = 20
snake_speed = 10
food_timer_limit = 10  # 20 seconds to eat food

start_time = pygame.time.get_ticks()
pause_start_time = 0
total_paused_duration = 0
paused = False


# Fonts 
font = pygame.font.SysFont('Arial', 25)
game_over_font = pygame.font.SysFont('Arial', 50)

def load_high_score():
    if os.path.exists("highscore.json"):
        with open("highscore.json", "r") as file:
            data = json.load(file)
            return data.get("high_score", 0)
    return 0

def save_high_score(score):
    data = {"high_score": score}
    with open("highscore.json", "w") as file:
        json.dump(data, file)

def random_food():
    x = random.randint(0, (width - snake_block) // snake_block) * snake_block
    y = random.randint(0, (height - snake_block) // snake_block) * snake_block
    return x, y

def draw_snake(snake_body, direction):
    # Define additional colors for gradient and shading
    light_silver = (180, 180, 180)  # Lighter silver for head
    outline_color = (120, 120, 120)  # Mid-tone gray for 3D effect

    for i, segment in enumerate(snake_body):
        x, y = segment[0], segment[1]
        rect = pygame.Rect(x, y, snake_block, snake_block)

        # Gradient: interpolate from light_silver (head, last segment) to dark_silver (tail, first segment)
        t = (len(snake_body) - 1 - i) / max(1, len(snake_body) - 1)  # Reverse gradient
        r = int(light_silver[0] + (dark_silver[0] - light_silver[0]) * t)
        g = int(light_silver[1] + (dark_silver[1] - light_silver[1]) * t)
        b = int(light_silver[2] + (dark_silver[2] - light_silver[2]) * t)
        segment_color = (r, g, b)

        # Determine segment type
        is_head = (i == len(snake_body) - 1)  # Head is last element
        is_tail = (i == 0)  # Tail is first element

        # Draw outline for 3D effect
        outline_rect = rect.inflate(2, 2)  # Slightly larger
        pygame.draw.rect(screen, outline_color, outline_rect, border_radius=6)

        # Draw main segment
        if is_head:
            pygame.draw.rect(screen, segment_color, rect, border_radius=8)
            # Add eyes based on direction
            eye_radius = snake_block // 6
            eye_offset = snake_block // 4
            if direction == "RIGHT":
                eye1 = (x + snake_block - eye_offset, y + eye_offset)
                eye2 = (x + snake_block - eye_offset, y + snake_block - eye_offset)
            elif direction == "LEFT":
                eye1 = (x + eye_offset, y + eye_offset)
                eye2 = (x + eye_offset, y + snake_block - eye_offset)
            elif direction == "UP":
                eye1 = (x + eye_offset, y + eye_offset)
                eye2 = (x + snake_block - eye_offset, y + eye_offset)
            elif direction == "DOWN":
                eye1 = (x + eye_offset, y + snake_block - eye_offset)
                eye2 = (x + snake_block - eye_offset, y + snake_block - eye_offset)
            pygame.draw.circle(screen, white, eye1, eye_radius)
            pygame.draw.circle(screen, white, eye2, eye_radius)
            pygame.draw.circle(screen, black, eye1, eye_radius // 2)  # Pupils
            pygame.draw.circle(screen, black, eye2, eye_radius // 2)
        elif is_tail and len(snake_body) > 1:
            # Tapered tail based on direction to next segment
            next_segment = snake_body[i + 1]
            dx = next_segment[0] - segment[0]
            dy = next_segment[1] - segment[1]
            if dx > 0:  # Tail pointing left
                points = [
                    (x + snake_block, y),
                    (x + snake_block, y + snake_block),
                    (x, y + snake_block // 2)
                ]
            elif dx < 0:  # Tail pointing right
                points = [
                    (x, y),
                    (x, y + snake_block),
                    (x + snake_block, y + snake_block // 2)
                ]
            elif dy > 0:  # Tail pointing up
                points = [
                    (x, y + snake_block),
                    (x + snake_block, y + snake_block),
                    (x + snake_block // 2, y)
                ]
            elif dy < 0:  # Tail pointing down
                points = [
                    (x, y),
                    (x + snake_block, y),
                    (x + snake_block // 2, y + snake_block)
                ]
            pygame.draw.polygon(screen, segment_color, points)
        else:
            # Body segment
            pygame.draw.rect(screen, segment_color, rect, border_radius=6)

        # Connect segments with lines, but skip if wrapping occurs
        if i < len(snake_body) - 1:  # Connect to next segment (toward head)
            next_segment = snake_body[i + 1]
            center1 = (x + snake_block // 2, y + snake_block // 2)
            center2 = (next_segment[0] + snake_block // 2, next_segment[1] + snake_block // 2)
            # Check for wrapping by comparing distances
            dx = abs(next_segment[0] - x)
            dy = abs(next_segment[1] - y)
            # If the distance is greater than half the screen size, it's a wraparound
            if dx <= width // 2 and dy <= height // 2:
                pygame.draw.line(screen, dark_silver, center1, center2, snake_block // 4)

def message(msg, color, y_offset=0):
    mesg = game_over_font.render(msg, True, color)
    rect = mesg.get_rect(center=(width // 2, height // 3 + y_offset))
    screen.blit(mesg, rect)

def show_score(score, high_score, time_left):
    score_text = font.render("Score : " + str(score), True, white)
    high_score_text = font.render("High Score : " + str(high_score), True, white)
    timer_text = font.render(f"Timer: {time_left:.1f}s", True, white)
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (10, 40))
    screen.blit(timer_text, (10, 70))  # Display timer below high score

def game_over_screen(score, high_score, last_frame):
    pygame.mixer.music.stop()  # Stop music on game over
    screen.blit(last_frame, (0, 0))
    message("Game Over", red)
    score_text = font.render("Your Score: " + str(score), True, white)
    high_score_text = font.render("High Score: " + str(high_score), True, white)
    screen.blit(score_text, (width // 2 - score_text.get_width() // 2, height // 2))
    screen.blit(high_score_text, (width // 2 - high_score_text.get_width() // 2, height // 2 + 40))

    instr_font = pygame.font.SysFont("arial", 20)
    instr1 = instr_font.render("Press R to Play Again", True, white)
    instr2 = instr_font.render("Press ESC to Quit", True, white)
    screen.blit(instr1, (width // 2 - instr1.get_width() // 2, height // 2 + 80))
    screen.blit(instr2, (width // 2 - instr2.get_width() // 2, height // 2 + 110))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
 #                   
def menu_screen():
    background = pygame.image.load("C:/Users/Hp/h.c/pythonproject/background.png")
    background = pygame.transform.scale(background, (width, height))

    while True:
        screen.blit(background, (0, 0))

        # Title
        title_font = pygame.font.SysFont("Arial", 36, bold=True)
        start_text = title_font.render("Press ENTER to Start the Game", True, white)
        screen.blit(start_text, (width // 2 - start_text.get_width() // 2, height // 2 - 40))

        # Author name with shadow and glow effect
        credit_font = pygame.font.SysFont("Arial", 26, bold=True)
        author_color = (255, 255, 0)  # Yellow
        author_text = "Created by Muhammad Haris"

        # Calculate position
        x = width // 2 - credit_font.size(author_text)[0] // 2
        y = height // 2 + 30

        # Shadow
        shadow = credit_font.render(author_text, True, (0, 0, 0))
        screen.blit(shadow, (x + 2, y + 2))

        # Main Text
        credit = credit_font.render(author_text, True, author_color)
        screen.blit(credit, (x, y))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return

#
def game_loop():
    snake_x = (100 // snake_block) * snake_block
    snake_y = (50 // snake_block) * snake_block
    snake_dx = snake_block
    snake_dy = 0
    snake_body = [[snake_x, snake_y]]
    food_x, food_y = random_food()
    score = 0
    direction = "RIGHT"
    paused = False
    pause_start_time = 0
    total_paused_time = 0
    food_eaten_count = 0
    high_score = load_high_score()
    music_muted = False
    last_food_time = pygame.time.get_ticks()
    size_decreased = False
    floating_score = None
    score_timer = 0
    yellow_food = None
    Black_food = None
    
    if not music_muted:
        pygame.mixer.music.play(-1)

    while True:
        # Handle all events no matter what
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                elif event.key == pygame.K_p:
                    if paused:
                        paused = False
                        total_paused_time += pygame.time.get_ticks() - pause_start_time
                        pygame.mixer.music.unpause()
                    else:
                        paused = True
                        pause_start_time = pygame.time.get_ticks()
                        game_pause_sound.play()
                        pygame.mixer.music.pause()

                elif not paused:  # Only process controls if not paused
                    if event.key == pygame.K_LEFT and direction != "RIGHT":
                        snake_dx = -snake_block
                        snake_dy = 0
                        direction = "LEFT"
                    elif event.key == pygame.K_RIGHT and direction != "LEFT":
                        snake_dx = snake_block
                        snake_dy = 0
                        direction = "RIGHT"
                    elif event.key == pygame.K_UP and direction != "DOWN":
                        snake_dx = 0
                        snake_dy = -snake_block
                        direction = "UP"
                    elif event.key == pygame.K_DOWN and direction != "UP":
                        snake_dx = 0
                        snake_dy = snake_block
                        direction = "DOWN"
                    elif event.key == pygame.K_m:
                        music_muted = not music_muted
                        if music_muted:
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()

        # Only update gameplay if not paused
        if not paused:
            # Calculate adjusted timer
            current_time = pygame.time.get_ticks()
            time_since_last_food = (current_time - last_food_time - total_paused_time) / 1000
            time_left = max(0, food_timer_limit - time_since_last_food)

            # Update snake position
            snake_x = (snake_x + snake_dx) % width
            snake_y = (snake_y + snake_dy) % height
            snake_body.append([snake_x, snake_y])

            # Check for collision with self
            if [snake_x, snake_y] in snake_body[:-1]:
                game_over_sound.play()
                pygame.time.delay(500)
                last_frame = screen.copy()
                if score > high_score:
                    save_high_score(score)
                return score, high_score, last_frame

            # Check for food collision
            ate_food = False
            if snake_x == food_x and snake_y == food_y:
                red_food_sound.play()
                score += 5
                food_eaten_count += 1
                floating_score = "+5"
                score_timer = pygame.time.get_ticks()
                food_x, food_y = random_food()
                if food_eaten_count >= 5:
                    yellow_food = random_food()
                    Black_food = random_food()
                ate_food = True
            elif yellow_food and snake_x == yellow_food[0] and snake_y == yellow_food[1]:
                yellow_food_sound.play()
                score += 10
                floating_score = "+10"
                score_timer = pygame.time.get_ticks()
                yellow_food = None
                food_eaten_count = 0
                ate_food = True
            elif Black_food and snake_x == Black_food[0] and snake_y == Black_food[1]:
                game_over_sound.play()
                pygame.time.delay(500)
                last_frame = screen.copy()
                if score > high_score:
                    save_high_score(score)
                return score, high_score, last_frame
            
            # Reset timer if food was eaten
            if ate_food:
                last_food_time = pygame.time.get_ticks()
                size_decreased = False
            else:
                # If no food eaten, decrease size after 20 seconds
                if time_since_last_food >= food_timer_limit and not size_decreased:
                    if len(snake_body) > 1:  # Ensure there's something to remove
                        snake_body.pop(0)
                    size_decreased = True  # Prevent multiple decreases until timer resets
                    last_food_time = pygame.time.get_ticks()
                    
                # Normal size decrease (not eating food)
                snake_body.pop(0)

            # Check if snake size is 0 (game over)
            if len(snake_body) == 0:
                game_over_sound.play()
                pygame.time.delay(500)
                last_frame = screen.copy()
                if score > high_score:
                    save_high_score(score)
                return score, high_score, last_frame

            # Reset size_decreased flag when timer resets
            if time_since_last_food < food_timer_limit:
                size_decreased = False

            # Update high score
            if score > high_score:
                high_score = score
                save_high_score(high_score)

            # Draw game elements
            screen.blit(background, (0, 0))
            pygame.draw.circle(screen, red, (food_x + snake_block // 2, food_y + snake_block // 2), snake_block // 2)
            if yellow_food:
                pygame.draw.circle(screen, yellow, (yellow_food[0] + snake_block // 2, yellow_food[1] + snake_block // 2), snake_block // 2)
            draw_snake(snake_body, direction)
            show_score(score, high_score, time_left)
            if Black_food:
                pygame.draw.circle(screen,black, (Black_food[0] + snake_block // 2, Black_food[1] + snake_block // 2), snake_block // 2)
            draw_snake(snake_body, direction)
            show_score(score, high_score, time_left)
                

            if floating_score and pygame.time.get_ticks() - score_timer < 800:
                float_font = pygame.font.SysFont("Arial", 30)
                score_text = float_font.render(floating_score, True, white)
                screen.blit(score_text, (snake_x, snake_y - 30))
            else:
                floating_score = None

            pygame.display.flip()
            clock.tick(snake_speed)

        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_p:
                        paused = False
                        game_pause_sound.play()
                        if not music_muted:
                            pygame.mixer.music.unpause()  # Resume music if not muted
                    elif event.key == pygame.K_m:
                        music_muted = not music_muted
                        if not music_muted and not paused:
                            pygame.mixer.music.unpause()
                        elif music_muted:
                            pygame.mixer.music.pause()

            screen.blit(background, (0, 0))
            pygame.draw.circle(screen, red, (food_x + snake_block // 2, food_y + snake_block // 2), snake_block // 2)
            if yellow_food:
                pygame.draw.circle(screen, yellow, (yellow_food[0] + snake_block // 2, yellow_food[1] + snake_block // 2), snake_block // 2)
            draw_snake(snake_body, direction)
            show_score(score, high_score, time_left)
            
            if Black_food:
                pygame.draw.circle(screen,black, (Black_food[0] + snake_block // 2, Black_food[1] + snake_block // 2), snake_block // 2)
            draw_snake(snake_body, direction)
            show_score(score, high_score, time_left)

            pause_font = pygame.font.SysFont("Arial", 50)
            pause_text = pause_font.render("Game Paused", True, yellow)
            pause_rect = pause_text.get_rect(center=(width // 2, height // 2))
            screen.blit(pause_text, pause_rect)

            pygame.display.flip()
            clock.tick(10)
    
def main():
    menu_screen()
    while True:
        score, high_score, last_frame = game_loop()
        game_over_screen(score, high_score, last_frame)

if __name__ == "__main__":
    main()