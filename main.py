import pygame, sys, random, os,math,json
from pygame.math import Vector2
import socket
import threading
import json
from food import Food
from settings import *
from snake import Snake
from network import NetworkClient



# def check_internet_connection():
#     try:
#         socket.create_connection(("8.8.8.8", 53), timeout=2)
#         return True
#     except OSError:
#         return False


server = "192.168.99.230"
port = 5555

# class NetworkClient:
#     def __init__(self):
#         self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.sock.connect((server, port))
#         self.other_scores = {}  # holds {player_id: score} received from server
#         self.running = True
#         self.lock = threading.Lock()

#         # Start background thread to listen for server messages
#         threading.Thread(target=self.listen_thread, daemon=True).start()

#     def listen_thread(self):
#         while self.running:
#             try:
#                 data = self.sock.recv(4096)
#                 if data:
#                     scores = json.loads(data.decode())
#                     with self.lock:
#                         self.other_scores = scores
#                 else:
#                     break
#             except Exception as e:
#                 print(f"[NetworkClient] Error in listen thread: {e}")
#                 break
#         self.sock.close()

#     def send_score(self, score):
#         """
#         Send the current player score to the server as JSON.
#         """
#         try:
#             self.sock.sendall(json.dumps({"score": score}).encode())
#         except Exception as e:
#             print(f"[NetworkClient] Error sending score: {e}")

#     def get_scores(self):
#         """
#         Return a copy of the other players' scores.
#         """
#         with self.lock:
#             return dict(self.other_scores)

#     def stop(self):
#         self.running = False
#         self.sock.close()




pygame.init()



title_font = pygame.font.Font(None, 60)
score_font = pygame.font.Font(None,60)
high_score_font = pygame.font.Font(None,60)
high_score_text_font = pygame.font.Font(None, 30)
score_text_font = pygame.font.Font(None,30)
prompt_text_font = pygame.font.Font("font/bold.ttf", 25)
credits_text_font = pygame.font.Font("font/bold.ttf", 18)
help_text_font = pygame.font.Font("font/bold.ttf",25)
go_help_text_font = pygame.font.Font("font/bold.ttf",25)
mode_text_font = pygame.font.Font("font/bold.ttf", 30)
offline_text_font = pygame.font.Font("font/bold.ttf",25)
online_text_font = pygame.font.Font("font/bold.ttf",25)
not_avaiable_text_font= pygame.font.Font("font/bold.ttf",25)

ip_active = False
user_active = False
username = "Liam"
server_ip = "192.168.99.230"

names = ""
scor = ""

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



class Button:
    def __init__(self, pos, image_path, hover_image_path):
        self.image = pygame.image.load(resource_path(image_path)).convert_alpha()
        self.hover_image = pygame.image.load(resource_path(hover_image_path)).convert_alpha()
        self.rect = self.image.get_rect(center=pos)

    def draw(self, screen):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            screen.blit(self.hover_image, self.rect)
        else:
            screen.blit(self.image, self.rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                return True
        return False

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.state = "MENU"
        self.score = 0
        self.high_score = 0
        self.high_score = load_high_score()
        self.network = NetworkClient(server_ip,username)
    def draw(self):
        self.food.draw()
        self.snake.draw()
    def update(self):
        if self.state in ["RUNNING", "ONLINE_PLAY"]:
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
            self.network.send_score(self.score)
    def check_collison_with_edges(self):
        if self.snake.body[0].x == number_of_cell or self.snake.body[0].x == -1:
            self.game_over()
        if self.snake.body[0].y == number_of_cell or self.snake.body[0].y == -1:
            self.game_over()
    def game_over(self):
        self.snake.reset()
        self.food.position = self.food.generate_random_pos(self.snake.body)
        if self.state == "ONLINE_PLAY":
            self.state = "DEAD"
        else:
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



def draw_grid():
    for x in range(number_of_cell):
        for y in range(number_of_cell):
            rect = pygame.Rect(OFFSET + x * cell_size, OFFSET + y * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen,LIGHT_GREEN,rect,1)

start_button = Button(
    pos=(screen.get_width() // 2, 300),
    image_path="online2.png",
    hover_image_path="online1.png"
)

def draw_main_menu():
    screen.fill(GREEN)

    title_surface = title_font.render("Liam's Snake", True, DARK_GREEN)
    credits_text_surface = credits_text_font.render("Background music is made by my friend Kane", True, DARK_GREEN)
    go_help_surface = go_help_text_font.render("Press h for help", True, DARK_GREEN)

    screen.blit(title_surface, ((screen.get_width() - title_surface.get_width()) // 2, 150))
    screen.blit(go_help_surface, ((screen.get_width() - go_help_surface.get_width()) // 2, 350))
    screen.blit(credits_text_surface, (OFFSET + 220, cell_size * number_of_cell + 120))

    # Draw hoverable start button
    start_button.draw(screen)

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

def handleclick(event):
    global username,font,color
    font = pygame.font.Font(None, 40)
    # input_box = pygame.Rect(200, 185, 240, 50)  # Fixed width
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive

    if game.state == "ONLINE":
        global user_active, ip_active, server_ip, username
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box
            if input_box.collidepoint(event.pos):
                user_active = True
                ip_active = False
            elif ip_box.collidepoint(event.pos):
                user_active = False
                ip_active = True
            else:
                user_active = False
                ip_active = False
        


        if event.type == pygame.KEYDOWN:
            if user_active:
                if event.key == pygame.K_RETURN:
                    print("Username entered:", username)
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += event.unicode
            elif ip_active:
                if event.key == pygame.K_RETURN:
                    print("Server IP entered:", server_ip)
                    game.state = "ONLINE_PLAY"
                elif event.key == pygame.K_BACKSPACE:
                    server_ip = server_ip[:-1]
                else:
                    if event.unicode.isdigit() or event.unicode == "." or event.unicode == ":":
                        server_ip += event.unicode



def OnlineModeName():
    global ip_box, input_box
    ip_box = pygame.Rect(225, 350, 240, 50)
    input_box = pygame.Rect(225, 250, 240, 50)
    screen.fill(GREEN)
    draw_box(input_box, username, user_active,placeholder="Username")
    draw_box(ip_box, server_ip, ip_active,"Server IP")
    pygame.display.update()

def draw_box(box, text, is_active, placeholder=""):
    # UPDATED:s Active box has a different color
    border_color = pygame.Color('dodgerblue2') if is_active else pygame.Color('lightskyblue3')
    pygame.draw.rect(screen, border_color, box, 2)

    if text == "" and not is_active:
        # Placeholder style (gray)
        display_text = placeholder
        text_surface = font.render(display_text, True, pygame.Color('gray'))
    else:
        # Cursor if active
        cursor = "|" if is_active and pygame.time.get_ticks() % 1000 < 500 else ""
        display_text = text + cursor
        text_surface = font.render(display_text, True, pygame.Color('white'))

    text_surface = font.render(display_text, True, pygame.Color('white'))
    max_text_width = box.w - 10

    # UPDATED: Clip text if too long
    if text_surface.get_width() > max_text_width:
        offset = text_surface.get_width() - max_text_width
        clipped_surface = text_surface.subsurface((offset, 0, max_text_width, text_surface.get_height()))
    else:
        clipped_surface = text_surface

    screen.blit(clipped_surface, (box.x + 5, box.y + 5))


def draw_other_scores(screen, network, font):
    """
    Display the scores of other players (from the server) on screen.
    Assumes `network.get_scores()` returns a dictionary: {username: score}
    """
    scores = network.get_scores()
    # print("Received scores:", scores)
    # print(scores.items())
    for name, score in scores.items():
        global names,scor
        names = name
        scor = score
        print(str(names) + " " + str(scor))




pygame.display.set_caption("Retro Snake")

clock = pygame.time.Clock()

game = Game()

# save_high_score(0)



SNAKE_UPDATE = pygame.USEREVENT + 1
pygame.time.set_timer(SNAKE_UPDATE,150)


while True:
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            game.network.stop()
            pygame.quit()
            sys.exit()
        if game.state == "MENU":

            if start_button.is_clicked(event):
                game.state = "MODE"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                game.state = "HELP"
                
        # if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
        #     game.state = "HELP"
        
        if game.state == "HELP":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game.state = "MENU"

        if game.state == "MODE":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                game.state = "OFFLINE"
        if game.state == "MODE":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_o:
                game.state = "ONLINE"
        if game.state == "ONLINE":
            handleclick(event)
        if game.state == "DEAD":
            if event.type == pygame.KEYDOWN:
                game.snake.reset()
                # game.food.position = game.food.generate_random_pos(game.snake.body)
                game.score = 0
                game.state = "ONLINE_PLAY"
        elif game.state == "STOPPED":
            if event.type == pygame.KEYDOWN:
                game.state = "RUNNING"
        
        elif game.state in ["RUNNING","ONLINE_PLAY"]:
            if event.type == SNAKE_UPDATE:
                game.update()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and game.snake.direction != Vector2(0,1):
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
    elif game.state == "ONLINE":
        OnlineModeName()
    elif game.state == "OFFLINE":
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
        #draw_other_scores(screen,game.network,score_font)
        game.state = "STOPPED"
        pygame.display.update()
    elif game.state == "ONLINE_PLAY":
        screen.fill(GREEN)
        draw_grid()
        pygame.draw.rect(screen, DARK_GREEN, (OFFSET-5, OFFSET-5, cell_size*number_of_cell+10, cell_size*number_of_cell+10), 5)
        game.draw()
        draw_other_scores(screen, game.network, score_font)
    
        title_surface = title_font.render("Retro Snake", True, DARK_GREEN)
        right_now_score = score_font.render(str(game.score),True, DARK_GREEN)
        online_score =  high_score_font.render(str(scor), True, DARK_GREEN)
        online_name = high_score_text_font.render(names, True, DARK_GREEN)
        own_name = score_text_font.render(username, True, DARK_GREEN)
    
        screen.blit(title_surface, (OFFSET-5,20))
        # screen.blit(right_now_score, (OFFSET+50, cell_size*number_of_cell +115))
        # screen.blit(own_name, (OFFSET+15, cell_size*number_of_cell + 90))
        screen.blit(online_score, (OFFSET+490, cell_size * number_of_cell + 115))
        screen.blit(online_name,(OFFSET+460, cell_size * number_of_cell + 90))
        pygame.display.update()
        
    elif game.state == "DEAD":
        screen.fill(GREEN)
        draw_grid()
        pygame.draw.rect(screen, DARK_GREEN, (OFFSET-5, OFFSET-5, cell_size*number_of_cell+10, cell_size*number_of_cell+10), 5)
        game.draw()
        draw_other_scores(screen, game.network, score_font)
    
        title_surface = title_font.render("Retro Snake", True, DARK_GREEN)
        score_surface = score_font.render(str(game.score),True, DARK_GREEN)
        high_score_surface =  high_score_font.render(str(scor), True, DARK_GREEN)
        high_score_text_surface = high_score_text_font.render(names, True, DARK_GREEN)
        score_text_surface = score_text_font.render(username, True, DARK_GREEN)
    
        screen.blit(title_surface, (OFFSET-5,20))
        # screen.blit(score_surface, (OFFSET+50, cell_size*number_of_cell +115))
        # screen.blit(score_text_surface, (OFFSET+15, cell_size*number_of_cell + 90))
        screen.blit(high_score_surface, (OFFSET+490, cell_size * number_of_cell + 115))
        screen.blit(high_score_text_surface,(OFFSET+460, cell_size * number_of_cell + 90))
        pygame.display.update()
        

    # else:
    #     screen.fill(GREEN)
    #     draw_grid()
    #     pygame.draw.rect(screen, DARK_GREEN, (OFFSET-5, OFFSET-5, cell_size*number_of_cell+10, cell_size*number_of_cell+10), 5)
    #     game.draw()
    
    #     title_surface = title_font.render("Retro Snake", True, DARK_GREEN)
    #     score_surface = score_font.render(str(game.score),True, DARK_GREEN)
    #     high_score_surface =  high_score_font.render(str(game.high_score), True, DARK_GREEN)
    #     high_score_text_surface = high_score_text_font.render("High Score", True, DARK_GREEN)
    #     score_text_surface = score_text_font.render("Current Score", True, DARK_GREEN)
    
    #     screen.blit(title_surface, (OFFSET-5,20))
    #     screen.blit(score_surface, (OFFSET+50, cell_size*number_of_cell +115))
    #     screen.blit(score_text_surface, (OFFSET+15, cell_size*number_of_cell + 90))
    #     screen.blit(high_score_surface, (OFFSET+490, cell_size * number_of_cell + 115))
    #     screen.blit(high_score_text_surface,(OFFSET+460, cell_size * number_of_cell + 90))
    #     # draw_other_scores(screen, game.network, score_font)
    
    #     pygame.display.update()
        

    clock.tick(60)

        
    




