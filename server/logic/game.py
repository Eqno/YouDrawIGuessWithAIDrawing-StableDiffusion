import random

from player import Player
from player import PlayerRole

from manager import Manager

from time import time
from enum import IntEnum

LOOP_LAST_TIME = 10
GAME_FAIL_TIME = 180

WHOLE_WIN_SCORE = 10
HALF_WIN_SCORE = 5

GUEST_MAX_NUM = 5


class GameMode(IntEnum):
    MATCH = 1
    CUSTOM = 2


class GameState(IntEnum):
    WAITING = 1
    PLAYING = 2
    HASENDED = 3


class Game:

    def __init__(self,
                 manager: Manager = None,
                 mode: GameMode = GameMode.MATCH):
        self.mode = mode
        self.state = GameState.WAITING

        self.host = None
        self.guests = []

        self.end_time = None
        self.loop_time = None
        self.into_loop = False

        self.round_num = None

        self.create_time = time()
        self.manager = manager

    def add_player(self, player: Player = None):

        if player is not None:
            if player.role == PlayerRole.UNSPECIFIED:

                if random.randint(0, GUEST_MAX_NUM \
                    - len(self.guests)) == 0 and self.host is None:
                    self.host = player
                    player.game = self
                    player.role = PlayerRole.HOST
                elif len(self.guests) < GUEST_MAX_NUM:
                    self.guests.append(player)
                    player.game = self
                    player.role = PlayerRole.GUEST
                else:
                    print('player num is full')

            elif player.role == PlayerRole.HOST:

                if self.host is None:
                    self.host = player
                    player.game = self
                else:
                    print('host is already occupied')

            elif len(self.guests) < GUEST_MAX_NUM:

                self.guests.append(player)

            else:
                print('guest num is full')
        else:
            print('there is no player to add')

    def get_wait_time(self):

        if self.state == GameState.WAITING:
            return time() - self.create_time
        else:
            return 0

    def begin_game(self, round_num=5):

        if self.host is None:
            print('require at least one host')
        elif len(self.guests) == 0:
            print('require at least one guest')
        else:
            self.state = GameState.PLAYING
            self.round_num = round_num
            self.goto_next_round()
        return self.state == GameState.PLAYING

    def collect_ans(self, player: Player):

        if self.state == GameState.PLAYING and self.host is not None:

            if player.ans == self.host.ans:

                if self.into_loop:
                    player.win = True
                    player.score += HALF_WIN_SCORE
                else:
                    self.into_loop = True
                    player.win = True
                    player.score += WHOLE_WIN_SCORE
                    self.loop_time = time() + LOOP_LAST_TIME

    def get_loop_time(self):

        if self.loop_time is not None:
            return self.loop_time - time()
        else:
            return None

    # 一直没人猜出来的时间
    def get_remain_time(self):

        if self.end_time is not None:
            return self.end_time - time()
        else:
            return None

    def goto_next_round(self):

        if self.round_num is None:
            print('please begin game first')
            return

        if self.round_num > 0:
            self.round_num -= 1
        else:
            self.state = GameState.HASENDED
            return

        self.host.ans = None
        for guest in self.guests:
            guest.ans = None

        self.end_time = time() + GAME_FAIL_TIME
        self.loop_time = None
        self.into_loop = False
