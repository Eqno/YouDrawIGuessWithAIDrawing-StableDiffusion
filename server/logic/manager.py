from game import *
from player import *

GAME_MAX_NUM = 20
PLAYER_MAX_NUM = 100

class Manager:
    def __init__(self):
        self.games = []
        self.players = []

    def get_game_list(self):
        return self.games
    
    def get_player_list(self):
        return self.players

    # 创建游戏实例，并将索引和信息返回
    def create_game_instance(self, game_mode:GameMode):

        if len(self.games) < GAME_MAX_NUM:
            self.games.append(Game(self, game_mode))
            return len(self.games) - 1, 'create game instance succeed'

        return -1, 'instance num exceeded max: {}'.format(GAME_MAX_NUM)
    
    # 创建玩家实例，并将索引和信息返回
    def create_player_instance(self, player_name:str):
        
        if len(self.players) < PLAYER_MAX_NUM:
            self.players.append(Player(self, player_name))
            return len(self.players) - 1, 'create player instance succeed'

        return -1, 'instance num exceed max: {}'.format(PLAYER_MAX_NUM)