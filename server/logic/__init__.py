from enum import IntEnum
from website import backend
import time

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

def player_join_game(join_mode:str = None, current_name:str = None, target_name:str = None, current_role:int = 3):

    current_player = players.get(current_name, None)

    if current_player is None:
        return False, 'current player not have an instance'

    if current_player.game is not None:
        return False, 'current player is already in game now'

    if join_mode == 'match' and len(target_name) > 0:
        
        target_player = players.get(target_name, None)
        
        if target_player is None:
            return False, 'target player not have an instance'
        
        if target_player.game is None:
            return False, 'target player is not in game yet'

        return current_player.join_game(mode=join_mode, game=target_player.game, role=current_role)

    return current_player.join_game(mode=join_mode, role=current_role)

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

    host, guests = {}, []
    
    if game_state == 'hasended':
        if player.game.host is not None:
            host = {
                'score': player.game.host.score,
                'name': player.game.host.name,
            }
        for guest in player.game.guests:
            guests.append({
                'score': guest.score,
                'name': guest.name,
            })
    else:
        if player.game.host is not None:
            host = {
                'ready': player.game.host.ready,
                'name': player.game.host.name,
            }
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

def game_submit_info(player_name:str, info:str, negative:str, rand_seed:int):

    retcode, player = __get_player_in_game__(player_name)
    if not retcode: return retcode, player
    return player.give_info(info, negative, rand_seed)

def game_get_info(player_name:str):

    retcode, player = __get_player_in_game__(player_name)
    if not retcode: return retcode, player
    return player.get_info()

def check_escaped(escaped_users: list):

    for user in escaped_users:
        player = players.get(user, None)

        if player is not None:
            if player.game is not None:

                if player.game.state == GameState.PLAYING:
                    player.escape = True
                    player.score = -100
                    return

                if player.game.host is not None \
                    and player.game.host.name == user:
                    player.game.host = None

                guests = []
                if player.game.guests is not None:
                    for guest in player.game.guests:
                        if guest.name != user:
                            guests.append(guest)
                player.game.guests = guests

            players.pop(user)
    
    print('players: {}'.format(players))

def __game_loop__():

    need_to_pop = []
    for index, game in enumerate(games):
        if game.state == GameState.PLAYING:

            retcode, message = game.game_loop()
            if not retcode:
                print('===== GAME END =====\n' + message)
                game.state = GameState.HASENDED
            
        elif game.state == GameState.HASENDED:

            game_exsist = False
            if game.host is not None \
                and game.host.escape is False:
                game_exsist = True
            for guest in game.guests:
                if guest.escape is False:
                    game_exsist = True
                    break
            if not game_exsist:
                game.host = None
                game.guests = None
                need_to_pop.append(index)

    for i in need_to_pop:
        print('============ pop game {} ================'.format(i))
        games.pop(i)

from .game import Game
from .player import Player