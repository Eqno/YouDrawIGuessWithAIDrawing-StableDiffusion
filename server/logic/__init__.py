from enum import IntEnum

GAME_MAX_NUM = 20
PLAYER_MAX_NUM = 100

class PlayerRole(IntEnum):
    HOST = 1
    GUEST = 2
    UNSPECIFIED = 3

class GameMode(IntEnum):
    MATCH = 1
    CUSTOM = 2

class GameState(IntEnum):
    WAITING = 1
    PLAYING = 2
    HASENDED = 3

games = []
players = {}

def get_all_game_list():
    return games

def get_all_player_list():
    return players

# 创建游戏实例，并将索引和信息返回
def create_game_instance(game_mode: GameMode):

    if len(games) < GAME_MAX_NUM:
        games.append(Game(game_mode))
        return len(games) - 1, 'create game instance succeed'

    return -1, 'instance num exceeded max: {}'.format(GAME_MAX_NUM)

# 创建玩家实例，并将结果和信息返回
def create_player_instance(player_name: str):

    if len(players) < PLAYER_MAX_NUM:

        players[player_name] = Player(player_name)
        return True, 'create player instance succeed'

    return False, 'instance num exceed max: {}'.format(PLAYER_MAX_NUM)

def player_join_game(current_name:str, target_name:str = None, current_role:int = 3):

    current_player = players.get(current_name, None)

    if current_player is None:
        return False, 'current player not have an instance'

    if current_player.game is not None:
        return False, 'current player is already in game now'

    if len(target_name) > 0:
        
        target_player = players.get(target_name, None)
        
        if target_player is None:
            return False, 'target player not have an instance'
        
        if target_player.game is None:
            return False, 'target player is not in game yet'

        return current_player.join_game(target_player.game, current_role)

    return current_player.join_game(role=current_role)

def __get_player_in_game__(name:str):

    player = players.get(name, None)

    if player is None:
        return False, 'current player not have an instance'

    if player.game is None:
        return False, 'current player is not in game yet'

    return True, player

def player_get_others(player_name:str):

    retcode, player = __get_player_in_game__(player_name)
    if not retcode: return retcode, player

    game_state = 'unknown'

    if player.game.state == GameState.WAITING:
        game_state = 'waiting'
    elif player.game.state == GameState.PLAYING:
        game_state = 'playing'
    elif player.game.state == GameState.HASENDED:
        game_state = 'hasended'

    host = {}
    if player.game.host is not None:
        host = {
            'ready': player.game.host.ready,
            'name': player.game.host.name,
        }
    guests = []
    for guest in player.game.guests:
        guests.append({
            'ready': guest.ready,
            'name': guest.name,
        })
    
    return True, { 'game_state': game_state, 'host': host, 'guests': guests }

def player_set_ready(player_name:str, ready:bool):

    retcode, player = __get_player_in_game__(player_name)
    if not retcode: return retcode, player

    if ready is not True and ready is not False:
        return False, 'ready must be set true or false'
    return player.set_ready(ready)

from .game import Game
from .player import Player