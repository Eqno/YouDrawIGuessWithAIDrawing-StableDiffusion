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

    def __pop(self, index: int):
        if self.is_empty():
            return None, None

        d = self._list.pop(index)
        self._keys.remove(d['key'])
        return d['key'], d['value']

    def pop(self):
        '''
        return: (key, value) or (None, None)
        '''
        return self.__pop(0)

    def pop_from_key(self, key):
        if not self.is_exist(key):
            return None, None
        target_index = -1
        for i in range(len(self._list)):
            if self._list[i]['key'] == key:
                target_index = i
                break
        if target_index == -1:
            return None, None
        return self.__pop(target_index)

    def dump(self):
        print(self._keys)
        print(self._list)


def selftest():
    q = KVqueue()
    assert q.push('a', 'a') == True
    assert q.push('a', 'a') == False
    assert q.push('b', 'b') == True
    assert q.pop() == ('a', 'a')
    assert q.push('a', 'a') == True
    assert q.pop_from_key('c') == (None, None)
    assert q.is_exist('c') == False
    assert q.push('c', 'c') == True
    assert q.is_exist('c') == True
    assert q.pop_from_key('c') == ('c', 'c')
    assert q.pop_from_key('c') == (None, None)
    assert q.pop() == ('b', 'b')
    assert q.is_empty() == False
    assert q.pop() == ('a', 'a')
    assert q.is_empty() == True
    print('selftest pass')


if __name__ == '__main__':
    selftest()
