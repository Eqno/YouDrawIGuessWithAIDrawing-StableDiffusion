from . import GameMode
from . import GameState
from . import PlayerRole
from . import create_game_instance, get_all_game_list

import sys, os

# sys.path.append(os.getcwd().replace('\\', '/') + '/../')
# from model import text2image

def cmp(game):
    return game.get_wait_time()

class Player:

    def __init__(self, name: str):

        self.name = name
        self.role = None

        self.win = False
        self.ans = ''
        self.score = 0

        self.game = None
        self.ready = False

    def join_game(self,
                  game = None,
                  role: PlayerRole = PlayerRole.UNSPECIFIED):
        self.role = role

        self.win = False
        self.ans = ''
        self.score = 0

        self.game = None
        self.ready = False

        games = get_all_game_list()

        if game is not None:

            return game.add_player(self)

        elif len(games) > 0:

            match_games = []
            for game in games:
                if game.mode == GameMode.MATCH and game.state == GameState.WAITING:
                    match_games.append(game)

            if len(match_games) > 0:
                match_games.sort(key=cmp, reverse=True)
                return match_games[0].add_player(self)
        
        index, message = create_game_instance(GameMode.MATCH)

        if index != -1:
            return games[index].add_player(self)
        return False, message

    def set_ready(self, ready:bool):

        if self.game.state != GameState.WAITING:
            return False, 'player could only ready when waiting'

        self.ready = ready
        retcode, message = self.game.check_ready()

        if retcode:
            return retcode, { 'begin_game': True, 'other_info': message}
        return True, { 'begin_game': False, 'other_info': 'player set ready succeed'}

    # guest 给出答案，host 设置答案
    def give_answer(self, ans=str):

        self.ans = ans

        if self.role == PlayerRole.GUEST:
            if not self.win:
                self.game.collect_ans(self)
            else:
                print('the player has won')

    # guest 给出讨论，host 给出咒语
    def give_describe(self, describe: str, negtive: str = '', rand_seed=0):

        if self.role == PlayerRole.GUEST:
            if not self.win:
                self.game.collect_desc(self.name, describe)
            else:
                print('the player has won')
            return None
        else:
            return None # text2image.generate_image(describe, negtive, self.name, rand_seed)

    def get_score(self):
        return self.score

    def get_win(self):
        return self.win