from . import GameMode
from . import GameState
from . import PlayerRole
from . import create_game_instance, get_all_game_list

def cmp(game):
    return game.get_wait_time()

class Player:

    def __init__(self, name: str):

        self.name = name
        self.role = None

        self.win = False
        self.score = 0

        self.game = None
        self.ready = False

    def join_game(self,
                  mode = 'match',
                  game = None,
                  role: PlayerRole = PlayerRole.UNSPECIFIED):
        self.role = role

        self.win = False
        self.score = 0

        self.game = None
        self.ready = False

        games = get_all_game_list()
        if mode is None or mode == 'match':

            if game is not None:
                return game.add_player(self)

            elif len(games) > 0:

                match_games = []
                for game in games:
                    if game.mode == GameMode.MATCH and game.state == GameState.WAITING:
                        match_games.append(game)

                if len(match_games) > 0:
                    match_games.sort(key=cmp, reverse=True)
                    retcode, message = match_games[0].add_player(self)
                    
                    if retcode:
                        return True, message
        
        index, message = create_game_instance(GameMode.MATCH)

        if index != -1:
            return games[index].add_player(self)
        return False, message

    def set_ready(self, ready:bool):

        return self.game.check_ready(self, ready, 5)

    # guest 给出答案，host 给出咒语
    def give_info(self, info: str, negtive: str = '', rand_seed=0):

        if self.role == PlayerRole.GUEST:
            return self.game.collect_ans(self, info)
        else:
            return self.game.collect_img(info, negtive, rand_seed)
            # return None # text2image.generate_image(describe, negtive, self.name, rand_seed)

    def get_info(self):

        return self.game.get_info()