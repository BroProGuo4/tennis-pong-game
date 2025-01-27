import pygame
import sys
import random
import time
import argparse

# Define the argument parser
parser = argparse.ArgumentParser(description="Tennis Pong by Brooklyn Guo")

# select starting game speed
# parser.add_argument("-slow", action="store_true", help="Enabling slow starting speed")
# parser.add_argument("-medium", action="store_true", help="Enabling medium starting speed")
# parser.add_argument("-fast", action="store_true", help="Enabling fast starting speed")
parser.add_argument('-ballspeed', type=float, default=7.0, help="Set ball speed (default is 7.0)")

# select game pace multiplier (idea: play around with random speed ballspeed at each hit, or perhaps an AI that hits the ball at random ball speeds)
parser.add_argument('-increment', type=float, default=0.5, help="Set ball speed (default is 0.5)")

# random speed modifier
parser.add_argument("-randomness", type=str, default="off", help="Enabling random speed modifier on each hit")

# set paddle speeds for top and bottom players:
parser.add_argument('-speed1', type=int, default=7, help="Set P1 paddle speed (default is 7)")
parser.add_argument('-speed2', type=int, default=7, help="Set P2 paddle speed (default is 7)")

parser.add_argument("-handicap1", type=str, default="default", help="Enabling handicap for bottom player (p1)")
parser.add_argument("-handicap2", type=str, default="default", help="Enabling handicap for top player (p2)")

# select AI model for players 1 and 2
parser.add_argument("-p1", type=str, default="user", help="Enabling AI vs. AI mode")
parser.add_argument("-p2", type=str, default="user", help="Enabling AI vs. AI mode")

# select whether ball landing zone is flashed on paddle collision with ball
parser.add_argument("-flash", action="store_true", help="Enabling landing zone flash assist")

# select your AI you're playing against (default AI aims for contact at center of paddle)
# parser.add_argument("-phantom", action="store_true", help="Enabling smarter AI 'phantom'") # phantom hits down the line (this AI is not very good, as the logic causes AI to not have time to get to position and miss the ball a lot)
# parser.add_argument("-sentinel", action="store_true", help="Enabling smarter AI 'sentinel'") # sentinel hits inside out (decent difficulty, makes the player move around)
# parser.add_argument("-titan", action="store_true", help="Enabling smarter AI 'titan'") # titan hits to the side of where the player is not (hard)
# parser.add_argument("-rival", action="store_true", help="Enabling smarter AI 'rival'") # rival hits perfectly in the corner of where the player is not (very hard)

# select court colors from famour tennis tournaments
parser.add_argument("-court", type=str, default="default", help="Choosing Tournament Court Colors")

args = parser.parse_args()


# Initialize Pygame
pygame.init()

# Flash timer variables
flash_duration = 1000  # Duration for flashing (in milliseconds)
last_flash_time = 0  # Time when the flash was last triggered
is_flashing = False  # Whether the ball destination is currently being flashed
ball_destination_x, ball_destination_y = None, None  # Store the destination coordinates


# SPEED_MODIFIER = 5.0
RALLY_LENGTH = 0

# Screen dimensions
WIDTH, HEIGHT = 400, 600 # 400, 600

HIT_BOX_PADDING = 10

COURT_LEFT, COURT_RIGHT = 40, WIDTH - 40
COURT_WIDTH = COURT_RIGHT - COURT_LEFT
# COURT_LENGTH = # generalize this later
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vertical Pong with AI")

# if args.slow:
#     SPEED_MODIFIER = 3.0
# elif args.medium: 
#     SPEED_MODIFIER = 7.0
# elif args.fast:
#     SPEED_MODIFIER = 10.0
# else:
#     SPEED_MODIFIER = 5.0

SPEED_MODIFIER = args.ballspeed
INCREMENT = args.increment

if args.handicap1 == "full":
    P1_RIGHT_BOUND = COURT_RIGHT
    P1_LEFT_BOUND = COURT_LEFT
elif args.handicap1 == "half":
    P1_RIGHT_BOUND = COURT_RIGHT + 20
    P1_LEFT_BOUND = COURT_LEFT - 20
# elif int(args.handicap1) > 0:
#     P1_RIGHT_BOUND = COURT_RIGHT + int(args.handicap1)
#     P1_LEFT_BOUND = COURT_LEFT - int(args.handicap1)
else:
    P1_RIGHT_BOUND = WIDTH
    P1_LEFT_BOUND = 0

if args.handicap2 == "full":
    P2_RIGHT_BOUND = COURT_RIGHT
    P2_LEFT_BOUND = COURT_LEFT
elif args.handicap2 == "half":
    P2_RIGHT_BOUND = COURT_RIGHT + 20
    P2_LEFT_BOUND = COURT_LEFT - 20
# elif int(args.handicap2) > 0:
#     P2_RIGHT_BOUND = COURT_RIGHT + int(args.handicap2)
#     P2_LEFT_BOUND = COURT_LEFT - int(args.handicap2)
else:
    P2_RIGHT_BOUND = WIDTH
    P2_LEFT_BOUND = 0

INITIAL_SPEED = SPEED_MODIFIER

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

SINGLES_COURT = False
SW19 = False

if args.court == "ao":
    FLOOR_COLOR, COURT_COLOR = (30, 143, 213), (56, 124, 184) # Australian Open
elif args.court == "uso":
    FLOOR_COLOR, COURT_COLOR = (110, 161, 85), (71, 105, 151) # US Open
elif args.court == "sw":
    FLOOR_COLOR, COURT_COLOR = (43, 130, 9), (43, 130, 9) # Wimbledon
    SW19 = True
elif args.court == "rg":
    FLOOR_COLOR, COURT_COLOR = (232, 99, 46), (232, 99, 46) # Roland Garros
elif args.court == "davis":
    FLOOR_COLOR, COURT_COLOR = (107, 105, 106), (61, 121, 105) # Davis Cup
elif args.court == "nitto":
    FLOOR_COLOR, COURT_COLOR = (89, 130, 178), (64, 87, 114) # Nitto ATP Finals
elif args.court == "nextgen":
    FLOOR_COLOR, COURT_COLOR = (104, 170, 255), (52, 84, 124) # Next Gen ATP Finals
    SINGLES_COURT = True
elif args.court == "laver":
    FLOOR_COLOR, COURT_COLOR = (64, 64, 64), (64, 64, 64) # Laver Cup
elif args.court == "cancun":
    FLOOR_COLOR, COURT_COLOR = (51, 56, 61), (93, 41, 71) # cancun
elif args.court == "riyadh":
    FLOOR_COLOR, COURT_COLOR = (100, 99, 106), (141, 96, 211) # riyadh
elif args.court == "shanghai":
    FLOOR_COLOR, COURT_COLOR = (162, 197, 125), (74, 71, 125) # shanghai
else:
    FLOOR_COLOR, COURT_COLOR = (237, 109, 167), (64, 64, 64) # Custom

BALL_COLOR = (205, 235, 52)

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Paddle properties
PADDLE_WIDTH, PADDLE_HEIGHT = 80, 10
p1_x = (WIDTH - PADDLE_WIDTH) // 2
p1_y = HEIGHT - 80
p2_x = (WIDTH - PADDLE_WIDTH) // 2
p2_y = 80
p1_speed = args.speed1
p2_speed = args.speed2
p1_prev_x, p2_prev_x = 0, 0

# Ball properties
BALL_SIZE = 15
ball_x = WIDTH // 2
ball_y = HEIGHT // 2

if args.p1 != "user" and args.p2 != "user":
    ball_speed_x = random.choice([-4, 4])
    
else:
    ball_speed_x = 0
ball_speed_y = random.choice([-4, 4])

# Score
player_score = 0
ai_score = 0
font = pygame.font.Font(None, 36)

def reset_ball():
    """Resets the ball to the center with a random direction."""
    global ball_x, ball_y, ball_speed_x, ball_speed_y, SPEED_MODIFIER, RALLY_LENGTH
    ball_x = WIDTH // 2
    ball_y = HEIGHT // 2

    if args.p1 != "user" and args.p2 != "user":
        ball_speed_x = random.choice([-4, 4])
        
    else:
        ball_speed_x = 0
    ball_speed_y = random.choice([-4, 4])
    

    SPEED_MODIFIER = INITIAL_SPEED
    RALLY_LENGTH = 0

def draw_paddle(x, y):
    pygame.draw.rect(screen, BLACK, (x, y, PADDLE_WIDTH, PADDLE_HEIGHT))

def draw_ball():
    pygame.draw.ellipse(screen, BALL_COLOR, (ball_x, ball_y, BALL_SIZE, BALL_SIZE))

def draw_text():
    p1_score_text = font.render(f"P1: {player_score}", True, WHITE)
    screen.blit(p1_score_text, (10, 10))
    p2_score_text = font.render(f"P2: {ai_score}", True, WHITE)
    screen.blit(p2_score_text, (10, 35))

    ball_speed_modifier_text = font.render(f"Ball Speed: {SPEED_MODIFIER}", True, WHITE)
    screen.blit(ball_speed_modifier_text, (WIDTH-215, 10))

    # Draw ball position in top-left corner
    # ball_position_text = font.render(f"Ball: X={ball_x:.2f}, Y={ball_y:.2f}", True, WHITE)
    # screen.blit(ball_position_text, (20, HEIGHT - 40))

    rally_length_text = font.render(f"Rally Length: {RALLY_LENGTH}", True, WHITE)
    screen.blit(rally_length_text, (WIDTH - 200, HEIGHT - 30))

def draw_court(floor_color, court_color, singles_court: bool, wimbledon: bool):
    if wimbledon:
        green1, green2 = (162, 193, 41), (131, 177, 23)

        draw_x = 0
        while draw_x < WIDTH:
            pygame.draw.rect(screen, green1, (draw_x, 0, 40, HEIGHT))
            pygame.draw.rect(screen, green2, (draw_x + 40, 0, 40, HEIGHT))
            draw_x += 80

    if not wimbledon:
        pygame.draw.rect(screen, court_color, (COURT_LEFT, 110, COURT_WIDTH, 382))

    # singles vertical rectangle colorings
    if singles_court and not wimbledon:
        pygame.draw.rect(screen, floor_color, (COURT_LEFT, 110, COURT_LEFT + 2, 382))
        pygame.draw.rect(screen, floor_color, (COURT_WIDTH - 2, 110, COURT_WIDTH, 382))

    # vertical boundaries
    if not singles_court:
        pygame.draw.line(screen, WHITE, (COURT_LEFT, 110), (COURT_LEFT, HEIGHT - 110), 5)
        pygame.draw.line(screen, WHITE, (COURT_RIGHT, 110), (COURT_RIGHT, HEIGHT - 110), 5)
    pygame.draw.line(screen, WHITE, (COURT_LEFT + 40, 110), (COURT_LEFT + 40, HEIGHT - 110), 5)
    pygame.draw.line(screen, WHITE, (COURT_RIGHT - 40, 110), (COURT_RIGHT - 40, HEIGHT - 110), 5)

    # vertical service half line
    pygame.draw.line(screen, WHITE, (WIDTH // 2, 195), (WIDTH // 2, HEIGHT - 195), 5)

    # serve ticks
    pygame.draw.line(screen, WHITE, (WIDTH // 2, 110), (WIDTH // 2, 116), 5)
    pygame.draw.line(screen, WHITE, (WIDTH // 2, HEIGHT - 110), (WIDTH // 2, HEIGHT - 116), 5)
    

    # horizontal boundaries
    if not singles_court:
        pygame.draw.line(screen, WHITE, (COURT_LEFT-2, 110), (COURT_RIGHT+2, 110), 5)
        pygame.draw.line(screen, WHITE, (COURT_LEFT-2, HEIGHT - 110), (COURT_RIGHT+2, HEIGHT - 110), 5)
        pygame.draw.line(screen, WHITE, (COURT_LEFT, HEIGHT // 2), (COURT_RIGHT, HEIGHT // 2), 5)
    else:
        pygame.draw.line(screen, WHITE, (COURT_LEFT-2 + 40, 110), (COURT_RIGHT+2 - 40, 110), 5)
        pygame.draw.line(screen, WHITE, (COURT_LEFT-2 + 40, HEIGHT - 110), (COURT_RIGHT+2 - 40, HEIGHT - 110), 5)
        pygame.draw.line(screen, WHITE, (COURT_LEFT + 40, HEIGHT // 2), (COURT_RIGHT - 40, HEIGHT // 2), 5)

    pygame.draw.line(screen, WHITE, (COURT_LEFT + 40, 195), (COURT_RIGHT - 40, 195), 5)
    pygame.draw.line(screen, WHITE, (COURT_LEFT + 40, HEIGHT - 195), (COURT_RIGHT - 40, HEIGHT - 195), 5)

paused = False

# basic AI that aims to hit ball in the middle of its paddle 
# (returns ball to center of court)
def basic(x, ball_x, speed, left_bound, right_bound):
    prev_x = x
    if x + PADDLE_WIDTH // 2 < ball_x and x < right_bound - PADDLE_WIDTH:
        x += speed
    if x + PADDLE_WIDTH // 2 > ball_x and x > left_bound:
        x -= speed
    return prev_x, x

# this AI aims to hit cross court and inside out shots only
def phantom(x, ball_x, speed, left_bound, right_bound):
    prev_x = x
    if x < ball_x and x < right_bound - PADDLE_WIDTH:
        x += speed
    if x + PADDLE_WIDTH > ball_x and x > left_bound:
        x -= speed
    return prev_x, x

# this AI aims to hit down the line shots only
def sentinel(x, ball_x, speed, left_bound, right_bound):
    prev_x = x
    if x + PADDLE_WIDTH < ball_x and x < right_bound - PADDLE_WIDTH:
        x += speed
    if x > ball_x and x > left_bound:
        x -= speed
    return prev_x, x

# this AI aims to hit to the side of the court that the opponent 
# is farther from, with a random multiplier to determining how wide the shot is
def titan(x, opp_x, ball_x, speed, left_bound, right_bound):
    prev_x = x

    opp_center_x = opp_x + PADDLE_WIDTH // 2  # opposition's paddle center position
    randomness = random.uniform(0.10, 0.80)
    shift = (PADDLE_WIDTH / 2) * randomness
    
    # Determine where the AI should hit the ball based on the opposition's position
    if opp_center_x < WIDTH // 2:  # opposition is on the left side
        # AI aims to hit the ball on the right side of its paddle
        proposed = ball_x + (BALL_SIZE // 2) - PADDLE_WIDTH + shift
        if proposed >= left_bound and proposed + PADDLE_WIDTH <= right_bound:
            if x < proposed:
                x += speed  # Move right
                if x > proposed:  # Prevent overshooting
                    x = proposed
            elif x > proposed:
                x -= speed  # Move left
                if x < proposed:  # Prevent overshooting
                    x = proposed
            # x = proposed
        else: # proposed shot is out of bounds
            if x < proposed and x + PADDLE_WIDTH < right_bound: # need to move right and can still move right
                x += speed
            if x > proposed and x > left_bound:
                x -= speed
    else:  # opposition is on the right side
        # AI aims to hit the ball on the left side of its paddle
        proposed = ball_x + (BALL_SIZE // 2) - shift
        if proposed >= left_bound and proposed + PADDLE_WIDTH <= right_bound:
            if x < proposed:
                x += speed  # Move right
                if x > proposed:  # Prevent overshooting
                    x = proposed
            elif x > proposed:
                x -= speed  # Move left
                if x < proposed:  # Prevent overshooting
                    x = proposed
        else: # proposed shot is out of bounds
            if x < proposed and x + PADDLE_WIDTH < right_bound: # need to move right and can still move right
                x += speed
            if x > proposed and x > left_bound:
                x -= speed
    return prev_x, x

# this AI hits perfectly in the corner that the opponent is not on, 
# given that the AI can get there in time and the proposed destination 
# is possible to hit to within the x-bounds of the AI
def rival(x, opp_x, ball_x, speed, left_bound, right_bound):
    prev_x = x

    opp_center_x = opp_x + PADDLE_WIDTH // 2  # oppositions's paddle center position
    
    # Determine where the AI should hit the ball based on the opposition's position
    if opp_center_x < WIDTH // 2:  # opposition is on the left side
        # AI aims to hit the ball on the right side of its paddle
        proposed = ball_x + (BALL_SIZE // 2) - PADDLE_WIDTH
        if proposed >= left_bound and proposed + PADDLE_WIDTH <= right_bound:
            if x < proposed:
                x += speed  # Move right
                if x > proposed:  # Prevent overshooting
                    x = proposed
            elif x > proposed:
                x -= speed  # Move left
                if x < proposed:  # Prevent overshooting
                    x = proposed
        else: # proposed shot is out of bounds
            if x < proposed and x + PADDLE_WIDTH < right_bound: # need to move right and can still move right
                x += speed
            if x > proposed and x > left_bound:
                x -= speed
    else:  # opposition is on the right side
        # AI aims to hit the ball on the left side of its paddle
        proposed = ball_x + (BALL_SIZE // 2)
        if proposed >= left_bound and proposed + PADDLE_WIDTH <= right_bound: # proposed shot is within bounds
            if x < proposed:
                x += speed  # Move right
                if x > proposed:  # Prevent overshooting
                    x = proposed
            elif x > proposed:
                x -= speed  # Move left
                if x < proposed:  # Prevent overshooting
                    x = proposed
        else: # proposed shot is out of bounds
            if x < proposed and x + PADDLE_WIDTH < right_bound: # need to move right and can still move right
                x += speed
            if x > proposed and x > left_bound:
                x -= speed
    return prev_x, x

# this AI is impossible to beat as it perfectly hits to the corners by teleporting to the ball.
def teleporter(x, opp_x, ball_x, speed, left_bound, right_bound):
    prev_x = x

    opp_center_x = opp_x + PADDLE_WIDTH // 2  # oppositions's paddle center position
    
    # Determine where the AI should hit the ball based on the opposition's position
    if opp_center_x < WIDTH // 2:  # opposition is on the left side
        # AI aims to hit the ball on the right side of its paddle
        proposed = ball_x + (BALL_SIZE // 2) - PADDLE_WIDTH
        x = proposed
        
    else:  # opposition is on the right side
        # AI aims to hit the ball on the left side of its paddle
        proposed = ball_x + (BALL_SIZE // 2)
        x = proposed

    return prev_x, x

# this AI hits in the opposite direction the opposition is moving.
# if opposition is standing still, hit in the direction that the player is not on.
def matrix(x, opp_x, opp_prev_x, ball_x, speed, left_bound, right_bound):
    prev_x = x
    
    opp_velocity = opp_x - opp_prev_x

    opp_center_x = opp_x + PADDLE_WIDTH // 2  # oppositions's paddle center position

    # print(f'opp_velocity: {opp_velocity}')
    if opp_velocity != 0:
        if opp_velocity < 0: # opponent is moving left
            proposed = ball_x + (BALL_SIZE // 2) - PADDLE_WIDTH # hit right
            if proposed >= left_bound and proposed + PADDLE_WIDTH <= right_bound: # proposed shot is within bounds
                if x < proposed:
                    x += speed  # Move right
                    if x > proposed:  # Prevent overshooting
                        x = proposed
                elif x > proposed:
                    x -= speed  # Move left
                    if x < proposed:  # Prevent overshooting
                        x = proposed
            else: # proposed shot is out of bounds
                if x < proposed and x + PADDLE_WIDTH < right_bound: # need to move right and can still move right
                    x += speed
                if x > proposed and x > left_bound:
                    x -= speed
        else: # opponent is moving right
            proposed = ball_x + (BALL_SIZE // 2) # hit left
            if proposed >= left_bound and proposed + PADDLE_WIDTH <= right_bound: # proposed shot is within bounds
                if x < proposed:
                    x += speed  # Move right
                    if x > proposed:  # Prevent overshooting
                        x = proposed
                elif x > proposed:
                    x -= speed  # Move left
                    if x < proposed:  # Prevent overshooting
                        x = proposed
            else: # proposed shot is out of bounds
                if x < proposed and x + PADDLE_WIDTH < right_bound: # need to move right and can still move right
                    x += speed
                if x > proposed and x > left_bound:
                    x -= speed

    else:
        # Determine where the AI should hit the ball based on the opposition's position
        if opp_center_x < WIDTH // 2:  # opposition is on the left side
            # AI aims to hit the ball on the right side of its paddle
            proposed = ball_x + (BALL_SIZE // 2) - PADDLE_WIDTH # hit right
            if proposed >= left_bound and proposed + PADDLE_WIDTH <= right_bound: # proposed shot is within bounds
                if x < proposed:
                    x += speed  # Move right
                    if x > proposed:  # Prevent overshooting
                        x = proposed
                elif x > proposed:
                    x -= speed  # Move left
                    if x < proposed:  # Prevent overshooting
                        x = proposed
            else: # proposed shot is out of bounds
                if x < proposed and x + PADDLE_WIDTH < right_bound: # need to move right and can still move right
                    x += speed
                if x > proposed and x > left_bound:
                    x -= speed
            
        else:  # opposition is on the right side
            # AI aims to hit the ball on the left side of its paddle
            proposed = ball_x + (BALL_SIZE // 2) # hit left
            if proposed >= left_bound and proposed + PADDLE_WIDTH <= right_bound: # proposed shot is within bounds
                if x < proposed:
                    x += speed  # Move right
                    if x > proposed:  # Prevent overshooting
                        x = proposed
                elif x > proposed:
                    x -= speed  # Move left
                    if x < proposed:  # Prevent overshooting
                        x = proposed
            else: # proposed shot is out of bounds
                if x < proposed and x + PADDLE_WIDTH < right_bound: # need to move right and can still move right
                    x += speed
                if x > proposed and x > left_bound:
                    x -= speed

    return prev_x, x

def player_controls(x, speed, left_bound, right_bound, top: bool):
    prev_x = x
    keys = pygame.key.get_pressed()
    if not top:
        if keys[pygame.K_LEFT] and x > left_bound:
            x -= speed
        if keys[pygame.K_RIGHT] and x < right_bound - PADDLE_WIDTH:
            x += speed
    else:
        if keys[pygame.K_a] and x > left_bound:
            x -= speed
        if keys[pygame.K_d] and x < right_bound - PADDLE_WIDTH:
            x += speed
    return prev_x, x


# Game loop
running = True
while running:
    screen.fill(FLOOR_COLOR)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                print(f'Thank you for playing Tennis Pong by Brooklyn Guo! Quitting gracefully...')
                running = False
            if event.key == pygame.K_p:
                paused = not paused

    if paused:
        # Draw the "Paused" message
        pause_text = font.render("Paused", True, WHITE)
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))
        # pygame.display.flip()
        clock.tick(FPS)
        continue  # Skip the rest of the game loop while paused

    # bottom player choice (p1)
    if args.p1 == "basic":
        p1_prev_x, p1_x = basic(p1_x, ball_x, p1_speed, P1_LEFT_BOUND, P1_RIGHT_BOUND)
    elif args.p1 == "phantom":
        p1_prev_x, p1_x = phantom(p1_x, ball_x, p1_speed, P1_LEFT_BOUND, P1_RIGHT_BOUND)
    elif args.p1 == "sentinel":
        p1_prev_x, p1_x = sentinel(p1_x, ball_x, p1_speed, P1_LEFT_BOUND, P1_RIGHT_BOUND)
    elif args.p1 == "titan":
        p1_prev_x, p1_x = titan(p1_x, p2_x, ball_x, p1_speed, P1_LEFT_BOUND, P1_RIGHT_BOUND)
    elif args.p1 == "rival":
        p1_prev_x, p1_x = rival(p1_x, p2_x, ball_x, p1_speed, P1_LEFT_BOUND, P1_RIGHT_BOUND)
    elif args.p1 == "teleporter":
        p1_prev_x, p1_x = teleporter(p1_x, p2_x, ball_x, p1_speed, P1_LEFT_BOUND, P1_RIGHT_BOUND)
    elif args.p1 == "matrix":
        p1_prev_x, p1_x = matrix(p1_x, p2_x, p2_prev_x, ball_x, p1_speed, P1_LEFT_BOUND, P1_RIGHT_BOUND)
    else: # player controls
        p1_prev_x, p1_x = player_controls(p1_x, p1_speed, P1_LEFT_BOUND, P1_RIGHT_BOUND, False)
        
    
    # top player choice (p2)
    if args.p2 == "basic":
        p2_prev_x, p2_x = basic(p2_x, ball_x, p2_speed, P2_LEFT_BOUND, P2_RIGHT_BOUND)
    elif args.p2 == "phantom":
        p2_prev_x, p2_x = phantom(p2_x, ball_x, p2_speed, P2_LEFT_BOUND, P2_RIGHT_BOUND)
    elif args.p2 == "sentinel":
        p2_prev_x, p2_x = sentinel(p2_x, ball_x, p2_speed, P2_LEFT_BOUND, P2_RIGHT_BOUND)
    elif args.p2 == "titan":
        p2_prev_x, p2_x = titan(p2_x, p1_x, ball_x, p2_speed, P2_LEFT_BOUND, P2_RIGHT_BOUND)
    elif args.p2 == "rival":
        p2_prev_x, p2_x = rival(p2_x, p1_x, ball_x, p2_speed, P2_LEFT_BOUND, P2_RIGHT_BOUND)
    elif args.p2 == "teleporter":
        p2_prev_x, p2_x = teleporter(p2_x, p1_x, ball_x, p2_speed, P2_LEFT_BOUND, P2_RIGHT_BOUND)
    elif args.p2 == "matrix":
        p2_prev_x, p2_x = matrix(p2_x, p1_x, p1_prev_x, ball_x, p2_speed, P2_LEFT_BOUND, P2_RIGHT_BOUND)
    else: # player controls
        p2_prev_x, p2_x = player_controls(p2_x, p2_speed, P2_LEFT_BOUND, P2_RIGHT_BOUND, True)

    # Ball movement
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # Ball collision with walls
    if ball_x <= 0 or ball_x >= WIDTH - BALL_SIZE:
        ball_speed_x = -ball_speed_x

    # Ball collision with player paddle
    if (
        (p1_y - HIT_BOX_PADDING < ball_y + BALL_SIZE < p1_y + PADDLE_HEIGHT + HIT_BOX_PADDING)  # Ball's vertical collision with player paddle's hit box
        and p1_x - HIT_BOX_PADDING < ball_x + BALL_SIZE // 2 < p1_x + PADDLE_WIDTH + HIT_BOX_PADDING  # Ball's horizontal collision with player paddle's hit box
    ):
        # Calculate relative hit position
        relative_hit = ((ball_x + BALL_SIZE // 2) - (p1_x)) / PADDLE_WIDTH
        # print(f'COURT_LEFT: {COURT_LEFT}, COURT_RIGHT: {COURT_RIGHT}, relative_hit: {relative_hit}')

        # calculate the ball destination
        ball_destination_x, ball_destination_y = (COURT_WIDTH * relative_hit) + COURT_LEFT, 80
        # print(f'relative_hit: {relative_hit}, ball_destination: {(ball_destination_x, ball_destination_y)}')

        # Start the flash
        if args.flash:
            is_flashing = True

        # Calculate the difference between the ball's current position and the destination
        diff_x = ball_destination_x - ball_x
        diff_y = ball_destination_y - ball_y

        # Normalize the difference to get direction vector
        distance = (diff_x**2 + diff_y**2)**0.5  # Euclidean distance
        if distance != 0:
            ball_speed_x = (diff_x / distance) * SPEED_MODIFIER  # Horizontal speed (normalized)
            ball_speed_y = (diff_y / distance) * SPEED_MODIFIER  # Vertical speed (normalized)

        # Make sure the ball always moves upward
        ball_speed_y = -abs(ball_speed_y)  # Ensure the ball moves upward
        if args.randomness == "uniform":
            SPEED_MODIFIER = random.uniform(7.0, 18.0)
        elif args.randomness == "gauss":
            if args.ballspeed >= 5:
                SPEED_MODIFIER = random.gauss(args.ballspeed, 4)
            else:
                SPEED_MODIFIER = random.gauss(12, 4)
        else:
            SPEED_MODIFIER += INCREMENT
        RALLY_LENGTH += 1

    # Ball collision with AI paddle
    if (
        (p2_y - HIT_BOX_PADDING < ball_y + BALL_SIZE < p2_y + PADDLE_HEIGHT + HIT_BOX_PADDING)  # Ball's vertical collision with AI paddle's hit box
        and p2_x - HIT_BOX_PADDING < ball_x + BALL_SIZE // 2 < p2_x + PADDLE_WIDTH + HIT_BOX_PADDING  # Ball's horizontal collision with AI paddle's hit box
    ):
        # Calculate relative hit position (similar to player collision)
        relative_hit = ((ball_x + BALL_SIZE // 2) - (p2_x)) / PADDLE_WIDTH
        # print(f'COURT_LEFT: {COURT_LEFT}, COURT_RIGHT: {COURT_RIGHT}, relative_hit: {relative_hit}')

        # Calculate the ball destination
        ball_destination_x, ball_destination_y = (COURT_WIDTH * relative_hit) + COURT_LEFT, HEIGHT - 80
        # print(f'relative_hit: {relative_hit}, ball_destination: {(ball_destination_x, ball_destination_y)}')

        # Start the flash
        if args.flash:
            is_flashing = True

        # Calculate the difference between the ball's current position and the destination
        diff_x = ball_destination_x - ball_x
        diff_y = ball_destination_y - ball_y

        # Normalize the difference to get direction vector
        distance = (diff_x**2 + diff_y**2)**0.5  # Euclidean distance
        if distance != 0:
            ball_speed_x = (diff_x / distance) * SPEED_MODIFIER  # Horizontal speed (normalized)
            ball_speed_y = (diff_y / distance) * SPEED_MODIFIER  # Vertical speed (normalized)

        # Make sure the ball always moves downward
        ball_speed_y = abs(ball_speed_y)  # Ensure the ball moves downward
        if args.randomness == "uniform":
            SPEED_MODIFIER = random.uniform(7.0, 18.0)
        elif args.randomness == "gauss":
            if args.ballspeed >= 5:
                SPEED_MODIFIER = random.gauss(args.ballspeed, 4)
            else:
                SPEED_MODIFIER = random.gauss(12, 4)
        else:
            SPEED_MODIFIER += INCREMENT
        RALLY_LENGTH += 1
        RALLY_LENGTH += 1

    # Scoring conditions
    if ball_y > HEIGHT:  # Ball passed the player
        if args.flash:
            is_flashing = False
        ai_score += 1
        reset_ball()

    if ball_y < 0:  # Ball passed the AI
        if args.flash:
            is_flashing = False
        player_score += 1
        reset_ball()

    # Draw everything
    draw_court(FLOOR_COLOR, COURT_COLOR, SINGLES_COURT, SW19)
    draw_paddle(p1_x, p1_y)
    draw_paddle(p2_x, p2_y)
    draw_text()
    draw_ball()

    # In the game loop, before updating the screen:
    if is_flashing:
        pygame.draw.ellipse(screen, (255, 0, 0), (int(ball_destination_x - (BALL_SIZE/2)), int(ball_destination_y), 10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()