import random, re

from . import PlayerRole
from . import GameMode
from . import GameState
from . import wordbase
from .kv_queue import KVqueue
from .stable_diffusion_binding import stable_diffusion_init

from time import time

LOOP_LAST_TIME = 10
GAME_FAIL_TIME = 180

WHOLE_WIN_SCORE = 10
HALF_WIN_SCORE = 5

GUEST_MAX_NUM = 5


task_queue = KVqueue()
img_queue = KVqueue()

# sd_thread = stable_diffusion_init(task_queue, img_queue)


class Game:

    def __init__(self, mode: GameMode = GameMode.MATCH):

        self.mode = mode
        self.state = GameState.WAITING

        self.wordset = ['咖波']
        self.image_path = None
        self.image_loaded = False

        self.ans = None
        self.start = False

        self.host = None
        self.guests = []
        self.info_record = []

        self.loop_flag = []
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
    def check_ready(self, player=None, ready:bool=False, round_num=5):

        if self.state != GameState.WAITING:
            return False, 'player could only ready when waiting'

        player.ready = ready

        if self.host and self.host.ready:
            
            guest_ready = True
            for guest in self.guests:
                if not guest.ready:
                    guest_ready = False
                    break
            
            if len(self.guests) > 0 and guest_ready:

                self.state = GameState.PLAYING

                word_set = wordbase.get_random_set()
                if word_set is not None:
                    random.shuffle(word_set)
                    self.wordset = word_set

                self.round_num = round_num
                self.goto_next_round()
        
        return True, 'player set ready succeed'

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

                    res = dict({
                        'is_alert': True,
                        'alert_prefix': '系统',
                        'players': [{
                            'name': player.name + ' (猜谜者)',
                            'ranking': player.score,
                        }],
                        'content': '回答正确'
                    })
                    self.info_record.append(res)

                    return True, 'ans is correct'
                else:
                    
                    print('correct!')

                    player.win = True
                    self.host.win = True
                    player.score += WHOLE_WIN_SCORE
                    self.loop_time = time() + LOOP_LAST_TIME

                    res = dict({
                        'is_alert': True,
                        'alert_prefix': '系统',
                        'players': [{
                            'name': player.name + ' (猜谜者)',
                            'ranking': player.score,
                        }],
                        'content': '首次回答正确'
                    })
                    self.info_record.append(res)

                    ret = dict({
                        'is_alert': True,
                        'alert_prefix': '提示',
                        'players': [],
                        'content': self.ans
                    })
                    self.info_record.append(ret)

                    res = dict({
                        'is_alert': True,
                        'alert_prefix': '系统',
                        'players': [],
                        'content': '进入倒计时'
                    })
                    self.info_record.append(res)
                    return True, 'ans is the first correct'
                
            else:
                res = dict({
                    'is_alert': False,
                    'alert_prefix': '',
                    'players': [{
                        'name': player.name + ' (猜谜者)',
                        'ranking': player.score,
                    }],
                    'content': info
                })
                self.info_record.append(res)
                return True, 'ans is incorrect'

        return False, 'collect ans failed'

    def collect_img(self, info, negative, rand_seed):
        global task_queue

        if self.state == GameState.PLAYING \
            and self.host is not None:

                if self.host.win is True:

                    for i in self.ans:
                        if re.search(i, info, re.IGNORECASE) is not None:
                            return False, 'could not contain keyword character'

                    res = dict({
                        'is_alert': False,
                        'alert_prefix': '',
                        'players': [{
                            'name': self.host.name + ' (出题者)',
                            'ranking': self.host.score,
                        }],
                        'content': info
                    })
                    self.info_record.append(res)
                    return True, 'host say something'

                if task_queue.is_exist(self.host.name):
                    return False, 'already have task in queue'

                task_queue.push(self.host.name, {
                    'username': self.host.name,
                    'positive': info,
                    'negative': negative,
                    'rand_seed': rand_seed
                })
                self.image_loaded = False
                return True, 'add task to generate image'

        return False, 'collect img failed'

    def pop_img(self, username):
        '''
        return username and filename
        '''
        global img_queue
        
        _, image_path = img_queue.pop_from_key(username)

        if image_path is not None:
            self.image_loaded = True
            self.image_path = image_path

    def get_info(self):

        if self.state == GameState.HASENDED:
            return True, 'game has ended'
        if self.state == GameState.WAITING:
            return False, 'player could only get info when playing'
        
        if self.host is not None:
            self.pop_img(self.host.name)

        return True, {
            'image_loaded': self.image_loaded,
            'image_path': self.image_path,
            'info_record': self.info_record
        }

    def game_loop(self):

        if self.host is None or self.host.escape is True:
            return False, 'host escaped'

        has_guest = False
        for guest in self.guests:
            if guest.escape is False:
                has_guest = True
                break
        if not has_guest:
            return False, 'guests escaped'

        if self.loop_time is not None:
            loop_time = self.loop_time - time()

            if loop_time < 5.5 and self.loop_flag[0] is False:
                res = dict({
                    'is_alert': True,
                    'alert_prefix': '系统',
                    'players': [],
                    'content': '倒计时 5 秒'
                })
                self.info_record.append(res)
                self.loop_flag[0] = True
            
            if loop_time < 3.5 and self.loop_flag[1] is False:
                res = dict({
                    'is_alert': True,
                    'alert_prefix': '系统',
                    'players': [],
                    'content': '倒计时 3 秒'
                })
                self.info_record.append(res)
                self.loop_flag[1] = True

            if loop_time < 2.5 and self.loop_flag[2] is False:
                res = dict({
                    'is_alert': True,
                    'alert_prefix': '系统',
                    'players': [],
                    'content': '倒计时 2 秒'
                })
                self.info_record.append(res)
                self.loop_flag[2] = True

            if loop_time < 1.5 and self.loop_flag[3] is False:
                res = dict({
                    'is_alert': True,
                    'alert_prefix': '系统',
                    'players': [],
                    'content': '倒计时 1 秒'
                })
                self.info_record.append(res)
                self.loop_flag[3] = True

            if loop_time < 0:
                return self.goto_next_round()
        return True, self.loop_time

    # 一直没人猜出来的时间
    def get_remain_time(self):

        if self.end_time is not None:
            return self.end_time - time()
        else:
            return None

    def get_from_wordset(self):

        if len(self.wordset) > 1:
            return self.wordset.pop(0)
        elif len(self.wordset) > 0:
            return self.wordset[0]
        return None

    def goto_next_round(self):

        if self.round_num is None:
            return False, 'please begin game first'

        self.loop_time = None
        self.image_path = None
        self.ans = self.get_from_wordset()

        if self.ans is None:
            return False, 'there is no more words to be answer'

        self.loop_flag = [False, False, False, False]

        self.host.win = False
        for guest in self.guests:
            guest.win = False

        if self.round_num > 0:
            self.round_num -= 1

            if self.start is False:

                res = dict({
                    'is_alert': True,
                    'alert_prefix': '系统',
                    'players': [],
                    'content': '游戏共计 5 轮'
                })
                self.info_record.append(res)

                res = dict({
                    'is_alert': True,
                    'alert_prefix': '系统',
                    'players': [],
                    'content': '开始第一轮'
                })
                self.info_record.append(res)

                self.start = True
            
            else:
                res = dict({
                    'is_alert': True,
                    'alert_prefix': '系统',
                    'players': [],
                    'content': '进入新一轮'
                })
                self.info_record.append(res)

            return True, 'next round'
        else:
            self.state = GameState.HASENDED
            return True, 'game end'