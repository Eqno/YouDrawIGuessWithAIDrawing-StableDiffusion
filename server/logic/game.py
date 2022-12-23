import random

from . import PlayerRole
from . import GameMode
from . import GameState

from time import time

LOOP_LAST_TIME = 10
GAME_FAIL_TIME = 180

WHOLE_WIN_SCORE = 10
HALF_WIN_SCORE = 5

GUEST_MAX_NUM = 5

class Game:

    def __init__(self, mode: GameMode = GameMode.MATCH):

        self.mode = mode
        self.state = GameState.WAITING

        self.host = None
        self.guests = []

        self.end_time = None
        self.loop_time = None
        self.into_loop = False

        self.round_num = None

        self.create_time = time()

    def add_player(self, player):

        if self.state != GameState.WAITING:
            
            return False, 'game has began or ended'

        if player is not None:

            if player.role == PlayerRole.UNSPECIFIED:

                if random.randint(0, GUEST_MAX_NUM \
                    - len(self.guests)) == 0 and self.host is None:

                    self.host = player
                    player.game = self
                    player.role = PlayerRole.HOST

                    return True, 'player random as host'

                elif len(self.guests) < GUEST_MAX_NUM:

                    self.guests.append(player)
                    player.game = self
                    player.role = PlayerRole.GUEST

                    return True, 'player random as guest'

                return False, 'player num is full'

            elif player.role == PlayerRole.HOST:

                if self.host is None:

                    self.host = player
                    player.game = self

                    return True, 'player join as host'

                return False, 'host is already occupied'

            elif len(self.guests) < GUEST_MAX_NUM:

                self.guests.append(player)
                player.game = self

                return True, 'player join as guest'

            return False, 'guest num is full'

        return False, 'there is no player to add'

    def get_wait_time(self):

        if self.state == GameState.WAITING:
            return time() - self.create_time
        else:
            return 0

    # 所有人都点了准备就自动开始
    def check_ready(self, round_num=5):

        if self.host and self.host.ready:
            
            guest_ready = True
            for guest in self.guests:
                if not guest.ready:
                    guest_ready = False
                    break
            
            if len(self.guests) > 0 and guest_ready:

                self.state = GameState.PLAYING
                self.round_num = round_num
                self.goto_next_round()

                return True, 'game begin while everyone is ready'
            
        return False, 'there is someone not ready yet'

    def collect_ans(self, player):

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
