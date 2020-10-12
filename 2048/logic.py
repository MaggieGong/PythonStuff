import curses
from random import randrange, choice
from collections import defaultdict

actions = ["up", "down", "left", "right", "restart", "exit"]
#ord()return the ASCII value of the variable
#consider capitalized letters
letter_codes = [ord(character) for character in "WASDRQwasdeq"]
#connect actions and letter codes
actions_dict = dict(zip(letter_codes, actions * 2))

#FSM
#init, win, game, gameover, exit

def init():
    #initialize the game
    return "Game"

def end(state):
    #ending interface
    #letter_code: to restart or end the game
    #defaultdict: default value for all the keys other than "Restart" and "Exit"
    player_response = defaultdict(lambda: state)
    player_response["Restart"], player_response["Exit"] = "Init", "Exit"
    return player_response[action]

def game():
    #game state
    #reads player's action
    if action == "Restart":
        return "Init"
    if action == "Exit":
        return "Exit"
    if "player acts":
        if "player wins":
            return "Win"
        if "player loses":
            return "Gameover"
    return "Game"

state_actions = {
    'Init': init,
    'Win': lambda: end('Win')
    'Gameover': lambda: end('Gameover')
    'Game': game
}

state = 'Init'

while state != 'Exit':
    state = state_actions[state]()