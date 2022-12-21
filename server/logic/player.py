from game import Game
from game import GameMode

from manager import Manager
import sys
sys.path.append('../../model')
from text2image import generate_image

from enum import IntEnum

class PlayerRole(IntEnum):
    HOST = 1
    GUEST = 2
    UNSPECIFIED = 3

def cmp(game:Game):
    return game.get_wait_time()

class Player:
    def __init__(self, manager:Manager, name:str):
        
        self.name = name
        self.role = None

        self.win = False
        self.ans = ''
        self.score = 0

        self.game = None
        self.manager = manager

    def join_game(self, game:Game=None, role:PlayerRole=PlayerRole.UNSPECIFIED):

        self.game = None
        self.role = role

        self.ans = ''
        self.score = 0

        games = self.manager.get_game_list()

        if game is not None:
            game.add_player(self)
        elif len(games) > 0:
            games.sort(key=cmp, reverse=True)
            games[0].add_player(self)
        else:
            index = self.manager.create_game_instance(GameMode.MATCH)
            games[index].add_player(self)
        
        if self.game is None:
            print('join game failed')
            return False
        return True

    # guest 给出答案，host 设置答案
    def give_answer(self, ans=str):

        self.ans = ans
        
        if self.role == PlayerRole.GUEST:
            if not self.win:
                self.game.collect_ans(self)
            else: print('the player has won')

    # guest 给出讨论，host 给出咒语
    def give_describe(self, describe:str, negtive:str='', rand_seed=0):

        if self.role == PlayerRole.GUEST:
            if not self.win:
                self.game.collect_desc(self.name, describe)
            else: print('the player has won')
            return None
        else: return generate_image(describe, negtive, self.name, rand_seed)

    def get_score(self):
        return self.score

    def get_win(self):
        return self.win