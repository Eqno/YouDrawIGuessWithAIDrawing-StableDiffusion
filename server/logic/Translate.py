# YouDao.py
import hashlib
import time
import uuid
from . import consts
import pathlib
from json import loads as json_loads

import requests

YOUDAO_URL = 'https://openapi.youdao.com/api'
KEY_FILE = consts.cwd / 'server' / 'logic' / 'KeySecret.json'  # 存储key与secret的json文件路径
MAX_LENGTH = 1500  # 限制翻译输入的最大长度


def load_key_secret(key_file: str) -> tuple[str, str]:
    '''
    读取json文件中保存的API key

    :param key_file:存储key与secret的json文件
    :return:(key, secret)
    '''
    with open(key_file, 'r', encoding='utf-8') as f:
        data = json_loads(f.read())['YouDao']
        app_key = data['APP_KEY']
        app_secret = data['APP_SECRET']
        return app_key, app_secret


class YouDaoTranslator:
    '''
    调用有道翻译API实现机器翻译
    '''

    def __init__(self):
        self.q = ''  # 待翻译内容
        self._request_data = {}
        self._APP_KEY, self._APP_SECRET = load_key_secret(KEY_FILE)

    def _gen_sign(self, current_time: str, salt: str) -> str:
        '''
        生成签名

        :param current_time: 当前UTC时间戳(秒)
        :param salt: UUID
        :return: sign
        '''
        q = self.q
        q_size = len(q)
        if q_size <= 20:
            sign_input = q
        else:
            sign_input = q[0:10] + str(q_size) + q[-10:]
        sign_str = self._APP_KEY + sign_input + salt + current_time + self._APP_SECRET
        hash_algorithm = hashlib.sha256()
        hash_algorithm.update(sign_str.encode('utf-8'))
        return hash_algorithm.hexdigest()

    def _package_data(self, current_time: str, salt: str) -> None:
        '''
        设置接口调用参数

        :param current_time: 当前UTC时间戳(秒)
        :param salt: UUID
        :return: None
        '''
        request_data = self._request_data

        request_data['q'] = self.q  # 待翻译内容
        request_data['appKey'] = self._APP_KEY
        request_data['salt'] = salt
        request_data['sign'] = self._gen_sign(current_time, salt)
        request_data['signType'] = 'v3'
        request_data['curtime'] = current_time
        # _request_data['ext'] = 'mp3'  # 翻译结果音频格式
        # _request_data['voice'] = '0'  # 翻译结果发音选择，0为女声，1为男声
        request_data['strict'] = 'true'  # 是否严格按照指定from和to进行翻译
        # _request_data['vocabId'] = 'out_Id'  # 用户上传的词典，详见文档

    def _set_trs_mode(self, mode: str) -> None:
        '''
        设置翻译语言模式

        :param mode: 语言模式，en2zh或zh2en
        :return: None
        '''
        if mode == 'en2zh':
            self._request_data['from'] = 'en'
            self._request_data['to'] = 'zh-CHS'
        elif mode == 'zh2en':
            self._request_data['from'] = 'zh-CHS'
            self._request_data['to'] = 'en'
        else:
            # 处理中英互译之外的异常翻译模式
            self._request_data['from'] = 'auto'
            self._request_data['to'] = 'auto'

    def _do_request(self) -> requests.Response:
        '''
        发送请求并获取Response

        :return: Response
        '''
        current_time = str(int(time.time()))
        salt = str(uuid.uuid1())
        self._package_data(current_time, salt)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return requests.post(YOUDAO_URL, data=self._request_data, headers=headers)

    def translate(self, q: str, mode: str) -> str:
        '''
        翻译

        :param q: 待翻译文本
        :param mode: 翻译语言模式，en2zh或zh2en
        :return: 翻译结果
        '''
        if not q:
            return 'q is empty!'
        if len(q) > MAX_LENGTH:
            return 'q is too long!'

        self.q = q
        self._set_trs_mode(mode)
        response = self._do_request()
        content_type = response.headers['Content-Type']

        if content_type == 'audio/mp3':
            # 返回mp3格式的音频结果
            millis = int(round(time.time() * 1000))
            file_path = '合成的音频存储路径' + str(millis) + '.mp3'
            with open(file_path, 'wb') as fo:
                fo.write(response.content)
            trans_result = file_path
        else:
            # 返回json格式的文本结果
            error_code = json_loads(response.content)['errorCode']  # 有道API的错误码
            if error_code == '0':
                trans_result = json_loads(response.content)['translation']
            else:
                trans_result = f'ErrorCode {error_code}, check YouDao\'s API doc plz.'
        return trans_result