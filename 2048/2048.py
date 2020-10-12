import curses
from random import randrange, choice
from collections import defaultdict

#ord()return the ASCII value of the variable
#consider capitalized letters
letter_codes = [ord(character) for character in "WASDRQwasdeq"]
actions = ["Up", "Left", "Down", "Right", "Restart", "Exit"]
#connect actions and letter codes
actions_dict = dict(zip(letter_codes, actions * 2))

def get_user_action(keyboard):
    char = "N"
    while char not in actions_dict:
        #pressed key's ASCHII value
        char = keyboard.getch()
    return actions_dict[char]

#4 * 4 matrix, solve using zip(*)
def transpose(field):
    return [list(row) for row in zip(*field)]

#invert every line in the matrix, not about the concept of inverse matrix
def invert(field):
    return [row[::-1] for row in field]

class GameField(object):
    def __init__(self, height = 4, width = 4, win = 2048):
        self.height = height
        self.width = width
        self.win_value = win
        self.score = 0
        self.highscore = 0
        self.reset()

    def reset(self):
        if self.score > self.highscore:
            self.highscore = self.score
        self.score = 0
        #initialize starting interface to 0 and randomly generate the initial values
        self.field = [[0 for i in range(self.width)] for j in range(self.height)]
        self.generate()
        self.generate()

    def move(self, direction):
        def move_row_left(row):
            def combine(row):
                #combine elements together
                new_row = [i for i in row if i !=0]
                new_row += [0 for i in range(len(row) - len(new_row))]
                return new_row
            
            def merge(row):
                #merge adjacent elements together
                pair = False
                new_row = []
                for i in range(len(row)):
                    if pair:
                        new_row.append(2 * row[i])
                        #update score
                        self.score += 2 * row[i]
                        pair = False
                    else:
                        #whether the adjacent elements can merge
                        if i + 1 < len(row) and row[i] == row[i + 1]:
                            #can merge, add 0 to the list
                            pair = True
                            new_row.append(0)
                        else:
                            #can't merge, add the element into the list
                            new_row.append(row[i])
                assert len(new_row) == len(row)
                return new_row
            return combine(merge(combine(row)))

        #create moves dictionary, different field -> different keys
        moves = {}
        #modifies moves['Left'] to have different values
        moves['Left'] = lambda field: [move_row_left(row) for row in field]
        moves['Right'] = lambda field: invert(moves['Left'] (invert(field)))
        moves['Up'] = lambda field: transpose(moves['Left'] (transpose(field)))
        moves['Down'] = lambda field: transpose(moves['Right'] (transpose(field)))

        #directions are the keys -> see if they are in the moves dict
        if direction in moves:
            #to see if the movement action can be completed
            if self.move_is_possible(direction):
                #do the corresponding action on the field
                self.field = moves[direction](self.field)
                self.generate()
                return True
            else:
                return False
    
    #win and lose
    def is_win(self):
        #wins if any element is larger than self.win_value
        return any(any(i >= self.win_value for i in row) for row in self.field)
    
    def is_gameover(self):
        #loses if can't move and merge anymore
        return not any(self.move_is_possible(move) for move in actions)
    
    def draw(self, screen):
        help_string1 = '(W)Up (S)Down (A)Left (D)Right'
        help_string2 = '     (R)Restart (Q)Exit'
        gameover_string = '           GAME OVER'
        win_string = '          YOU WIN!'

        #cast to the terminal
        def cast(string):
            #screen.addstr: draw strings
            screen.addstr(string + '\n')
        #horizontal lines
        def draw_hori():
            line = "+" + ("+------" * self.width + "+")[1:]
            separator = defaultdict(lambda: line)
            if not hasattr(draw_hori, 'counter'):
                draw_hori.counter = 0
            cast(separator[draw_hori.counter])
            draw_hori.counter += 1
        #vertical lines
        def draw_ver():
            cast(''.join('|{: ^5} '.format(num) if num > 0 else '|      ' for num in row) + '|')

        screen.clear()
        #draw score and highest score
        cast('SCORE: ' + str(self.score))
        if 0 != self.highscore:
            cast('HIGHEST SCORE: ' + str(self.highscore))

        #draw frame
        for row in self.field:
            draw_hori()
            draw_ver()
        draw_hori()

        #prompts
        if self.is_win():
            cast(win_string)
        else:
            if self.is_gameover():
                cast(gameover_string)
            else:
                cast(help_string1)
        cast(help_string2)

    def generate(self):
        new_elem = 4 if randrange(100) > 89 else 2
        (i, j) = choice([(i, j) for i in range(self.width) for j in range(self.height) if self.field[i][j] == 0])
        self.field[i][j] = new_elem
    
    def move_is_possible(self, direction):
        def left_movable(row):
            def change(i):
                #left is empty and right is filled -> move to the left
                if row[i] == 0 and row[i + 1] != 0:
                    return True
                #left = right, merge with left
                if row[i] != 0 and row[i + 1] == row[i]:
                    return True
                return False
            return any(change(i) for i in range(len(row) - 1))
        
        check = {}
        check['Left'] = lambda field: any(left_movable(row) for row in field)
        check['Right'] = lambda field: check['Left'] (invert(field))
        check['Up'] = lambda field: check['Left'] (transpose(field))
        check['Down'] = lambda field: check['Right'] (transpose(field))

        #if directions exist in check dict, evaluates the corresponding functions
        if direction in check:
            return check[direction](self.field)
        else:
            return False

#Main Logic
def main(stdscr):
    def init():
        #reset the field
        game_field.reset()
        return 'Game'
    
    def end(state):
        game_field.draw(stdstr)
        #reads player's input to determine to restart the game or end the game
        action = get_user_action(stdscr)
        #if not 'Restart' or 'Exit', continue
        responses = defaultdict(lambda: state)

        responses['Restart'], responses['Exit'] = 'Init', 'Exit'
        return responses[action]
    
    def game():
        game_field.draw(stdscr)
        action = get_user_action(stdscr)
        if action == "Restart":
            return 'Init'
        if action == 'Exit':
            return 'Exit'
        if game_field.move(action):
            if game_field.is_win():
                return 'Win'
            if game_field.is_gameover():
                return ' Gameover'
        return 'Game'
    
    state_actions = {
        'Init': init,
        'Win': lambda: end('Win'),
        'Gameover': lambda: end('Gameover'),
        'Game': game
    }

    curses.use_default_colors()

    #create a gamefield object and set win value to 2048
    game_field = GameField(win=2048)

    state = 'Init'

    #start FSM
    while state != 'Exit':
        state = state_actions[state]()

curses.wrapper(main)