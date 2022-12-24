import random, re

from . import PlayerRole
from . import GameMode
from . import GameState

from time import time

LOOP_LAST_TIME = 10
GAME_FAIL_TIME = 180

WHOLE_WIN_SCORE = 10
HALF_WIN_SCORE = 5

GUEST_MAX_NUM = 5

task_queue = {}

class Game:

    def __init__(self, mode: GameMode = GameMode.MATCH):

        self.mode = mode
        self.state = GameState.WAITING

        self.ans = '咖波'

        self.host = None
        self.guests = []
        self.info_record = []

        self.end_time = None
        self.loop_time = None

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

    def collect_ans(self, player, info):

        if self.state == GameState.PLAYING \
            and player is not None \
            and self.host is not None:

            if player.win is True:
                return False, 'player has won'

            if re.search(self.ans, info, re.IGNORECASE) is not None:

                if self.loop_time is not None:
                    
                    player.win = True
                    player.score += HALF_WIN_SCORE

                    self.info_record.append({
                        'is_alert': True,
                        'alert_prefix': '系统',
                        'players': [{
                            'name': player.name + ' (猜谜者)',
                            'ranking': player.score,
                        }],
                        'content': '回答正确'
                    })

                    return True, 'ans is correct'
                else:
                    
                    player.win = True
                    self.host.win = True
                    player.score += WHOLE_WIN_SCORE
                    self.loop_time = time() + LOOP_LAST_TIME

                    self.info_record.append({
                        'is_alert': True,
                        'alert_prefix': '系统',
                        'players': [{
                            'name': player.name + ' (猜谜者)',
                            'ranking': player.score,
                        }],
                        'content': '首次回答正确'
                    })
                    self.info_record.append({
                        'is_alert': True,
                        'alert_prefix': '提示',
                        'players': [],
                        'content': self.ans
                    })
                    self.info_record.append({
                        'is_alert': True,
                        'alert_prefix': '系统',
                        'players': [],
                        'content': '进入倒计时'
                    })
                    return True, 'ans is the first correct'
                
            else:

                self.info_record.append({
                    'is_alert': False,
                    'alert_prefix': '',
                    'players': [{
                        'name': player.name + ' (猜谜者)',
                        'ranking': player.score,
                    }],
                    'content': info
                })
                return True, 'ans is incorrect'

        return False, 'collect ans failed'

    def collect_img(self, info, negative, rand_seed):

        if self.state == GameState.PLAYING \
            and self.host is not None:

                if self.host.won is True:

                    for i in self.ans:
                        if re.search(i, info, re.IGNORECASE) is not None:
                            return False, 'could not contain keyword character'

                    self.info_record.append({
                        'is_alert': False,
                        'alert_prefix': '',
                        'players': [{
                            'name': self.host.name + ' (出题者)',
                            'ranking': self.host.score,
                        }],
                        'content': info
                    })
                    return True, 'host say something'

                host_task = task_queue.get(self.host.name)
                if host_task is not None:
                    return False, 'already have task in queue'

                task_queue[self.host.name] = {
                    'positive': info,
                    'negative': negative,
                    'rand_seed': rand_seed
                }
                return True, 'add task to generate image'

        return False, 'collect img failed'

    def get_loop_time(self):

        if self.loop_time is not None:
            
            loop_time = self.loop_time - time()

            print(loop_time)

            if loop_time < 0:
                self.goto_next_round()

    # 一直没人猜出来的时间
    def get_remain_time(self):

        if self.end_time is not None:
            return self.end_time - time()
        else:
            return None

    def goto_next_round(self):

        if self.round_num is None:
            return False, 'please begin game first'

        self.loop_time = None
        self.ans = '咖波2'

        if self.host is None:
            return False, 'host escaped'
        self.host.win = False

        if len(self.guests) == 0:
            return False, 'guests escaped'
        for guest in self.guests:
            guest.win = False

        if self.round_num > 0:
            self.round_num -= 1
            return True, 'next round'
        else:
            self.state = GameState.HASENDED
            return True, 'game end'