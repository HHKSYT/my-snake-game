import pygame, sys, random, os,math,json
from pygame.math import Vector2
import socket

# def check_internet_connection():
#     try:
#         socket.create_connection(("8.8.8.8", 53), timeout=2)
#         return True
#     except OSError:
#         return False
    

def resource_path(relative_path):
    # Detects if the program is being run from a PyInstaller bundle
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


pygame.init()

title_font = pygame.font.Font(None, 60)
score_font = pygame.font.Font(None,60)
high_score_font = pygame.font.Font(None,60)
high_score_text_font = pygame.font.Font(None, 30)
score_text_font = pygame.font.Font(None,30)
prompt_text_font = pygame.font.Font("bold.ttf", 25)
credits_text_font = pygame.font.Font("bold.ttf", 25)
help_text_font = pygame.font.Font("bold.ttf",25)
go_help_text_font = pygame.font.Font("bold.ttf",25)
mode_text_font = pygame.font.Font("bold.ttf", 30)
offline_text_font = pygame.font.Font("bold.ttf",25)
online_text_font = pygame.font.Font("bold.ttf",25)
not_avaiable_text_font= pygame.font.Font("bold.ttf",25)

help_text = """
    Welcome to Liam's snake game
    A game created for fun
    created with python
    How to play:
    move the snake with arrows keys
    eat the food
    there is no limit here (unless you fully cover the grid)
    and most importantly
    have fun
    Press ESC to go back
"""


GREEN = (173,204,96)
DARK_GREEN = (43,51,24)
LIGHT_GREEN = (100,120,80)

cell_size = 20
number_of_cell = 27
OFFSET = 75

def load_high_score(filename="highscore.json"):
    try:
        with open(filename, "r") as f:
            score = json.load(f).get("high_score", 0)
            print(f"[DEBUG] Loaded high score from file: {score}")
            return score
    except (FileNotFoundError, ValueError) as e:
        print(f"[DEBUG] Could not load high score file: {e}")
        return 0

def save_high_score(score, filename="highscore.json"):
    try:
        with open(filename, "w") as f:
            json.dump({"high_score": score}, f)
        print(f"[DEBUG] Saved high score to file: {score}")
    except Exception as e:
        print(f"[ERROR] Could not save high score: {e}")

class Food:
    def __init__(self,snake_body):
        self.position = self.generate_random_pos(snake_body)
    def draw(self):
        food_rect = pygame.Rect(OFFSET + self.position.x * cell_size, OFFSET + self.position.y * cell_size,cell_size,cell_size)
        screen.blit(food_surface,food_rect)
    def generate_random_cell(self):
        x = random.randint(0, number_of_cell -1)
        y = random.randint(0,number_of_cell -1)
        return Vector2(x,y)
    def generate_random_pos(self, snake_body):
        position = self.generate_random_cell()
        while position in snake_body:
            position = self.generate_random_cell()

        return position

class Snake:
    def __init__(self):
        self.body = [Vector2(6,9), Vector2(5,9), Vector2(4,9)]
        self.direction = Vector2(1,0)
        self.add_segment = False
        self.eat_sound = pygame.mixer.Sound(resource_path("Sounds/eat.mp3"))
        self.wall_hit_sound = pygame.mixer.Sound(resource_path("Sounds/wall.mp3"))
    def draw(self):
        for segment in self.body:
            segment_rect = (OFFSET + segment.x *cell_size, OFFSET + segment.y*cell_size, cell_size, cell_size)
            pygame.draw.rect(screen,DARK_GREEN,segment_rect, 0,7)
    def update(self):
        self.body.insert(0,self.body[0] + self.direction)
        if self.add_segment == True:

            self.add_segment = False
        else:
            self.body = self.body[:-1]
    def reset(self):
        self.body = [Vector2(6,9), Vector2(5,9), Vector2(4,9)]
        self.direction = Vector2(1,0)

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.state = "MENU"
        self.score = 0
        self.high_score = 0
        self.high_score = load_high_score()
    def draw(self):
        self.food.draw()
        self.snake.draw()
    def update(self):
        if self.state == "RUNNING":
            self.snake.update()
            self.check_collison_with_food()
            self.check_collison_with_edges()
            self.check_collision_with_tail()

    def check_collison_with_food(self):
        if self.snake.body[0] == self.food.position:
            self.food.position = self.food.generate_random_pos(self.snake.body)
            self.snake.add_segment = True
            self.score += 1
            if self.score > self.high_score:
                self.high_score = self.score
            self.snake.eat_sound.play()
    def check_collison_with_edges(self):
        if self.snake.body[0].x == number_of_cell or self.snake.body[0].x == -1:
            self.game_over()
        if self.snake.body[0].y == number_of_cell or self.snake.body[0].y == -1:
            self.game_over()
    def game_over(self):
        self.snake.reset()
        self.food.position = self.food.generate_random_pos(self.snake.body)
        self.state = "STOPPED"
        if self.score > self.high_score:
            self.high_score = self.score
        save_high_score(self.high_score)
        self.score = 0
        self.snake.wall_hit_sound.play()
    def check_collision_with_tail(self):
        headless_body = self.snake.body[1:]
        if self.snake.body[0] in headless_body:
            self.game_over()


screen = pygame.display.set_mode((2*OFFSET + cell_size*number_of_cell, 2*OFFSET + cell_size*number_of_cell))

def draw_grid():
    for x in range(number_of_cell):
        for y in range(number_of_cell):
            rect = pygame.Rect(OFFSET + x * cell_size, OFFSET + y * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen,LIGHT_GREEN,rect,1)

def draw_main_menu():
    screen.fill(GREEN)
    
    title_surface = title_font.render("Liam's Snake", True, DARK_GREEN)
    prompt_surface = prompt_text_font.render("Press ENTER to Start", True, DARK_GREEN)
    credits_text_surface = credits_text_font.render("Background music is made by my friend Kane",True, DARK_GREEN)
    go_help_surface = go_help_text_font.render("Press h for help", True, DARK_GREEN)

    # Center the text
    screen.blit(title_surface, ((screen.get_width() - title_surface.get_width()) // 2, 150))
    screen.blit(prompt_surface, ((screen.get_width() - prompt_surface.get_width()) // 2, 250))
    screen.blit(go_help_surface, ((screen.get_width() - go_help_surface.get_width()) // 2, 350))
    screen.blit(credits_text_surface, (OFFSET+235, cell_size * number_of_cell + 120))
    pygame.display.update()

def draw_help_menu():
    screen.fill(GREEN)

    lines = help_text.strip().split("\n")  # Split into lines
    start_y = 100  # Starting vertical position
    line_spacing = 35  # Pixels between lines

    for i, line in enumerate(lines):
        rendered_line = help_text_font.render(line.strip(), True, DARK_GREEN)
        screen.blit(
            rendered_line,
            ((screen.get_width() - rendered_line.get_width()) // 2, start_y + i * line_spacing)
        )

    pygame.display.update()

def draw_choose_offline():
    screen.fill(GREEN)
    
    mode_text_surface = mode_text_font.render("Choose Offline or Online", True, DARK_GREEN)
    offline_text_surface = offline_text_font.render("Press f for offline", True, DARK_GREEN)
    online_text_surface = online_text_font.render("Press o for online", True, DARK_GREEN)
    not_avaiable_surface = not_avaiable_text_font.render("Online mode is currently not avaiable", True, DARK_GREEN)

    screen.blit(mode_text_surface, ((screen.get_width() - mode_text_surface.get_width()) // 2, 150))
    screen.blit(offline_text_surface, ((screen.get_width() - offline_text_surface.get_width()) // 2, 250))
    screen.blit(online_text_surface, ((screen.get_width() - online_text_surface.get_width()) // 2, 350))
    screen.blit(not_avaiable_surface, ((screen.get_width() - not_avaiable_surface.get_width()) // 2, 400))
    pygame.display.update()


pygame.display.set_caption("Retro Snake")

clock = pygame.time.Clock()

game = Game()

# save_high_score(0)


food_surface = pygame.image.load(resource_path("Final.png"))

SNAKE_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SNAKE_UPDATE,200)


while True:
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game.state == "MENU":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                game.state = "MODE"
                
            if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                game.state = "HELP"
        
        if game.state == "HELP":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game.state = "MENU"

        if game.state == "MODE":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                game.state = "RUNNING"
                
        elif game.state == "STOPPED":
            if event.type == pygame.KEYDOWN:
                game.state = "RUNNING"

        elif game.state == "RUNNING":
            if event.type == SNAKE_UPDATE:
                game.update()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and game.   snake.direction != Vector2(0,1):
                    game.snake.direction = Vector2(0,-1)
                if event.key == pygame.K_DOWN and game.snake.direction != Vector2(0,-1):
                    game.snake.direction = Vector2(0,1)
                if event.key == pygame.K_LEFT and game.snake.direction != Vector2(1,0):
                    game.snake.direction = Vector2(-1,0)
                if event.key == pygame.K_RIGHT and game.snake.direction != Vector2(-1,0):
                    game.snake.direction = Vector2(1,0)
    if game.state == "HELP":
        draw_help_menu()
    elif game.state == "MODE":
        draw_choose_offline()
    elif game.state == "MENU":
        draw_main_menu()
    else:

        screen.fill(GREEN)
        draw_grid()
        pygame.draw.rect(screen, DARK_GREEN, (OFFSET-5, OFFSET-5, cell_size*number_of_cell+10, cell_size*number_of_cell+10), 5)
        game.draw()
        title_surface = title_font.render("Retro Snake", True, DARK_GREEN)
        score_surface = score_font.render(str(game.score),True, DARK_GREEN)
        high_score_surface =  high_score_font.render(str(game.high_score), True, DARK_GREEN)
        high_score_text_surface = high_score_text_font.render("High Score", True, DARK_GREEN)
        score_text_surface = score_text_font.render("Current Score", True, DARK_GREEN)
        
        screen.blit(title_surface, (OFFSET-5,20))
        screen.blit(score_surface, (OFFSET+50, cell_size*number_of_cell +115))
        screen.blit(score_text_surface, (OFFSET+15, cell_size*number_of_cell + 90))
        screen.blit(high_score_surface, (OFFSET+490, cell_size * number_of_cell + 115))
        screen.blit(high_score_text_surface,(OFFSET+460, cell_size * number_of_cell + 90))
        pygame.display.update()

    clock.tick(60)
    
