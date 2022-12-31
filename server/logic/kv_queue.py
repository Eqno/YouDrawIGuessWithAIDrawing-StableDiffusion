# -*- coding: utf-8 -*-


class KVqueue(object):
    _list = None
    _keys = None

    def __init__(self):
        self._list = list()
        self._keys = set()

    def is_empty(self) -> bool:
        return len(self._list) == 0

    def is_exist(self, key: str) -> bool:
        return key in self._keys

    def push(self, key, value) -> bool:
        if self.is_exist(key):
            return False
        self._keys.add(key)
        self._list.append({'key': key, 'value': value})
        return True

    def pop(self):
        '''
        return: (key, value) or (None, None)
        '''
        if self.is_empty():
            return (None, None)

        d = self._list.pop(0)
        self._keys.remove(d['key'])
        return (d['key'], d['value'])

    def dump(self):
        print(self._keys)
        print(self._list)
